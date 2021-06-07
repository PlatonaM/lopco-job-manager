## lopco-job-manager

Central service for the execution of LOPCO pipelines. The execution of a pipeline is done by a job. 
For this purpose, the service accesses the [machine](https://github.com/PlatonaM/lopco-machine-registry) and [pipeline](https://github.com/PlatonaM/lopco-pipeline-registry) registry as well as the [deployment manager](https://github.com/PlatonaM/lopco-deployment-manager).
Via the latter, the job manager launches the workers required for a pipeline as Docker containers. 
Jobs can be started, listed, monitored and stopped via an HTTP API.

### Configuration

`CONF_LOGGER_LEVEL`: Set logging level to `info`, `warning`, `error`, `critical` or `debug`.

`CONF_PIPELINEREGISTRY_URL`: URL of pipeline registry.

`CONF_PIPELINEREGISTRY_API`: Pipeline registry endpoint.

`CONF_DEPLOYMENTMANAGER_URL`: URL of deployment manager.

`CONF_DEPLOYMENTMANAGER_API`: Deployment manager endpoint.

`CONF_MACHINEREGISTRY_URL`: URL of machine registry.

`CONF_MACHINEREGISTRY_API`: Machine registry endpoint.

`CONF_WORKERCALLBACK_ENV_VAR`: Name of environment variable containing the worker callback URL.

`CONF_WORKERCALLBACK_URL`: Job manager URL.

`CONF_WORKERCALLBACK_API`: Worker callback endpoint.

`CONF_JOBS_MAX_NUM`: Number of parallel jobs.

`CONF_JOBS_CHECK`: Determine how often the manager checks if new jobs are available.

`CONF_DATACACHE_PATH`: Path to LOPCO data cache volume.

### Data Structures

#### Job

    {
        "ds_id": <string>,
        "init_sources": [
            {
                "init_source": <string>
            }
        ],
        "status": <string>("pending" / "running" / "finished" / "failed" / "aborted"),
        "stages": {
            "0": {
                "inputs": [
                    {
                        <string>: <string/number>,
                        ...
                    },
                    ...
                ],
                "outputs": [
                    {
                        <string>: <string/number>,
                        ...
                    },
                    ...
                ],
                "started": <string>,
                "completed": <string>,
                "log": <string>
            },
            "1": {
                ...
            },
            ...
        },
        "pipeline_id": <string>,
        "created": <string>,
        "ds_platform_id": <string>,
        "ds_platform_type_id": <string>
    }

#### New Job

    {
        "hash": <string>,
        "ds_id": <string>,
        "file_name": <string>
    }

#### Worker Output Callback

Single output:

    {
        <string>(worker container name): {
            <string>: <string/number>,
            ...
        }
    }

Multiple outputs:

    {
        <string>(worker container name): [
            {
                <string>: <string/number>,
                ...
            },
            ...
        ]
    }

### API

#### /jobs

**GET**

_List all active jobs._

    # Example

    curl http://<host>/jobs
    {
        "-Fm3IrWXyMFGAnwgt6Jyow": {
            "ds_id": "3zrj5j573kj75",
            "init_sources": [
                {
                    "init_source": "26f61003a4e94e268a18f407c768f82f"
                }
            ],
            "status": "running",
            "stages": {
                "0": {
                    "inputs": [
                        {
                            "xlsx_file": "26f61003a4e94e268a18f407c768f82f"
                        }
                    ],
                    "outputs": [
                        {
                            "csv_file": "3961c9e6fa9c4f788cdc03e1fcba90cb"
                        }
                    ],
                    "started": "2020-11-27T12:45:41.528081Z",
                    "completed": "2020-11-27T12:45:45.224914Z",
                    "log": "converting ...\n;sensor;time;gesamtwirkleistung\n1;ec-generator;2019-05-15 00:00:01;367.351867675781\n2;ec-generator;2019-05-15 00:00:06;18.6313285827637\n3;ec-generator;2019-05-15 00:00:11;1348.40270996094\n4;ec-generator;2019-05-15 00:00:16;679.065856933594\ntotal number of lines written: 93702\n"
                },
                "1": {
                    "inputs": [
                        {
                            "input_csv": "3961c9e6fa9c4f788cdc03e1fcba90cb"
                        }
                    ],
                    "outputs": [
                        {
                            "output_csv": "10c109903bdf45efb746e6a1a20367b2"
                        }
                    ],
                    "started": "2020-11-27T12:45:45.232198Z",
                    "completed": "2020-11-27T12:45:46.342370Z",
                    "log": "trimming ...\nsensor;time;gesamtwirkleistung\nec-generator;2019-05-15 00:00:01;367.351867675781\nec-generator;2019-05-15 00:00:06;18.6313285827637\nec-generator;2019-05-15 00:00:11;1348.40270996094\nec-generator;2019-05-15 00:00:16;679.065856933594\ntotal number of lines written: 93702\n"
                }
            },
            "pipeline_id": "677f99d4-2ec7-450c-add2-8b7c5f7f171c",
            "created": "2020-11-27T12:45:41.468634Z",
            "ds_platform_id": "device:aeb83bf0-c50c-48e9-91b6-4db07c65c99c",
            "ds_platform_type_id": "device-type:c5940477-afe5-493c-9a9e-8043f8de7acd"
        }
    }

**POST**

_Start a new job._

    # Example

    cat new_job_data.json
    {
        "hash": "502a515f3b0c661ae0532da64863157a4e7c2b908351a15de1e59dc6fa0327ed695a9708ebaf312a1dd70617b573af6b52f45a380ccb29a3104f85560a102477",
        "ds_id": "098z0g976gf76ftfj",
        "file_name": "51613626e8f342bb810d4ce0aaee4ca3"
    }

    curl \
    -d @new_job_data.json \
    -H 'Content-Type: application/json' \
    -X POST http://<host>/jobs

----

#### /jobs/{job}

**GET**

_Get information on a running job._

    # Example

    curl http://<host>/jobs/-Fm3IrWXyMFGAnwgt6Jyow
    {
        "ds_id": "3zrj5j573kj75",
        "init_sources": [
            {
                "init_source": "26f61003a4e94e268a18f407c768f82f"
            }
        ],
        "status": "running",
        "stages": {
            "0": {
                "inputs": [
                    {
                        "xlsx_file": "26f61003a4e94e268a18f407c768f82f"
                    }
                ],
                "outputs": [
                    {
                        "csv_file": "3961c9e6fa9c4f788cdc03e1fcba90cb"
                    }
                ],
                "started": "2020-11-27T12:45:41.528081Z",
                "completed": "2020-11-27T12:45:45.224914Z",
                "log": "converting ...\n;sensor;time;gesamtwirkleistung\n1;ec-generator;2019-05-15 00:00:01;367.351867675781\n2;ec-generator;2019-05-15 00:00:06;18.6313285827637\n3;ec-generator;2019-05-15 00:00:11;1348.40270996094\n4;ec-generator;2019-05-15 00:00:16;679.065856933594\ntotal number of lines written: 93702\n"
            },
            "1": {
                "inputs": [
                    {
                        "input_csv": "3961c9e6fa9c4f788cdc03e1fcba90cb"
                    }
                ],
                "outputs": [
                    {
                        "output_csv": "10c109903bdf45efb746e6a1a20367b2"
                    }
                ],
                "started": "2020-11-27T12:45:45.232198Z",
                "completed": "2020-11-27T12:45:46.342370Z",
                "log": "trimming ...\nsensor;time;gesamtwirkleistung\nec-generator;2019-05-15 00:00:01;367.351867675781\nec-generator;2019-05-15 00:00:06;18.6313285827637\nec-generator;2019-05-15 00:00:11;1348.40270996094\nec-generator;2019-05-15 00:00:16;679.065856933594\ntotal number of lines written: 93702\n"
            }
        },
        "pipeline_id": "677f99d4-2ec7-450c-add2-8b7c5f7f171c",
        "created": "2020-11-27T12:45:41.468634Z",
        "ds_platform_id": "device:aeb83bf0-c50c-48e9-91b6-4db07c65c99c",
        "ds_platform_type_id": "device-type:c5940477-afe5-493c-9a9e-8043f8de7acd"
    }


**POST**

_Advance running job._

    # Example

    cat job_stage_single_result.json
    {
        "9e429e84-b3f4-4f70-b3d9-e5917f629d3b": {
            "csv_file": "c92730964a5044a7b5935c2cea3e882a"
        }
    }

    curl \
    -d @job_stage_single_result.json \
    -H 'Content-Type: application/json' \
    -X POST http://<host>/jobs/UVpxMTeqgMijLlbmNI8A_A


    cat job_stage_multiple_result.json
    {
        "db5012d4-c20f-4847-bf92-f715be0c4932": [
            {
                "unique_id": "ec-generator",
                "result_table": "1b3dac542c40447a92fa556130a49a5f"
            },
            {
                "unique_id": "ec-gesamt",
                "result_table": "a6ba3b80bc9a4b508d25832b48304e9b"
            },
            {
                "unique_id": "ec-prozess",
                "result_table": "403c693c1ba643a1b4e8048a7dd28f83"
            },
            {
                "unique_id": "ec-roboter",
                "result_table": "a6f399cba34241e49bb220d5792171d9"
            },
            {
                "unique_id": "roboter-ausgabe",
                "result_table": "677af6ecff894c7a99ba319b199337b8"
            },
            {
                "unique_id": "roboter-eingabe",
                "result_table": "59d0ea3793494b42b4d442f516796f68"
            },
            {
                "unique_id": "transport-gesamt",
                "result_table": "5d5ded6eeff04b41a2762d58bba0c3bd"
            },
            {
                "unique_id": "wm1-gesamt",
                "result_table": "73266503b1e046799cbf65f65d296b10"
            },
            {
                "unique_id": "wm1-heizung-reinigen",
                "result_table": "0112f484098e425cb79d0049daf13367"
            },
            {
                "unique_id": "wm1-heizung-trocknung",
                "result_table": "279d8e31d76c4351988fa32d492c434f"
            },
            {
                "unique_id": "wm2-gesamt",
                "result_table": "08d3af1e05a14addaed048e24dd8d37c"
            },
            {
                "unique_id": "wm2-heizung-reinigen",
                "result_table": "07333b0c8f084e03be828a574a18df9c"
            },
            {
                "unique_id": "wm2-heizung-trocknung",
                "result_table": "c9f80c208262444b92feceef94a19a20"
            },
            {
                "unique_id": "wm2-vakuumpumpe",
                "result_table": "b6724d721e33464a9ec56ec52343a6f2"
            }
        ]
    }

    curl \
    -d @job_stage_multiple_result.json \
    -H 'Content-Type: application/json' \
    -X POST http://<host>/jobs/UVpxMTeqgMijLlbmNI8A_A

_Abort running job._

    # Example

    cat job_status.json
    {
        "status": "aborted"
    }

    curl \
    -d @job_status.json \
    -H 'Content-Type: application/json' \
    -X POST http://<host>/jobs/pl1E9_NMD8arJ3u5o8Pr9Q

----

#### /history

**GET**

_List all finished/failed jobs._

    # Example

    curl http://<host>/history
    {
        "-Fm3IrWXyMFGAnwgt6Jyow": {
            "ds_id": "3zrj5j573kj75",
            "init_sources": [
                {
                    "init_source": "26f61003a4e94e268a18f407c768f82f"
                }
            ],
            "status": "failed",
            "stages": {
                "0": {
                    "inputs": [
                        {
                            "xlsx_file": "26f61003a4e94e268a18f407c768f82f"
                        }
                    ],
                    "outputs": [
                        {
                            "csv_file": "3961c9e6fa9c4f788cdc03e1fcba90cb"
                        }
                    ],
                    "started": "2020-11-27T12:45:41.528081Z",
                    "completed": "2020-11-27T12:45:45.224914Z",
                    "log": "converting ...\n;sensor;time;gesamtwirkleistung\n1;ec-generator;2019-05-15 00:00:01;367.351867675781\n2;ec-generator;2019-05-15 00:00:06;18.6313285827637\n3;ec-generator;2019-05-15 00:00:11;1348.40270996094\n4;ec-generator;2019-05-15 00:00:16;679.065856933594\ntotal number of lines written: 93702\n"
                },
                "1": {
                    "inputs": [
                        {
                            "input_csv": "3961c9e6fa9c4f788cdc03e1fcba90cb"
                        }
                    ],
                    "outputs": [
                        {
                            "output_csv": "10c109903bdf45efb746e6a1a20367b2"
                        }
                    ],
                    "started": "2020-11-27T12:45:45.232198Z",
                    "completed": "2020-11-27T12:45:46.342370Z",
                    "log": "trimming ...\nsensor;time;gesamtwirkleistung\nec-generator;2019-05-15 00:00:01;367.351867675781\nec-generator;2019-05-15 00:00:06;18.6313285827637\nec-generator;2019-05-15 00:00:11;1348.40270996094\nec-generator;2019-05-15 00:00:16;679.065856933594\ntotal number of lines written: 93702\n"
                },
                "2": {
                    "inputs": [
                        {
                            "input_csv": "10c109903bdf45efb746e6a1a20367b2"
                        }
                    ],
                    "outputs": [],
                    "started": "2020-11-27T12:45:46.349388Z",
                    "completed": "2020-11-27T12:45:57.260281Z",
                    "log": "adding unix timestamps ...\nTraceback (most recent call last):\n  File \"/usr/src/worker/add_unix_time.py\", line 35, in <module>\n    line.append(\"{}\\n\".format(time.mktime(datetime.datetime.strptime(line[time_col_num], time_format).timetuple())))\n  File \"/usr/local/lib/python3.9/_strptime.py\", line 568, in _strptime_datetime\n    tt, fraction, gmtoff_fraction = _strptime(data_string, format)\n  File \"/usr/local/lib/python3.9/_strptime.py\", line 349, in _strptime\n    raise ValueError(\"time data %r does not match format %r\" %\nValueError: time data '2019-05-15 00:00:01' does not match format '%Y-%m-%d _%H:%M:%S'\nadding unix timestamps failed\n"
                }
            },
            "pipeline_id": "677f99d4-2ec7-450c-add2-8b7c5f7f171c",
            "created": "2020-11-27T12:45:41.468634Z",
            "ds_platform_id": "device:aeb83bf0-c50c-48e9-91b6-4db07c65c99c",
            "ds_platform_type_id": "device-type:c5940477-afe5-493c-9a9e-8043f8de7acd"
        },
        "qLprtwA2UWtWpsjb4BO-zg": {
            "ds_id": "678o7kujzhg",
            "init_sources": [
                {
                    "init_source": "5698574d86584dd48ed6bcb33bb358a6"
                }
            ],
            "status": "finished",
            "stages": {
                "0": {
                    "inputs": [
                        {
                            "xlsx_file": "5698574d86584dd48ed6bcb33bb358a6"
                        }
                    ],
                    "outputs": [
                        {
                            "csv_file": "ceba3cf1ec384290a44c365d91bc0668"
                        }
                    ],
                    "started": "2020-11-27T12:30:42.200403Z",
                    "completed": "2020-11-27T12:30:45.044106Z",
                    "log": "converting ...\n;sensor;time;gesamtwirkleistung\n1;ec-generator;2019-05-15 00:00:01;367.351867675781\n2;ec-generator;2019-05-15 00:00:06;18.6313285827637\n3;ec-generator;2019-05-15 00:00:11;1348.40270996094\n4;ec-generator;2019-05-15 00:00:16;679.065856933594\ntotal number of lines written: 93702\n"
                },
                "1": {
                    "inputs": [
                        {
                            "input_csv": "ceba3cf1ec384290a44c365d91bc0668"
                        }
                    ],
                    "outputs": [
                        {
                            "output_csv": "b591a098a85744d2908badac8227391b"
                        }
                    ],
                    "started": "2020-11-27T12:30:45.047297Z",
                    "completed": "2020-11-27T12:30:46.136133Z",
                    "log": "trimming ...\nsensor;time;gesamtwirkleistung\nec-generator;2019-05-15 00:00:01;367.351867675781\nec-generator;2019-05-15 00:00:06;18.6313285827637\nec-generator;2019-05-15 00:00:11;1348.40270996094\nec-generator;2019-05-15 00:00:16;679.065856933594\ntotal number of lines written: 93702\n"
                },
                "2": {
                    "inputs": [
                        {
                            "source_table": "b591a098a85744d2908badac8227391b"
                        }
                    ],
                    "outputs": [
                        {
                            "unique_id": "ec-generator",
                            "result_table": "26f54dc15016484ab4d9996148af2d64"
                        },
                        {
                            "unique_id": "ec-gesamt",
                            "result_table": "36f9c61e59744db9b7aaeef2ccf5677a"
                        },
                        {
                            "unique_id": "ec-prozess",
                            "result_table": "d5cf18eed9764b328dc7a38e438b48b0"
                        },
                        {
                            "unique_id": "ec-roboter",
                            "result_table": "32e36b949dcb4024a06d6d5a14d252c4"
                        },
                        {
                            "unique_id": "roboter-ausgabe",
                            "result_table": "8bec50d3d65d4ee3982df6f7082ac1eb"
                        },
                        {
                            "unique_id": "roboter-eingabe",
                            "result_table": "855925c88dfd49cdba954a7cdfce3111"
                        },
                        {
                            "unique_id": "transport-gesamt",
                            "result_table": "2802dd2c7d064841a996a16ba3f7cd3c"
                        },
                        {
                            "unique_id": "wm1-gesamt",
                            "result_table": "22859ea3a0ec4e8db49ab349b7cdf128"
                        },
                        {
                            "unique_id": "wm1-heizung-reinigen",
                            "result_table": "88cd3c30306c48fe920609c8d281faca"
                        },
                        {
                            "unique_id": "wm1-heizung-trocknung",
                            "result_table": "e849aa40bae54d8897e7c0851e4f645b"
                        },
                        {
                            "unique_id": "wm2-gesamt",
                            "result_table": "748bfdec30f24bac91281d06f3820b3a"
                        },
                        {
                            "unique_id": "wm2-heizung-reinigen",
                            "result_table": "891e34357e0040ceafe6a8bd454f15a9"
                        },
                        {
                            "unique_id": "wm2-heizung-trocknung",
                            "result_table": "035d3f63b48b4897be1b505390574ae1"
                        },
                        {
                            "unique_id": "wm2-vakuumpumpe",
                            "result_table": "3f1c031cb9f345f6a83bdcf645e7e5b2"
                        }
                    ],
                    "started": "2020-11-27T12:30:46.140784Z",
                    "completed": "2020-11-27T12:30:47.256151Z",
                    "log": "splitting ...\nec-generator:\ntime;gesamtwirkleistung\n2019-05-15 00:00:01;367.351867675781\n2019-05-15 00:00:06;18.6313285827637\n2019-05-15 00:00:11;1348.40270996094\n2019-05-15 00:00:16;679.065856933594\ntotal number of lines written: 6693\nec-gesamt:\ntime;gesamtwirkleistung\n2019-05-15 00:00:01;3711.43334960938\n2019-05-15 00:00:06;3371.9970703125\n2019-05-15 00:00:11;5751.4482421875\n2019-05-15 00:00:16;3723.7841796875\ntotal number of lines written: 6693\nec-prozess:\ntime;gesamtwirkleistung\n2019-05-15 00:00:01;1330.78271484375\n2019-05-15 00:00:06;1018.794921875\n2019-05-15 00:00:11;2415.5556640625\n2019-05-15 00:00:16;1455.45788574219\ntotal number of lines written: 6693\nec-roboter:\ntime;gesamtwirkleistung\n2019-05-15 00:00:01;782.694091796875\n2019-05-15 00:00:06;645.65234375\n2019-05-15 00:00:11;1603.39184570312\n2019-05-15 00:00:16;359.232849121094\ntotal number of lines written: 6693\nroboter-ausgabe:\ntime;gesamtwirkleistung\n2019-05-15 00:00:01;405.657043457031\n2019-05-15 00:00:06;608.109252929688\n2019-05-15 00:00:11;483.931091308594\n2019-05-15 00:00:16;386.716979980469\ntotal number of lines written: 6693\nroboter-eingabe:\ntime;gesamtwirkleistung\n2019-05-15 00:00:01;644.819519042969\n2019-05-15 00:00:06;304.888061523438\n2019-05-15 00:00:11;506.249938964844\n2019-05-15 00:00:16;743.453369140625\ntotal number of lines written: 6693\ntransport-gesamt:\ntime;gesamtwirkleistung\n2019-05-15 00:00:01;1608.67260742188\n2019-05-15 00:00:06;1493.09448242188\n2019-05-15 00:00:11;1495.13391113281\n2019-05-15 00:00:16;1701.51147460938\ntotal number of lines written: 6693\nwm1-gesamt:\ntime;gesamtwirkleistung\n2019-05-15 00:00:01;11025.564453125\n2019-05-15 00:00:06;11013.9013671875\n2019-05-15 00:00:11;11121.78125\n2019-05-15 00:00:16;11136.767578125\ntotal number of lines written: 6693\nwm1-heizung-reinigen:\ntime;gesamtwirkleistung\n2019-05-15 00:00:01;0\n2019-05-15 00:00:06;0\n2019-05-15 00:00:11;0\n2019-05-15 00:00:16;0\ntotal number of lines written: 6693\nwm1-heizung-trocknung:\ntime;gesamtwirkleistung\n2019-05-15 00:00:01;0\n2019-05-15 00:00:06;0\n2019-05-15 00:00:11;0\n2019-05-15 00:00:16;0\ntotal number of lines written: 6693\nwm2-gesamt:\ntime;gesamtwirkleistung\n2019-05-15 00:00:01;24821.6640625\n2019-05-15 00:00:06;23854.912109375\n2019-05-15 00:00:11;23862.84375\n2019-05-15 00:00:16;23868.978515625\ntotal number of lines written: 6693\nwm2-heizung-reinigen:\ntime;gesamtwirkleistung\n2019-05-15 00:00:01;4832.04345703125\n2019-05-15 00:00:06;4826.5986328125\n2019-05-15 00:00:11;4828.2822265625\n2019-05-15 00:00:16;4833.0869140625\ntotal number of lines written: 6693\nwm2-heizung-trocknung:\ntime;gesamtwirkleistung\n2019-05-15 00:00:01;0\n2019-05-15 00:00:06;0\n2019-05-15 00:00:11;0\n2019-05-15 00:00:16;0\ntotal number of lines written: 6693\nwm2-vakuumpumpe:\ntime;gesamtwirkleistung\n2019-05-15 00:00:01;5269.39697265625\n2019-05-15 00:00:06;5266.73583984375\n2019-05-15 00:00:11;5269.59326171875\n2019-05-15 00:00:16;5265.99169921875\ntotal number of lines written: 6693\n"
                }
            },
            "pipeline_id": "7ce0d67f-3111-452d-b0f5-802c742035ed",
            "created": "2020-11-27T12:30:42.156329Z",
            "ds_platform_id": "device:e91424f8-c0d6-4687-a6ef-6ef5e3b14746",
            "ds_platform_type_id": "device-type:82af02d3-bcab-4e8f-9a95-9d7212c0753f"
        }
    }

----

#### /history/{job}

**GET**

_Get information on a finished/failed job._

    # Example
    
    curl http://<host>/history/-Fm3IrWXyMFGAnwgt6Jyow
    {
        "ds_id": "3zrj5j573kj75",
        "init_sources": [
            {
                "init_source": "26f61003a4e94e268a18f407c768f82f"
            }
        ],
        "status": "failed",
        "stages": {
            "0": {
                "inputs": [
                    {
                        "xlsx_file": "26f61003a4e94e268a18f407c768f82f"
                    }
                ],
                "outputs": [
                    {
                        "csv_file": "3961c9e6fa9c4f788cdc03e1fcba90cb"
                    }
                ],
                "started": "2020-11-27T12:45:41.528081Z",
                "completed": "2020-11-27T12:45:45.224914Z",
                "log": "converting ...\n;sensor;time;gesamtwirkleistung\n1;ec-generator;2019-05-15 00:00:01;367.351867675781\n2;ec-generator;2019-05-15 00:00:06;18.6313285827637\n3;ec-generator;2019-05-15 00:00:11;1348.40270996094\n4;ec-generator;2019-05-15 00:00:16;679.065856933594\ntotal number of lines written: 93702\n"
            },
            "1": {
                "inputs": [
                    {
                        "input_csv": "3961c9e6fa9c4f788cdc03e1fcba90cb"
                    }
                ],
                "outputs": [
                    {
                        "output_csv": "10c109903bdf45efb746e6a1a20367b2"
                    }
                ],
                "started": "2020-11-27T12:45:45.232198Z",
                "completed": "2020-11-27T12:45:46.342370Z",
                "log": "trimming ...\nsensor;time;gesamtwirkleistung\nec-generator;2019-05-15 00:00:01;367.351867675781\nec-generator;2019-05-15 00:00:06;18.6313285827637\nec-generator;2019-05-15 00:00:11;1348.40270996094\nec-generator;2019-05-15 00:00:16;679.065856933594\ntotal number of lines written: 93702\n"
            },
            "2": {
                "inputs": [
                    {
                        "input_csv": "10c109903bdf45efb746e6a1a20367b2"
                    }
                ],
                "outputs": [],
                "started": "2020-11-27T12:45:46.349388Z",
                "completed": "2020-11-27T12:45:57.260281Z",
                "log": "adding unix timestamps ...\nTraceback (most recent call last):\n  File \"/usr/src/worker/add_unix_time.py\", line 35, in <module>\n    line.append(\"{}\\n\".format(time.mktime(datetime.datetime.strptime(line[time_col_num], time_format).timetuple())))\n  File \"/usr/local/lib/python3.9/_strptime.py\", line 568, in _strptime_datetime\n    tt, fraction, gmtoff_fraction = _strptime(data_string, format)\n  File \"/usr/local/lib/python3.9/_strptime.py\", line 349, in _strptime\n    raise ValueError(\"time data %r does not match format %r\" %\nValueError: time data '2019-05-15 00:00:01' does not match format '%Y-%m-%d _%H:%M:%S'\nadding unix timestamps failed\n"
            }
        },
        "pipeline_id": "677f99d4-2ec7-450c-add2-8b7c5f7f171c",
        "created": "2020-11-27T12:45:41.468634Z",
        "ds_platform_id": "device:aeb83bf0-c50c-48e9-91b6-4db07c65c99c",
        "ds_platform_type_id": "device-type:c5940477-afe5-493c-9a9e-8043f8de7acd"
    }
