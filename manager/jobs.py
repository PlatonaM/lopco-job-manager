"""
   Copyright 2020 InfAI (CC SES)

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

__all__ = ("Handler", "Worker")


from .logger import getLogger
from .configuration import conf
from . import model
import threading
import queue
import snorkels
import time
import json
import requests
import os
import datetime


logger = getLogger(__name__.split(".", 1)[-1])


class Abort(Exception):
    pass


class GetPipelineError(Exception):
    pass


class StageError(Exception):
    pass


class Worker(threading.Thread):
    def __init__(self, job_id: str, active_kvs: snorkels.KeyValueStore, done_kvs: snorkels.KeyValueStore):
        super().__init__(name=job_id, daemon=True)
        self.__active_kvs = active_kvs
        self.__done_kvs = done_kvs
        self.__job_data = json.loads(self.__active_kvs.get(self.name))
        self.__pipeline = None
        self.input = queue.Queue()
        self.done = False

    def __setJobStatus(self, status):
        self.__job_data[model.Job.status] = status
        self.__active_kvs.set(self.name, json.dumps(self.__job_data))

    def __getPipeline(self):
        resp = requests.get(
            "{}/{}/{}".format(conf.MachineRegistry.url, conf.MachineRegistry.api, self.__job_data[model.Job.ds_id])
        )
        if not resp.status_code == 200:
            raise GetPipelineError("could not get pipeline id - {}".format(resp.status_code))
        ds_data = resp.json()
        resp = requests.get("{}/{}/{}".format(conf.PipelineRegistry.url, conf.PipelineRegistry.api, ds_data[model.DataSource.pipeline_id]))
        if not resp.status_code == 200:
            raise GetPipelineError("could not get pipeline - {}".format(resp.status_code))
        self.__pipeline = resp.json()
        self.__job_data[model.Job.pipeline_id] = ds_data[model.DataSource.pipeline_id]
        self.__job_data[model.Job.ds_platform_id] = ds_data[model.DataSource.platform_id]
        self.__job_data[model.Job.ds_platform_type_id] = ds_data[model.DataSource.platform_type_id]
        self.__active_kvs.set(self.name, json.dumps(self.__job_data))

    def __setJobStage(self, st_num, st_data):
        self.__job_data[model.Job.stages][str(st_num)] = st_data
        self.__active_kvs.set(self.name, json.dumps(self.__job_data))

    def __cleanup(self):
        for st_num in range(0, len(self.__job_data[model.Job.stages])):
            for output in self.__job_data[model.Job.stages][str(st_num)][model.JobStage.outputs]:
                if isinstance(output, dict):
                    for file in output.values():
                        try:
                            os.remove(os.path.join(conf.DataCache.path, file))
                            logger.debug("{}: removed file '{}' from data-cache".format(self.name, file))
                        except Exception:
                            pass

    def __mapInput(self, output: dict, input_map: dict, prefix=""):
        input = dict()
        for key, value in input_map.items():
            input["{}{}".format(prefix, key)] = output[value]
        return input

    def __startWorker(self, worker: dict, inputs: dict):
        if worker[model.Worker.configs]:
            configs = worker[model.Worker.configs].copy()
        else:
            configs = dict()
        configs["DS_PLATFORM_ID"] = self.__job_data[model.Job.ds_platform_id]
        configs["DS_PLATFORM_TYPE_ID"] = self.__job_data[model.Job.ds_platform_type_id]
        worker = {
            model.WorkerRequest.id: worker[model.Worker.id],
            model.WorkerRequest.name: worker[model.Worker.name],
            model.WorkerRequest.image: worker[model.Worker.image],
            model.WorkerRequest.data_cache_path: worker[model.Worker.data_cache_path],
            model.WorkerRequest.configs: configs,
            model.WorkerRequest.inputs: inputs,
            model.WorkerRequest.type: "worker"
        }
        worker[model.Worker.configs][conf.WorkerCallback.env_var] = "{}/{}/{}".format(
            conf.WorkerCallback.url,
            conf.WorkerCallback.api,
            self.name
        )
        resp = requests.post(
            "{}/{}".format(conf.DeploymentManager.url, conf.DeploymentManager.api),
            json=worker
        )
        if not resp.status_code == 200:
            raise RuntimeError("could not start worker - '{}'".format(resp.status_code))
        return resp.text

    def __waitForWorkerResult(self, worker_instance) -> list:
        logger.debug("{}: waiting for worker '{}'".format(self.name, worker_instance))
        fail_safe = 0
        while True:
            try:
                data = self.input.get(timeout=5)
                if data.get(model.Job.status) == model.JobStatus.aborted:
                    resp = requests.delete("{}/{}/{}".format(conf.DeploymentManager.url, conf.DeploymentManager.api, worker_instance))
                    if not resp.status_code == 200:
                        logger.warning("worker '{}' could not be stopped - {}".format(worker_instance, resp.status_code))
                    raise Abort
                if worker_instance in data:
                    return data[worker_instance] if isinstance(data[worker_instance], list) else [data[worker_instance]]
            except queue.Empty:
                resp = requests.get("{}/{}/{}".format(conf.DeploymentManager.url, conf.DeploymentManager.api, worker_instance))
                if not resp.status_code == 200:
                    fail_safe += 1
                if fail_safe > 1:
                    raise RuntimeError("worker '{}' quit without results".format(worker_instance))

    def __handleWorker(self, worker_instance) -> tuple:
        logger.debug("{}: waiting for worker '{}'".format(self.name, worker_instance))
        fail_safe = 0
        output = list()
        log = str()
        abort = False
        while True:
            try:
                data = self.input.get(timeout=5)
                if data.get(model.Job.status) == model.JobStatus.aborted:
                    abort = True
                    break
                if worker_instance in data:
                    output = data[worker_instance] if isinstance(data[worker_instance], list) else [data[worker_instance]]
                    break
            except queue.Empty:
                resp = requests.get("{}/{}/{}".format(conf.DeploymentManager.url, conf.DeploymentManager.api, worker_instance))
                if resp.status_code == 200:
                    worker = resp.json()
                    if worker[model.Worker.status] == model.WorkerState.stopped:
                        fail_safe += 1
                    # else:
                    #     fail_safe = 0
                else:
                    fail_safe += 1
                if fail_safe > 1:
                    break
        if not abort:
            try:
                resp = requests.get("{}/{}/{}/log".format(conf.DeploymentManager.url, conf.DeploymentManager.api, worker_instance))
                if resp.ok:
                    log = resp.text
                else:
                    raise RuntimeError(resp.status_code)
            except Exception as ex:
                logger.warning("could not get log for worker '{}' - {}".format(worker_instance, ex))
        try:
            resp = requests.delete("{}/{}/{}".format(conf.DeploymentManager.url, conf.DeploymentManager.api, worker_instance))
            if not resp.status_code == 200:
                raise RuntimeError(resp.status_code)
        except Exception as ex:
            logger.warning("could not remove worker '{}' - {}".format(worker_instance, ex))
        if abort:
            raise Abort
        return output, log

    def run(self):
        logger.info("{}: starting ...".format(self.name))
        self.__setJobStatus(model.JobStatus.running)
        try:
            self.__getPipeline()
            for st_num in range(0, len(self.__pipeline[model.Pipeline.stages])):
                logger.info(
                    "{}: executing stage '{}' of pipeline '{}'".format(
                        self.name,
                        st_num,
                        self.__job_data[model.Job.pipeline_id]
                    )
                )
                if st_num == 0:
                    prev_outputs = self.__job_data[model.Job.init_sources]
                else:
                    prev_outputs = self.__job_data[model.Job.stages][str(st_num - 1)][model.JobStage.outputs]
                if self.__pipeline[model.Pipeline.stages][str(st_num)][model.PipelineStage.worker][model.Worker.input][model.WokerIO.type] == model.WorkerIOType.single:
                    outputs = list()
                    inputs = list()
                    logs = str()
                    no_output_ex = None
                    start_time = '{}Z'.format(datetime.datetime.utcnow().isoformat())
                    for output in prev_outputs:
                        input = self.__mapInput(output, self.__pipeline[model.Pipeline.stages][str(st_num)][model.PipelineStage.input_map])
                        worker_instance = self.__startWorker(
                            self.__pipeline[model.Pipeline.stages][str(st_num)][model.PipelineStage.worker],
                            input
                        )
                        inputs.append(input)
                        output, log = self.__handleWorker(worker_instance)
                        logs += log
                        if not output:
                            no_output_ex = RuntimeError("worker '{}' quit without results".format(worker_instance))
                            break
                        outputs += output
                    self.__setJobStage(
                        st_num,
                        {
                            model.JobStage.inputs: inputs,
                            model.JobStage.outputs: outputs,
                            model.JobStage.started: start_time,
                            model.JobStage.completed: '{}Z'.format(datetime.datetime.utcnow().isoformat()),
                            model.JobStage.log: logs
                        }
                    )
                    if no_output_ex:
                        raise no_output_ex
                elif self.__pipeline[model.Pipeline.stages][str(st_num)][model.PipelineStage.worker][model.Worker.input][model.WokerIO.type] == model.WorkerIOType.multiple:
                    prefix = 0
                    inputs = list()
                    start_time = '{}Z'.format(datetime.datetime.utcnow().isoformat())
                    for output in prev_outputs:
                        inputs.append(self.__mapInput(output, self.__pipeline[model.Pipeline.stages][str(st_num)][model.PipelineStage.input_map], "_{}_".format(prefix)))
                        prefix += 1
                    worker_instance = self.__startWorker(self.__pipeline[model.Pipeline.stages][str(st_num)][model.PipelineStage.worker], dict([item for input in inputs for item in input.items()]))
                    outputs, log = self.__handleWorker(worker_instance)
                    self.__setJobStage(
                        st_num,
                        {
                            model.JobStage.inputs: inputs,
                            model.JobStage.outputs: outputs,
                            model.JobStage.started: start_time,
                            model.JobStage.completed: '{}Z'.format(datetime.datetime.utcnow().isoformat()),
                            model.JobStage.log: log
                        }
                    )
                    if not outputs:
                        raise RuntimeError("worker '{}' quit without results".format(worker_instance))
                else:
                    raise RuntimeError(
                        "unknown worker input type '{}'".format(
                            self.__pipeline[model.Pipeline.stages][str(st_num)][model.PipelineStage.worker][model.Worker.input][model.WokerIO.type]
                        )
                    )
            logger.info("{}: finished".format(self.name))
            self.__setJobStatus(model.JobStatus.finished)
        except Abort:
            logger.info("{}: aborted".format(self.name))
            self.__setJobStatus(model.JobStatus.aborted)
        except RuntimeError as ex:
            logger.error("{}: failed - {}".format(self.name, ex))
            self.__setJobStatus(model.JobStatus.failed)
        except Exception as ex:
            logger.exception("{}: failed - {}".format(self.name, ex))
            self.__setJobStatus(model.JobStatus.failed)
        self.__done_kvs.set(self.name, json.dumps(self.__job_data))
        self.__active_kvs.delete(self.name)
        self.__cleanup()
        self.done = True


class Handler(threading.Thread):
    def __init__(self, job_queue: queue.Queue, active_kvs: snorkels.KeyValueStore, done_kvs: snorkels.KeyValueStore):
        super().__init__(name="jobs-handler", daemon=True)
        self.__job_queue = job_queue
        self.__active_kvs = active_kvs
        self.__done_kvs = done_kvs
        self.__workers = dict()

    def run(self):
        while True:
            time.sleep(conf.Jobs.check)
            if len(self.__workers) < conf.Jobs.max_num:
                job_id = self.__job_queue.get()
                worker = Worker(job_id, self.__active_kvs, self.__done_kvs)
                self.__workers[job_id] = worker
                worker.start()
            for job_id in list(self.__workers.keys()):
                if self.__workers[job_id].done:
                    del self.__workers[job_id]

    def passToWorker(self, job_id, data):
        self.__workers[job_id].input.put_nowait(data)