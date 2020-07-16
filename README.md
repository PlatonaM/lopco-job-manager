#### /jobs

**GET**

_List IDs of all active jobs._

    # Example

    curl http://host:8000/job-manager/jobs
    [
        "pl1E9_NMD8arJ3u5o8Pr9Q"
    ]

**POST**

_Start a new job._

    # Example

    cat new_job_data.json
    {
        "hash": "502a515f3b0c661ae0532da64863157a4e7c2b908351a15de1e59dc6fa0327ed695a9708ebaf312a1dd70617b573af6b52f45a380ccb29a3104f85560a102477",
        "machine_id": "735d39eb6dc94acdadc9d019ff54fb1f",
        "file_name": "d84d28ad9e43459a8364b1a1f5c4c44d"
    }

    curl \
    -d @new_job_data.json \
    -H 'Content-Type: application/json' \
    -X POST http://host:8000/job-manager/jobs

----

#### /jobs/{job}

**GET**

_Get information on a running job._

    # Example

    curl http://host:8000/job-manager/jobs/UVpxMTeqgMijLlbmNI8A_A
    {
        "machine_id": "735d39eb6dc94acdadc9d019ff54fb1f",
        "status": "running",
        "stages": [
            {
                "id": "init",
                "outputs": [
                    {
                        "init_source": "5bb6e7a9fbf14e619956f76d7bbfcf17"
                    }
                ]
            }
        ],
        "pipeline_id": "a34f4ba9-13ad-4ab5-a7e8-d23157513466",
        "created": "2020-07-16T10:15:53.278087Z"
    }

**POST**

_Advance running job._

    # Example

    cat job_stage_result.json
    {
        "b57caaac4e5b4444a4169ce784a35201": [
                {
                    "csv_file": "49423bf25a104ce0929adb519926bfcd"
                }
        ]
    }

    curl \
    -d @job_stage_result.json \
    -H 'Content-Type: application/json' \
    -X POST http://host:8000/job-manager/jobs/UVpxMTeqgMijLlbmNI8A_A


_Abort running job._

    # Example

    cat job_status.json
    {
        "status": "aborted"
    }

    curl \
    -d @job_status.json \
    -H 'Content-Type: application/json' \
    -X POST http://host:8000/job-manager/jobs/pl1E9_NMD8arJ3u5o8Pr9Q

----

#### /history

**GET**

_List IDs of all finished/failed jobs._

    # Example

    curl http://host:8000/job-manager/history
    [
        "pl1E9_NMD8arJ3u5o8Pr9Q",
        "UVpxMTeqgMijLlbmNI8A_A"
    ]

----

#### /history/{job}

**GET**

_Get information on a finished/failed job._

    # Example
    
    curl http://host:8000/job-manager/history/UVpxMTeqgMijLlbmNI8A_A
    {
        "machine_id": "735d39eb6dc94acdadc9d019ff54fb1f",
        "status": "finished",
        "stages": [
            {
                "id": "init",
                "outputs": [
                    {
                        "init_source": "5bb6e7a9fbf14e619956f76d7bbfcf17"
                    }
                ]
            },
            {
                "id": "01",
                "outputs": [
                    {
                        "csv_file": "49423bf25a104ce0929adb519926bfcd"
                    }
                ]
            },
            {
                "id": "02",
                "outputs": [
                    {
                        "output_csv": "94c17cc51749447fa19db494120b9232"
                    }
                ]
            },
            {
                "id": "03",
                "outputs": [
                    {
                        "unique_id": "ec-generator",
                        "result_table": "ed97da5995d240de980f50437499454b"
                    },
                    {
                        "unique_id": "ec-gesamt",
                        "result_table": "07b7b4ae399444849a5711a40b3b4fca"
                    },
                    {
                        "unique_id": "ec-prozess",
                        "result_table": "63cc6255701344b7915c3a292818828a"
                    },
                    {
                        "unique_id": "ec-roboter",
                        "result_table": "6f131bcf20ba4e03957fc496033d1de4"
                    },
                    {
                        "unique_id": "roboter-ausgabe",
                        "result_table": "3e2bceebdbc44ae9a2c650ed3b590683"
                    },
                    {
                        "unique_id": "roboter-eingabe",
                        "result_table": "149bc605ce424604935de9f358737aef"
                    },
                    {
                        "unique_id": "transport-gesamt",
                        "result_table": "05a03cb415c94030b7ab00a7adefcdf3"
                    },
                    {
                        "unique_id": "wm1-gesamt",
                        "result_table": "428ed34798354341949628dac45d6c45"
                    },
                    {
                        "unique_id": "wm1-heizung-reinigen",
                        "result_table": "71f781558a2445e9b2de27bc7a5553f4"
                    },
                    {
                        "unique_id": "wm1-heizung-trocknung",
                        "result_table": "8eec7a91eed144239efac6de5ffdee31"
                    },
                    {
                        "unique_id": "wm2-gesamt",
                        "result_table": "4549c53f8285461183aeeab0700557d9"
                    },
                    {
                        "unique_id": "wm2-heizung-reinigen",
                        "result_table": "51105b5531ce40ce903ccb8d230eae2e"
                    },
                    {
                        "unique_id": "wm2-heizung-trocknung",
                        "result_table": "625b95a9b8384aeeb8e15dbbcdb28405"
                    },
                    {
                        "unique_id": "wm2-vakuumpumpe",
                        "result_table": "1c5a5471fb21403e867a9aaf854efca1"
                    }
                ]
            },
            {
                "id": "04",
                "outputs": [
                    null,
                    null,
                    null,
                    null,
                    null,
                    null,
                    null,
                    null,
                    null,
                    null,
                    null,
                    null,
                    null,
                    null
                ]
            }
        ],
        "pipeline_id": "a34f4ba9-13ad-4ab5-a7e8-d23157513466",
        "created": "2020-07-16T10:15:53.278087Z"
    }
