dags = {
    "dags": [
        {
            "dag_id": "hello_world",
            "description": "Hello world example",
            "file_token": "Ii9vcHQvYWlyZmxvdy9kYWdzL3JlcG8vZGFncy9oZWxsb3dvcmxkLnB5Ig.x6F3mxeBdDLzg9-dB34gk-iOU2o",
            "fileloc": "/opt/airflow/dags/repo/dags/helloworld.py",
            "is_active": True,
            "is_paused": True,
            "is_subdag": False,
            "owners": ["airflow"],
            "root_dag_id": None,
            "schedule_interval": {
                "__type": "CronExpression",
                "value": "* * * * *",
            },
            "tags": [],
        },
        {
            "dag_id": "same_old",
            "description": "Hello world example",
            "file_token": "Ii9vcHQvYWlyZmxvdy9kYWdzL3JlcG8vZGFncy9oZWxsb3dvcmxkLnB5Ig.x6F3mxeBdDLzg9-dB34gk-iOU2o",
            "fileloc": "/opt/airflow/dags/repo/dags/sameold.py",
            "is_active": True,
            "is_paused": True,
            "is_subdag": False,
            "owners": ["airflow"],
            "root_dag_id": None,
            "schedule_interval": {
                "__type": "CronExpression",
                "value": "* * * * *",
            },
            "tags": [],
        },
    ],
    "total_entries": 2,
}

dag_runs_hello_world = {
    "dag_runs": [
        {
            "conf": {},
            "dag_id": "hello_world",
            "dag_run_id": "scheduled__2021-10-08T16:42:00+00:00",
            "end_date": "2021-10-08T16:43:16.629694+00:00",
            "execution_date": "2021-10-08T16:42:00+00:00",
            "external_trigger": False,
            "start_date": "2021-10-08T16:43:01.101863+00:00",
            "state": "success",
        },
        {
            "conf": {},
            "dag_id": "hello_world",
            "dag_run_id": "scheduled__2021-10-08T16:41:00+00:00",
            "end_date": "2021-10-08T16:42:16.189200+00:00",
            "execution_date": "2021-10-08T16:41:00+00:00",
            "external_trigger": False,
            "start_date": "2021-10-08T16:42:00.830209+00:00",
            "state": "success",
        },
    ],
    "total_entries": 2,
}

dag_runs_same_old = {
    "dag_runs": [
        {
            "conf": {},
            "dag_id": "same_old",
            "dag_run_id": "scheduled__2021-10-08T16:43:00+00:00",
            "end_date": "2021-10-08T16:42:16.189200+00:00",
            "execution_date": "2021-10-08T16:41:00+00:00",
            "external_trigger": False,
            "start_date": "2021-10-08T16:42:00.830209+00:00",
            "state": "success",
        },
    ],
    "total_entries": 1,
}
