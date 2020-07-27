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

__all__ = ("conf",)


import simple_env_var
import os


@simple_env_var.configuration
class Conf:

    @simple_env_var.section
    class PipelineRegistry:
        url = "http://pipeline-registry"
        api = "pipelines"

    @simple_env_var.section
    class DeploymentManager:
        url = "http://deployment-manager"
        api = "deployments"

    @simple_env_var.section
    class MachineRegistry:
        url = "http://machine-registry"
        api = "machines"

    @simple_env_var.section
    class WorkerCallback:
        env_var = "JOB_CALLBACK_URL"
        url = "http://job-manager"
        api = "jobs"

    @simple_env_var.section
    class Jobs:
        max_num = 2
        check = 5

    @simple_env_var.section
    class DataCache:
        path = "/data_cache"

    @simple_env_var.section
    class Logger:
        level = "info"


conf = Conf(load=False)

local_storage = "{}/data".format(os.getcwd())