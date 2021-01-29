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

__all__ = ("ActiveJobs", "ActiveJob")


from .logger import getLogger
from .jobs import Handler
from . import model
import falcon
import snorkels
import json
import base64
import hashlib
import queue
import datetime


logger = getLogger(__name__.split(".", 1)[-1])


def reqDebugLog(req):
    logger.debug("method='{}' path='{}' content_type='{}'".format(req.method, req.path, req.content_type))


def reqErrorLog(req, ex):
    logger.error("method='{}' path='{}' - {}".format(req.method, req.path, ex))


class ActiveJobs:
    def __init__(self, kvs: snorkels.KeyValueStore, job_queue: queue.Queue):
        self.__kvs = kvs
        self.__job_queue = job_queue

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response):
        reqDebugLog(req)
        try:
            # data = [key.decode() for key in self.__kvs.keys()]
            data = dict()
            for key in self.__kvs.keys():
                data[key.decode()] = json.loads(self.__kvs.get(key))
            resp.content_type = falcon.MEDIA_JSON
            resp.body = json.dumps(data)
            resp.status = falcon.HTTP_200
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)

    def on_post(self, req: falcon.request.Request, resp: falcon.response.Response):
        reqDebugLog(req)
        try:
            data = json.load(req.bounded_stream)
            job_id = base64.urlsafe_b64encode(
                hashlib.md5("{}{}".format(data[model.NewJobRequest.ds_id], data[model.NewJobRequest.hash]).encode()).digest()
            ).decode().rstrip('=')
            if job_id.encode() not in self.__kvs.keys():
                logger.info("new job '{}'".format(job_id))
                job_data = dict()
                job_data[model.Job.ds_id] = data[model.NewJobRequest.ds_id]
                job_data[model.Job.init_sources] = [{"init_source": data[model.NewJobRequest.file_name]}]
                job_data[model.Job.status] = model.JobStatus.pending
                job_data[model.Job.stages] = dict()
                job_data[model.Job.pipeline_id] = None
                job_data[model.Job.created] = '{}Z'.format(datetime.datetime.utcnow().isoformat())
                self.__kvs.set(job_id, json.dumps(job_data))
                self.__job_queue.put_nowait(job_id)
                resp.status = falcon.HTTP_200
            else:
                resp.status = falcon.HTTP_409
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)


class ActiveJob:
    def __init__(self, kvs: snorkels.KeyValueStore, jobs_handler: Handler):
        self.__kvs = kvs
        self.__jobs_handler = jobs_handler

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response, job):
        reqDebugLog(req)
        try:
            data = self.__kvs.get(job)
            resp.content_type = falcon.MEDIA_JSON
            resp.body = data.decode()
            resp.status = falcon.HTTP_200
        except snorkels.GetError as ex:
            resp.status = falcon.HTTP_404
            reqErrorLog(req, ex)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)

    def on_post(self, req: falcon.request.Request, resp: falcon.response.Response, job):
        reqDebugLog(req)
        if not req.content_type == falcon.MEDIA_JSON:
            resp.status = falcon.HTTP_415
            reqErrorLog(req, "wrong content type - '{}'".format(req.content_type))
        else:
            try:
                self.__jobs_handler.pass_to_worker(job, json.load(req.bounded_stream))
            except Exception as ex:
                resp.status = falcon.HTTP_500
                reqErrorLog(req, ex)


class JobHistory:
    def __init__(self, kvs: snorkels.KeyValueStore):
        self.__kvs = kvs

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response):
        reqDebugLog(req)
        try:
            # data = [key.decode() for key in self.__kvs.keys()]
            data = dict()
            for key in self.__kvs.keys():
                data[key.decode()] = json.loads(self.__kvs.get(key))
            resp.content_type = falcon.MEDIA_JSON
            resp.body = json.dumps(data)
            resp.status = falcon.HTTP_200
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)


class PastJob:
    def __init__(self, kvs: snorkels.KeyValueStore):
        self.__kvs = kvs

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response, job):
        reqDebugLog(req)
        try:
            data = self.__kvs.get(job)
            resp.content_type = falcon.MEDIA_JSON
            resp.body = data.decode()
            resp.status = falcon.HTTP_200
        except snorkels.GetError as ex:
            resp.status = falcon.HTTP_404
            reqErrorLog(req, ex)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)
