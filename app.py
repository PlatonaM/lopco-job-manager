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

from manager.logger import initLogger
from manager.configuration import conf, local_storage
from manager import api
from manager import jobs
import falcon
import os
import snorkels
import queue


initLogger(conf.Logger.level)

if not os.path.exists(local_storage):
    os.makedirs(local_storage)

active_ps_adapter = snorkels.ps_adapter.SQLlite3Adapter(db_name="jobs", user_path=local_storage)
active_kvs = snorkels.KeyValueStore(name="jobs", ps_adapter=active_ps_adapter)

done_ps_adapter = snorkels.ps_adapter.SQLlite3Adapter(db_name="done_jobs", user_path=local_storage)
done_kvs = snorkels.KeyValueStore(name="done_jobs", ps_adapter=done_ps_adapter)

job_queue = queue.Queue()

jobs_handler = jobs.Handler(job_queue, active_kvs, done_kvs)

app = falcon.API()

app.req_options.strip_url_path_trailing_slash = True

routes = (
    ("/jobs", api.ActiveJobs(active_kvs, job_queue)),
    ("/jobs/{job}", api.ActiveJob(active_kvs, jobs_handler)),
    ("/history", api.JobHistory(done_kvs)),
    ("/history/{job}", api.PastJob(done_kvs))
)

for route in routes:
    app.add_route(*route)

jobs_handler.start()

# gunicorn -b 0.0.0.0:8080 --workers 2 --threads 4 --worker-class gthread --log-level error app:app
