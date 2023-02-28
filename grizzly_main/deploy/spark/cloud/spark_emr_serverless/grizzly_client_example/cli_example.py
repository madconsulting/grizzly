import os
import sys
import shutil
import inspect
import subprocess
import ruamel.yaml
from rich.prompt import Prompt
from rich import print as rich_print

from grizzly_main.path_interations import cd
import grizzly_main.iac_pulumi.aws.pulumi_projects.spark_emr_serverless
from grizzly_main.iac_pulumi.aws.reusable_architectures.spark_emr_serverless import (
    create_spark_emr_serverless_architecture,
)


class SparkEmrServerlessCLIExample:
    def __init__(self):
        pass

    @staticmethod
    def _ask_user_confirmation_to_execute_pulumi_command(
        pulumi_project_dir: str, pulumi_command: str
    ):
        is_execute_command = Prompt.ask(
            prompt="[bold blue]\nWould you like me to execute the command above in this terminal?",
            choices=["y", "n"],
            default="y",
        )
        if is_execute_command == "y":
            with cd(pulumi_project_dir):
                res = subprocess.run(
                    pulumi_command.split(),
                    # capture_output=True,
                    # text=True,
                    stderr=subprocess.PIPE,
                )
                if res.returncode != 0:
                    rich_print(
                        f"[bold red] The following error occurred with:"
                        f"\n- returncode {res.returncode}"
                        f"\n- stderr: {res.stderr.decode('utf-8')}"
                    )
                    print(
                        "Please start again the example addressing the Pulumi error above."
                    )
                    sys.exit()
                else:
                    print("Pulumi command executed successfully")
        else:
            Prompt.ask(
                prompt="[bold blue]\nPlease execute the command above in another terminal. "
                "Afterwards, type enter when you are ready to continue",
            )

    @staticmethod
    def _recommend_pulumi_get_started_tutorial() -> None:
        is_first_time = Prompt.ask(
            prompt="[bold blue]Is this the first time you use Pulumi to deploy AWS infrastructure?",
            choices=["y", "n"],
            default="y",
        )
        if is_first_time == "y":
            print(
                f"\nThen I recommend you to complete the following tutorial beforehand: "
                f"https://www.pulumi.com/docs/get-started/aws/begin/. After completing this tutorial, you should "
                f"have the prerequisites for this section, which are:"
            )
            print("- A Pulumi account with access to your AWS account.")
            print(
                "- Basic knowledge on how to create a Pulumi project and use basic pulumi commands to manage your "
                "infrastructure programmatically."
            )
            Prompt.ask(
                prompt="[bold blue]\nPlease type enter when you are ready to continue",
            )

    @staticmethod
    def _get_environment_name() -> str:
        print(
            "\nWe will use a single environment for this example. We will name the Pulumi Stack as the environment "
            "name."
        )
        stack_name = Prompt.ask(
            prompt="[bold blue]\nPlease type the environment / stack name",
            default="dev",
        )
        return stack_name

    @staticmethod
    def _copy_pulumi_files(stack_name: str) -> str:
        source_dir = os.path.dirname(
            inspect.getfile(
                grizzly_main.iac_pulumi.aws.pulumi_projects.spark_emr_serverless
            )
        )
        files_list = os.listdir(source_dir)
        # Keep only "dev" environment file name
        files_list = [
            file
            for file in files_list
            if not (
                (
                    file.startswith("Pulumi.")
                    and file.endswith(".yaml")
                    and "dev" not in file
                )
                and file != "Pulumi.yaml"
            )
            and file != "__pycache__"
        ]
        print(f"\nThe Pulumi code will be copied from the directory: {source_dir}")
        pulumi_project_dir = Prompt.ask(
            prompt="[bold blue]\nPlease write down the target directory (should be empty or not existing yet)",
            default="example_spark_emr_serverless",
        )
        if not os.path.exists(pulumi_project_dir):
            os.makedirs(pulumi_project_dir)
        else:
            if os.listdir(pulumi_project_dir):
                raise ValueError("Destination directory is not empty")
        new_file_list = []
        for file in files_list:
            if file == "Pulumi.dev.yaml":
                new_file = file.replace("dev", stack_name)
            else:
                new_file = file
            new_file_dir = f"{os.path.abspath(pulumi_project_dir)}/{new_file}"
            shutil.copyfile(src=f"{source_dir}/{file}", dst=new_file_dir)
            new_file_list.append(new_file)
        print(
            f"\nThe folowing files have been created in {pulumi_project_dir}: {new_file_list}"
        )
        return pulumi_project_dir

    @staticmethod
    def _update_aws_account_id(pulumi_project_dir: str, stack_name: str) -> None:
        stack_config_file = f"{pulumi_project_dir}/Pulumi.{stack_name}.yaml"
        print(
            f"\nIn the stack configuration file ({stack_config_file}), there is the aws_account_id pending to be "
            f"filled. This account requires programmatic access with rights to deploy and manage resources handled "
            f"through Pulumi, as described in: "
            f"https://www.pulumi.com/docs/get-started/aws/begin/#configure-pulumi-to-access-your-aws-account"
        )
        aws_account_id = Prompt.ask(
            prompt="[bold blue]\nPlease type your AWS account id",
        )
        data = ruamel.yaml.YAML().load(open(stack_config_file, "r"))
        data["config"]["spark_emr_serverless:aws_account_id"] = aws_account_id
        yaml = ruamel.yaml.YAML()
        with open(stack_config_file, "w") as fp:
            yaml.dump(data, fp)
        print(
            f"\nThe AWS account has been updated in {stack_config_file}. The file content is printed below:\n"
        )
        print(yaml.dump(data, sys.stdout))
        print(
            "\nFeel free to modify the other configuration parameters, such as the maximum computational resources "
            "for the Spark workers, but this is not required to run this example."
        )
        more_info = Prompt.ask(
            prompt="[bold blue]\nWould you like more information about the configuration parameters?",
            choices=["y", "n"],
            default="y",
        )
        if more_info == "y":
            print(
                "\nYou can find the explanation of the parameters in the docstrings of the "
                f"'create_spark_emr_serverless_architecture' function used in {pulumi_project_dir}/__main__.py "
            )
            print("print(create_spark_emr_serverless_architecture.__doc__)\n")
            print(create_spark_emr_serverless_architecture.__doc__)

    def _create_pulumi_stack(self, pulumi_project_dir: str, stack_name: str) -> None:
        print(
            "\nNow we are going to create a new stack (or select it, if already exists) using the following command:"
        )
        rich_print("\n[bold italic]pulumi stack select <org-name>/<stack> --create")
        print(
            "\nNote that <org-name> can be either the Pulumi organization where the stack will be created, or your "
            "\nPulumi individual Account ID if you don't belong to an organization."
            "\nFor more info about this command, read: https://www.pulumi.com/docs/reference/cli/pulumi_stack_select/"
        )
        org_name = Prompt.ask(prompt="[bold blue]\nPlease type the target <org-name>",)
        pulumi_command = f"pulumi stack select {org_name}/{stack_name} --create"
        rich_print(f"\nPulumi command: [bold italic]{pulumi_command}")
        self._ask_user_confirmation_to_execute_pulumi_command(
            pulumi_project_dir=pulumi_project_dir, pulumi_command=pulumi_command
        )

    def _deploy_infrastructure(self, pulumi_project_dir: str) -> None:
        pulumi_command = "pulumi up"
        print(
            "\nNow we are going to create a new stack (or select it, if already exists) using the following command:"
        )
        rich_print(f"\n[bold italic]{pulumi_command}")
        print(
            "\nFor more info about this command, read: https://www.pulumi.com/docs/reference/cli/pulumi_up/"
        )
        self._ask_user_confirmation_to_execute_pulumi_command(
            pulumi_project_dir=pulumi_project_dir, pulumi_command=pulumi_command
        )

    def _run_section_1(self) -> None:
        rich_print("[bold yellow]### SECTION 1 - Deploy the infrastructure ###\n")
        print(
            "In this section we will walk you through the steps to deploy the infrastructure as code using Pulumi.\n"
        )
        self._recommend_pulumi_get_started_tutorial()
        stack_name = self._get_environment_name()
        pulumi_project_dir = self._copy_pulumi_files(stack_name=stack_name)
        self._update_aws_account_id(
            pulumi_project_dir=pulumi_project_dir, stack_name=stack_name
        )
        self._create_pulumi_stack(
            pulumi_project_dir=pulumi_project_dir, stack_name=stack_name
        )
        self._deploy_infrastructure(pulumi_project_dir=pulumi_project_dir)
        print(
            "The infrastructure required to run PySpark code on EMR Serverless has been successfully deployed"
        )

    def _run_section_2(self) -> None:
        rich_print("[bold yellow]### SECTION 2 - r the infrastructure ###\n")

    def run_example(self) -> None:
        self._run_section_1()
        self._run_section_2()

        # TODO - optional section to show how to do an update with pulumi
        # TODO - optional section to destroy the existing infrastructure and optionally too the stack history in pulumi
        # TODO -
