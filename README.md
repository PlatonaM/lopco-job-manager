### Data Structures

#### Job

    {
        "ds_id": <string>,
        "init_sources": [
            {
                "init_source": <string>
            },
            ...
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
                "completed": <string>
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

#### Worker Result Callback

    {
        <string>: [
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
        "MA2uh3-yxrJT0eaqR4MojQ": {
            "ds_id": "098z0g976gf76ftfj",
            "init_sources": [
                {
                    "init_source": "5c3759fed6c241db8728219cd650d9f1"
                }
            ],
            "status": "running",
            "stages": {
                "0": {
                    "inputs": [
                        {
                            "xlsx_file": "5c3759fed6c241db8728219cd650d9f1"
                        }
                    ],
                    "outputs": [
                        {
                            "csv_file": "e5d0074b058a4d6b9aa6fea6e3dcf530",
                            "line_count": 123726
                        }
                    ],
                    "started": "2020-11-20T07:42:32.783796Z",
                    "completed": "2020-11-20T07:42:36.126325Z"
                },
                "1": {
                    "inputs": [
                        {
                            "input_csv": "e5d0074b058a4d6b9aa6fea6e3dcf530"
                        }
                    ],
                    "outputs": [
                        {
                            "output_csv": "c8da879e8c6144879b26d9e0c54d7113",
                            "line_count": 123726
                        }
                    ],
                    "started": "2020-11-20T07:42:36.132284Z",
                    "completed": "2020-11-20T07:42:37.071775Z"
                }
            },
            "pipeline_id": "677f99d4-2ec7-450c-add2-8b7c5f7f171c",
            "created": "2020-11-20T07:42:32.731518Z",
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

    curl http://<host>/jobs/MA2uh3-yxrJT0eaqR4MojQ
    {
        "ds_id": "098z0g976gf76ftfj",
        "init_sources": [
            {
                "init_source": "5c3759fed6c241db8728219cd650d9f1"
            }
        ],
        "status": "running",
        "stages": {
            "0": {
                "inputs": [
                    {
                        "xlsx_file": "5c3759fed6c241db8728219cd650d9f1"
                    }
                ],
                "outputs": [
                    {
                        "csv_file": "e5d0074b058a4d6b9aa6fea6e3dcf530",
                        "line_count": 123726
                    }
                ],
                "started": "2020-11-20T07:42:32.783796Z",
                "completed": "2020-11-20T07:42:36.126325Z"
            },
            "1": {
                "inputs": [
                    {
                        "input_csv": "e5d0074b058a4d6b9aa6fea6e3dcf530"
                    }
                ],
                "outputs": [
                    {
                        "output_csv": "c8da879e8c6144879b26d9e0c54d7113",
                        "line_count": 123726
                    }
                ],
                "started": "2020-11-20T07:42:36.132284Z",
                "completed": "2020-11-20T07:42:37.071775Z"
            }
        },
        "pipeline_id": "677f99d4-2ec7-450c-add2-8b7c5f7f171c",
        "created": "2020-11-20T07:42:32.731518Z",
        "ds_platform_id": "device:aeb83bf0-c50c-48e9-91b6-4db07c65c99c",
        "ds_platform_type_id": "device-type:c5940477-afe5-493c-9a9e-8043f8de7acd"
    }


**POST**

_Advance running job._

    # Example

    cat job_stage_single_result.json
    {
        "9e429e84-b3f4-4f70-b3d9-e5917f629d3b": [
            {
                "csv_file": "c92730964a5044a7b5935c2cea3e882a",
                "line_count": 93702
            }
        ]
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
                "result_table": "1b3dac542c40447a92fa556130a49a5f",
                "line_count": "6693"
            },
            {
                "unique_id": "ec-gesamt",
                "result_table": "a6ba3b80bc9a4b508d25832b48304e9b",
                "line_count": "6693"
            },
            {
                "unique_id": "ec-prozess",
                "result_table": "403c693c1ba643a1b4e8048a7dd28f83",
                "line_count": "6693"
            },
            {
                "unique_id": "ec-roboter",
                "result_table": "a6f399cba34241e49bb220d5792171d9",
                "line_count": "6693"
            },
            {
                "unique_id": "roboter-ausgabe",
                "result_table": "677af6ecff894c7a99ba319b199337b8",
                "line_count": "6693"
            },
            {
                "unique_id": "roboter-eingabe",
                "result_table": "59d0ea3793494b42b4d442f516796f68",
                "line_count": "6693"
            },
            {
                "unique_id": "transport-gesamt",
                "result_table": "5d5ded6eeff04b41a2762d58bba0c3bd",
                "line_count": "6693"
            },
            {
                "unique_id": "wm1-gesamt",
                "result_table": "73266503b1e046799cbf65f65d296b10",
                "line_count": "6693"
            },
            {
                "unique_id": "wm1-heizung-reinigen",
                "result_table": "0112f484098e425cb79d0049daf13367",
                "line_count": "6693"
            },
            {
                "unique_id": "wm1-heizung-trocknung",
                "result_table": "279d8e31d76c4351988fa32d492c434f",
                "line_count": "6693"
            },
            {
                "unique_id": "wm2-gesamt",
                "result_table": "08d3af1e05a14addaed048e24dd8d37c",
                "line_count": "6693"
            },
            {
                "unique_id": "wm2-heizung-reinigen",
                "result_table": "07333b0c8f084e03be828a574a18df9c",
                "line_count": "6693"
            },
            {
                "unique_id": "wm2-heizung-trocknung",
                "result_table": "c9f80c208262444b92feceef94a19a20",
                "line_count": "6693"
            },
            {
                "unique_id": "wm2-vakuumpumpe",
                "result_table": "b6724d721e33464a9ec56ec52343a6f2",
                "line_count": "6693"
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
        "0d-bTcQEwCwG_zcdBDuIGA": {
            "ds_id": "098z0g976gf76ftfj",
            "init_sources": [
                {
                    "init_source": "f3de23ed476d4a5b903ca108f1926ffd"
                }
            ],
            "status": "finished",
            "stages": {
                "0": {
                    "inputs": [
                        {
                            "xlsx_file": "f3de23ed476d4a5b903ca108f1926ffd"
                        }
                    ],
                    "outputs": [
                        {
                            "csv_file": "30577f02656d412e83f101b4a40bb1a4",
                            "line_count": 93702
                        }
                    ],
                    "started": "2020-11-20T07:38:29.322173Z",
                    "completed": "2020-11-20T07:38:31.885463Z"
                },
                "1": {
                    "inputs": [
                        {
                            "input_csv": "30577f02656d412e83f101b4a40bb1a4"
                        }
                    ],
                    "outputs": [
                        {
                            "output_csv": "e97d5d50bb994b018ba61a81d3a9ef5c",
                            "line_count": 93702
                        }
                    ],
                    "started": "2020-11-20T07:38:31.891534Z",
                    "completed": "2020-11-20T07:38:32.584822Z"
                },
                "2": {
                    "inputs": [
                        {
                            "source_table": "e97d5d50bb994b018ba61a81d3a9ef5c"
                        }
                    ],
                    "outputs": [
                        {
                            "unique_id": "ec-generator",
                            "result_table": "7e30f19413e8418caf63cde07b1166a9",
                            "line_count": "6693"
                        },
                        {
                            "unique_id": "ec-gesamt",
                            "result_table": "f29ef98d857e4f5685515ec02fb22805",
                            "line_count": "6693"
                        },
                        {
                            "unique_id": "ec-prozess",
                            "result_table": "c213efb9ee984f98b1dad95329a2a158",
                            "line_count": "6693"
                        },
                        {
                            "unique_id": "ec-roboter",
                            "result_table": "a8d07ed23be7473a8dda15b086b4ce4a",
                            "line_count": "6693"
                        },
                        {
                            "unique_id": "roboter-ausgabe",
                            "result_table": "d31e7b790e8a4ae4a3f3ceb49f30d3ed",
                            "line_count": "6693"
                        },
                        {
                            "unique_id": "roboter-eingabe",
                            "result_table": "7d699ae2b61b4d44a7c9c0389effcc27",
                            "line_count": "6693"
                        },
                        {
                            "unique_id": "transport-gesamt",
                            "result_table": "1fafc980725b4aee807a99c9bacd5a54",
                            "line_count": "6693"
                        },
                        {
                            "unique_id": "wm1-gesamt",
                            "result_table": "9a1cca2b68e04952a0178a8af43935fb",
                            "line_count": "6693"
                        },
                        {
                            "unique_id": "wm1-heizung-reinigen",
                            "result_table": "1afdd8a708be4a55901b670aaccc5bea",
                            "line_count": "6693"
                        },
                        {
                            "unique_id": "wm1-heizung-trocknung",
                            "result_table": "d92f6b3d6b4748d48d8998f10cb040ab",
                            "line_count": "6693"
                        },
                        {
                            "unique_id": "wm2-gesamt",
                            "result_table": "a78c3d7410a242be978573113504ce8f",
                            "line_count": "6693"
                        },
                        {
                            "unique_id": "wm2-heizung-reinigen",
                            "result_table": "671624bab6cf4e60b632417cc444c524",
                            "line_count": "6693"
                        },
                        {
                            "unique_id": "wm2-heizung-trocknung",
                            "result_table": "05dc8da358c04348bf9dbd6175228e51",
                            "line_count": "6693"
                        },
                        {
                            "unique_id": "wm2-vakuumpumpe",
                            "result_table": "9ed205ec098046f998621e06040a25f3",
                            "line_count": "6693"
                        }
                    ],
                    "started": "2020-11-20T07:38:32.592868Z",
                    "completed": "2020-11-20T07:38:33.420202Z"
                }
            },
            "pipeline_id": "677f99d4-2ec7-450c-add2-8b7c5f7f171c",
            "created": "2020-11-20T07:38:29.280343Z",
            "ds_platform_id": "device:aeb83bf0-c50c-48e9-91b6-4db07c65c99c",
            "ds_platform_type_id": "device-type:c5940477-afe5-493c-9a9e-8043f8de7acd"
        },
        "MA2uh3-yxrJT0eaqR4MojQ": {
            "ds_id": "098z0g976gf76ftfj",
            "init_sources": [
                {
                    "init_source": "065e11c04134490480c65f05d118b5f9"
                }
            ],
            "status": "aborted",
            "stages": {
                "0": {
                    "inputs": [
                        {
                            "xlsx_file": "065e11c04134490480c65f05d118b5f9"
                        }
                    ],
                    "outputs": [
                        {
                            "csv_file": "06d30aae9ecc49f7be1cb47b5be279f0",
                            "line_count": 123726
                        }
                    ],
                    "started": "2020-11-20T07:58:40.385870Z",
                    "completed": "2020-11-20T07:58:44.789344Z"
                }
            },
            "pipeline_id": "677f99d4-2ec7-450c-add2-8b7c5f7f171c",
            "created": "2020-11-20T07:58:40.236727Z",
            "ds_platform_id": "device:aeb83bf0-c50c-48e9-91b6-4db07c65c99c",
            "ds_platform_type_id": "device-type:c5940477-afe5-493c-9a9e-8043f8de7acd"
        }
    }

----

#### /history/{job}

**GET**

_Get information on a finished/failed job._

    # Example
    
    curl http://<host>/history/MA2uh3-yxrJT0eaqR4MojQ
    {
        "ds_id": "098z0g976gf76ftfj",
        "init_sources": [
            {
                "init_source": "5c3759fed6c241db8728219cd650d9f1"
            }
        ],
        "status": "finished",
        "stages": {
            "0": {
                "inputs": [
                    {
                        "xlsx_file": "5c3759fed6c241db8728219cd650d9f1"
                    }
                ],
                "outputs": [
                    {
                        "csv_file": "e5d0074b058a4d6b9aa6fea6e3dcf530",
                        "line_count": 123726
                    }
                ],
                "started": "2020-11-20T07:42:32.783796Z",
                "completed": "2020-11-20T07:42:36.126325Z"
            },
            "1": {
                "inputs": [
                    {
                        "input_csv": "e5d0074b058a4d6b9aa6fea6e3dcf530"
                    }
                ],
                "outputs": [
                    {
                        "output_csv": "c8da879e8c6144879b26d9e0c54d7113",
                        "line_count": 123726
                    }
                ],
                "started": "2020-11-20T07:42:36.132284Z",
                "completed": "2020-11-20T07:42:37.071775Z"
            },
            "2": {
                "inputs": [
                    {
                        "source_table": "c8da879e8c6144879b26d9e0c54d7113"
                    }
                ],
                "outputs": [
                    {
                        "unique_id": "ec-generator",
                        "result_table": "34e63c28f95b48b9b5d1e4677b5b6119",
                        "line_count": "29294"
                    },
                    {
                        "unique_id": "ec-gesamt",
                        "result_table": "eda3ba7caa184a8cb61a4cd8c9546256",
                        "line_count": "31981"
                    },
                    {
                        "unique_id": "ec-prozess",
                        "result_table": "25a7de771fcc464e868079684ca3cb5e",
                        "line_count": "31422"
                    },
                    {
                        "unique_id": "ec-roboter",
                        "result_table": "ca4ab8cb31e444039b7686ba2d9766d3",
                        "line_count": "31029"
                    }
                ],
                "started": "2020-11-20T07:42:37.078960Z",
                "completed": "2020-11-20T07:42:38.503447Z"
            }
        },
        "pipeline_id": "677f99d4-2ec7-450c-add2-8b7c5f7f171c",
        "created": "2020-11-20T07:42:32.731518Z",
        "ds_platform_id": "device:aeb83bf0-c50c-48e9-91b6-4db07c65c99c",
        "ds_platform_type_id": "device-type:c5940477-afe5-493c-9a9e-8043f8de7acd"
    }
