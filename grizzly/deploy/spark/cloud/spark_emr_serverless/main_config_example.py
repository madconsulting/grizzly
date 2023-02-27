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
    "pulumi_organization": "victor-vila",
    "pulumi_project": "spark_emr_serverless",
    "pulumi_stack": "dev",
    # Deployment variables
    "python_version": "3.9.12",
    "poetry_version": "1.2.0b3",
}
