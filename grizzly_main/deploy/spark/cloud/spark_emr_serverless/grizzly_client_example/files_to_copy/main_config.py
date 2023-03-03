main_config = {
    # Run specific variables
    "spark_resources_dict": {
        "driver": {"num_cores": 1, "memory_in_GB": 2, "disk_in_GB": 20,},
        "executor": {
            "num_cores": 1,
            "instances": 2,
            "memory_in_GB": 2,
            "disk_in_GB": 20,
        },
    },
    "pulumi_organization": "",  # TODO - Automatically filled in the CLI example
    "pulumi_project": "spark_emr_serverless",
    "pulumi_stack": "",  # TODO - Automatically filled in the CLI example
    # Deployment variables
    "python_version": "",  # TODO - Automatically filled in the CLI example
    "poetry_version": "",  # TODO - Automatically filled in the CLI example
    "poetry_dir": "",  # Empty directory by default (poetry files in root directory of client repository)
}
