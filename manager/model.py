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

__all__ = ("Job", "JobStatus", "JobStage", "NewJobRequest", "Pipeline", "Machine", "PipelineStage")


class NewJobRequest:
    machine_id = "machine_id"
    hash = "hash"
    file_name = "file_name"


class Machine:
    name = "name"
    pipeline_id = "pipeline_id"
    type_id = "type_id"


class Job:
    machine_id = "machine_id"
    status = "status"
    stages = "stages"
    pipeline_id = "pipeline_id"
    created = "created"
    init_sources = "init_sources"


class JobStage:
    inputs = "inputs"
    outputs = "outputs"


class JobStatus:
    pending = "pending"
    running = "running"
    finished = "finished"
    failed = "failed"
    aborted = "aborted"


class Pipeline:
    name = "name"
    stages = "stages"


class PipelineStage:
    id = "id"
    worker = "worker"
    input_map = "input_map"


class Worker:
    id = "id"
    name = "name"
    description = "description"
    image = "image"
    data_cache_path = "data_cache_path"
    input = "input"
    output = "output"
    configs = "configs"


class WokerIO:
    type = "type"
    fields = "fields"
    prefix = "prefix"


class WorkerIOType:
    single = "single"
    multiple = "multiple"


class WokerIOField:
    name = "name"
    media_type = "media_type"
    is_file = "is_file"


class WorkerRequest:
    id = "id"
    name = "name"
    image = "image"
    data_cache_path = "data_cache_path"
    inputs = "inputs"
    configs = "configs"
    type = "type"
