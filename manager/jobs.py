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
        self.__stage_outputs = dict()
        self.input = queue.Queue()
        self.done = False

    def __set_job_status(self, status):
        self.__job_data[model.Job.status] = status
        self.__active_kvs.set(self.name, json.dumps(self.__job_data))

    def __get_pipeline(self):
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

    def __set_job_stage(self, st_num, st_data):
        self.__job_data[model.Job.stages][str(st_num)] = st_data
        self.__active_kvs.set(self.name, json.dumps(self.__job_data))

    def __cleanup(self):
        for st_outputs in self.__stage_outputs.values():
            for output in st_outputs:
                try:
                    for file in output.values():
                        try:
                            os.remove(os.path.join(conf.DataCache.path, file))
                            logger.debug("{}: removed file '{}' from data-cache".format(self.name, file))
                        except Exception:
                            pass
                except Exception:
                    pass

    def __map_input(self, output: dict, input_map: dict, prefix=""):
        input = dict()
        for key, value in input_map.items():
            input["{}{}".format(prefix, key)] = output[value]
        return input

    def __gen_inputs(self, input_map: dict, multi_input: bool):
        stage_input_map = dict()
        for _input_field, _input_source in input_map.items():
            source_stage, source_field = _input_source.split(":")
            if source_stage not in stage_input_map:
                stage_input_map[source_stage] = dict()
            stage_input_map[source_stage][_input_field] = source_field
        multi_output_stage = None
        for _stage in stage_input_map.keys():
            if len(self.__stage_outputs[_stage]) > 1:
                if multi_output_stage:
                    raise RuntimeError("too many outputs to combine")
                multi_output_stage = _stage
        inputs = list()
        if multi_output_stage:
            for x in range(len(self.__stage_outputs[multi_output_stage])):
                inputs.append(
                    self.__map_input(
                        self.__stage_outputs[multi_output_stage][x],
                        stage_input_map[multi_output_stage],
                        "_{}_".format(x) if multi_input else ""
                    )
                )
            for x in range(len(inputs)):
                for _stage, _input_map in stage_input_map.items():
                    if _stage != multi_output_stage:
                        inputs[x].update(
                            self.__map_input(
                                self.__stage_outputs[_stage][0],
                                _input_map,
                                "_{}_".format(x) if multi_input else "")
                        )
        else:
            _input = dict()
            for _stage, _input_map in stage_input_map.items():
                for x in range(len(self.__stage_outputs[_stage])):
                    _input.update(
                        self.__map_input(
                            self.__stage_outputs[_stage][x],
                            _input_map,
                            "_{}_".format(x) if multi_input else ""
                        )
                    )
            inputs.append(_input)
        return inputs

    def __start_worker(self, worker: dict, inputs: dict):
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

    def __handle_worker(self, worker_instance) -> tuple:
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
        try:
            self.__set_job_status(model.JobStatus.running)
            self.__get_pipeline()
            self.__stage_outputs[str(0)] = self.__job_data[model.Job.init_sources]
            for st_num in range(1, len(self.__pipeline[model.Pipeline.stages]) + 1):
                logger.info(
                    "{}: executing stage '{}' of pipeline '{}'".format(
                        self.name,
                        st_num,
                        self.__job_data[model.Job.pipeline_id]
                    )
                )
                if self.__pipeline[model.Pipeline.stages][str(st_num)][model.PipelineStage.worker][model.Worker.input][model.WokerIO.type] == model.WorkerIOType.single:
                    outputs = list()
                    inputs = self.__gen_inputs(
                        self.__pipeline[model.Pipeline.stages][str(st_num)][model.PipelineStage.input_map],
                        False
                    )
                    logs = str()
                    no_output_ex = None
                    start_time = '{}Z'.format(datetime.datetime.utcnow().isoformat())
                    for input in inputs:
                        worker_instance = self.__start_worker(
                            self.__pipeline[model.Pipeline.stages][str(st_num)][model.PipelineStage.worker],
                            input
                        )
                        output, log = self.__handle_worker(worker_instance)
                        logs += log
                        if not output:
                            no_output_ex = RuntimeError("worker '{}' quit without results".format(worker_instance))
                            break
                        outputs += output
                    self.__set_job_stage(
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
                    self.__stage_outputs[str(st_num)] = outputs
                elif self.__pipeline[model.Pipeline.stages][str(st_num)][model.PipelineStage.worker][model.Worker.input][model.WokerIO.type] == model.WorkerIOType.multiple:
                    inputs = self.__gen_inputs(
                        self.__pipeline[model.Pipeline.stages][str(st_num)][model.PipelineStage.input_map],
                        True
                    )
                    start_time = '{}Z'.format(datetime.datetime.utcnow().isoformat())
                    worker_instance = self.__start_worker(self.__pipeline[model.Pipeline.stages][str(st_num)][model.PipelineStage.worker], dict([item for input in inputs for item in input.items()]))
                    outputs, log = self.__handle_worker(worker_instance)
                    self.__set_job_stage(
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
                    self.__stage_outputs[str(st_num)] = outputs
                else:
                    raise RuntimeError(
                        "unknown worker input type '{}'".format(
                            self.__pipeline[model.Pipeline.stages][str(st_num)][model.PipelineStage.worker][model.Worker.input][model.WokerIO.type]
                        )
                    )
            logger.info("{}: finished".format(self.name))
            self.__set_job_status(model.JobStatus.finished)
        except Abort:
            logger.info("{}: aborted".format(self.name))
            self.__set_job_status(model.JobStatus.aborted)
        except RuntimeError as ex:
            logger.error("{}: failed - {}".format(self.name, ex))
            self.__set_job_status(model.JobStatus.failed)
        except Exception as ex:
            logger.exception("{}: failed - {}".format(self.name, ex))
            self.__set_job_status(model.JobStatus.failed)
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

    def pass_to_worker(self, job_id, data):
        self.__workers[job_id].input.put_nowait(data)
