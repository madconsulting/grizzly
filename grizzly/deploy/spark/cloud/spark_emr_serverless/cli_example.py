import os
import re
import typer
import inspect
import shutil
from rich.prompt import Prompt
from rich import print as rich_print

import grizzly.iac_pulumi.aws.pulumi_projects.spark_emr_serverless


class SparkEmrServerlessCLIExample:

    def __init__(self):
        pass

    @staticmethod
    def _recommend_pulumi_get_started_tutorial():
        is_first_time = Prompt.ask(
            prompt="[bold][blue]Is this the first time you use Pulumi to deploy AWS infrastructure?",
            choices=["y", "n"],
            default="y"
        )
        if is_first_time == 'y':
            print(f"\nThen I recommend you to complete the following tutorial beforehand: "
                  f"https://www.pulumi.com/docs/get-started/aws/begin/. After completing this tutorial, you should "
                  f"have the prerequisites for this section, which are:")
            print("- A Pulumi account with access to your AWS account.")
            print("- Basic knowledge on how to create a Pulumi project and use basic pulumi commands to manage your "
                  "infrastructure programmatically.")
            Prompt.ask(
                prompt="[bold][blue]\nPlease type enter when you are ready to continue.",
            )

    @staticmethod
    def _get_environment_name() -> str:
        print("\nWe will use a single environment for this example. We will name the Pulumi Stack as the environment "
              "name.")
        stack_name = Prompt.ask(
            prompt="[bold][blue]\nPlease type the environment / stack name: ",
            default="dev"
        )
        return stack_name

    @staticmethod
    def _copy_pulumi_files(stack_name: str):
        source_dir = os.path.dirname(inspect.getfile(grizzly.iac_pulumi.aws.pulumi_projects.spark_emr_serverless))
        files_list = os.listdir(source_dir)
        # Keep only "dev" environment file name
        files_list = [file for file in files_list if
                      not((file.startswith("Pulumi.") and file.endswith(".yaml") and "dev" not in file) and file != "Pulumi.yaml") and
                      file != "__pycache__"]
        print(f"\nThe Pulumi code will be copied from the directory: {source_dir}")
        dest_dir = Prompt.ask(
            prompt="[bold][blue]\nPlease write down the target directory (should be empty or not existing yet)",
            default="example_spark_emr_serverless"
        )
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        else:
            if os.listdir(dest_dir):
                raise ValueError("Destination directory is not empty")
        new_file_list = []
        for file in files_list:
            if file == "Pulumi.dev.yaml":
                new_file = file.replace("dev", stack_name)
            else:
                new_file = file
            new_file_dir = f"{os.path.abspath(dest_dir)}/{new_file}"
            shutil.copyfile(src=f"{source_dir}/{file}", dst=new_file_dir)
            new_file_list.append(new_file)
        print(f"\nThe folowing files have been created in {dest_dir}: {new_file_list}")

    def _run_section_1(self):
        rich_print("[bold][yellow]### SECTION 1 - Deploy the infrastructure ###\n")
        print("In this section we will walk you through the steps to deploy the infrastructure as code using Pulumi.\n")
        self._recommend_pulumi_get_started_tutorial()
        stack_name = self._get_environment_name()
        self._copy_pulumi_files(stack_name=stack_name)
        # TODO - modify YAML file to fill the AWS account.

    def run_example(self):
        self._run_section_1()


