main_config = {
    # Run specific variables
    "spark_resources_dict": {
        "driver": {
            "num_cores": 1,
            "memory_in_GB": 2,
            "disk_in_GB": 20,
        },
        "executor": {
            "num_cores": 1,
            "instances": 2,
            "memory_in_GB": 2,
            "disk_in_GB": 20,
        },
    },
    "repository_name": "",  # Automatically filled in the CLI example
    "pulumi_organization": "",  # Automatically filled in the CLI example
    "pulumi_project": "",  # Automatically filled in the CLI example
    "pulumi_stack": "",  # Automatically filled in the CLI example
    # Deployment variables
    "python_version": "",  # Automatically filled in the CLI example
    "poetry_version": "",  # Automatically filled in the CLI example
    "poetry_dir": "",  # Empty directory by default (poetry files in root directory of client repository)
}
