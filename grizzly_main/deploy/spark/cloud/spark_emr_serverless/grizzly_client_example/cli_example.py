import inspect
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import types
from importlib.machinery import SourceFileLoader
from typing import Any, Dict, Optional, no_type_check

import ruamel.yaml
import seedir as sd
from rich import print as rich_print
from rich.prompt import Prompt

import grizzly_main.deploy.spark.cloud.spark_emr_serverless.grizzly_client_example.files_to_copy
import grizzly_main.iac_pulumi.aws.pulumi_projects.spark_emr_serverless
from grizzly_main.iac_pulumi.aws.reusable_architectures.spark_emr_serverless import (
    create_spark_emr_serverless_architecture,
)
from grizzly_main.path_interations import cd


class SparkEmrServerlessCLIExample:
    """
    CLI example to deploy and run PySpark code on EMR Serverless
    """

    def __init__(
        self,
        main_dir: str = "deploy_examples/spark_emr_serverless_example",
        pulumi_subdir: str = "iac_pulumi",
        code_subdir: str = "main",
    ):
        """
        Initialise SparkEmrServerlessCLIExample class
        :param main_dir: Main directory
        :param pulumi_subdir: Pulumi subdirectory (within main_dir)
        :param code_subdir: Code subdirectory (within main_dir) with files to deploy venv and package, PySpark example
                            code and tools to trigger and monitor the EMR Serverless jobs
        """
        self.pulumi_dir = f"{main_dir}/{pulumi_subdir}"
        self.code_dir = f"{main_dir}/{code_subdir}"
        self.main_config_path = f"{self.code_dir}/main_config.py"
        self.pulumi_organization = None
        self.pulumi_project = None
        self.pulumi_stack = None
        self.stack_config_file = None
        self.idle_timeout_minutes = None

    def _ask_user_confirmation_to_execute_pulumi_command(self, pulumi_command: str) -> None:
        """
        Ask user for confirmation to execute a given pulumi command
        :param pulumi_command: Pulumi command
        :return: None
        """
        is_execute_command = Prompt.ask(
            prompt="[bold blue]\nWould you like me to execute the command above in this terminal?",
            choices=["y", "n"],
            default="y",
        )
        if is_execute_command == "y":
            with cd(self.pulumi_dir):
                res = subprocess.run(
                    pulumi_command.split(),
                    stderr=subprocess.PIPE,
                )
                if res.returncode != 0:
                    rich_print(
                        f"[bold red] The following error occurred with:"
                        f"\n- returncode {res.returncode}"
                        f"\n- stderr: {res.stderr.decode('utf-8')}"
                    )
                    print(
                        "Please start again the example addressing the Pulumi error above, or contact Mad Consulting "
                        "if you need further support."
                    )
                    sys.exit()
                else:
                    print("Pulumi command executed successfully")
        else:
            Prompt.ask(
                prompt="[bold blue]\nPlease execute the command above in another terminal. "
                "Afterwards, type enter when you are ready to continue.",
            )

    @staticmethod
    def _run_python_script_from_terminal(
        file_path: str,
        success_message: str,
        is_capture_output: bool = False,
        args: Optional[str] = None,
    ) -> Optional[str]:
        """
        Run python script from terminal
        :param file_path: File path
        :param success_message: Message to be printed if script runs successfully
        :param is_capture_output: True if we are capturing the output of the logic run, False otherwise
        :param args: Additional arguments
        :return:
        """
        is_execute_command = Prompt.ask(
            prompt="[bold blue]\nWould you like me to execute it in this terminal?",
            choices=["y", "n"],
            default="y",
        )
        if is_execute_command == "y":
            if is_capture_output:
                stdout = subprocess.PIPE
            else:
                stdout = None
            command = ["poetry", "run", "python", file_path]
            if args:
                command += args.split()
            res = subprocess.run(
                command,
                stdout=stdout,
                stderr=subprocess.PIPE,
            )
            if res.returncode != 0:
                rich_print(
                    f"[bold red] The following error occurred with:"
                    f"\n- returncode {res.returncode}"
                    f"\n- stderr: {res.stderr.decode('utf-8')}"
                )
                print(
                    "Please start again the example addressing the error above, or contact Mad Consulting if you need "
                    "further support."
                )
                sys.exit()
            else:
                print(success_message)
        else:
            Prompt.ask(
                prompt=f"[bold blue]\nPlease execute the script {file_path}\n"
                "Afterwards, type enter when you are ready to continue.",
            )
        if is_capture_output:
            stdout = res.stdout.decode("utf-8")  # type: ignore
            print(stdout)
            return stdout  # type: ignore
        else:
            return None

    @staticmethod
    def _recommend_pulumi_get_started_tutorial() -> None:
        """
        Ask if this is the first time the user uses Pulumi. In such case, recommend the AWS Get Started tutorial
        from Pulumi
        :return: None
        """
        is_first_time = Prompt.ask(
            prompt="[bold blue]Is this the first time you use Pulumi to deploy AWS infrastructure?",
            choices=["y", "n"],
            default="y",
        )
        if is_first_time == "y":
            print(
                "\nThen I recommend you to complete the following tutorial beforehand: "
                "https://www.pulumi.com/docs/get-started/aws/begin/. After completing this tutorial, you should "
                "have the prerequisites for this section, which are:"
            )
            print("- A Pulumi account with access to your AWS account.")
            print(
                "- Basic knowledge on how to create a Pulumi project and use basic pulumi commands to manage your "
                "infrastructure programmatically."
            )
            Prompt.ask(
                prompt="[bold blue]\nPlease type enter when you are ready to continue",
            )

    @no_type_check  # Neglect mypy checks for this function
    def _set_pulumi_project_and_stack(self) -> None:
        """
        Set Pulumi project and stack names
        :return: None
        """
        self.pulumi_project = Prompt.ask(
            prompt="[bold blue]\nPlease type the Pulumi Project name",
            default="spark_emr_serverless",
        )
        print(
            "\nWe will use a single environment for this example. We will also name the Pulumi Stack as the "
            "environment name."
        )
        self.pulumi_stack = Prompt.ask(
            prompt="[bold blue]\nPlease type the environment / stack name",
            default="dev",
        )

    def _copy_pulumi_files(self) -> None:
        """
        Copy pulumi files to client repository within self.pulumi_dir
        :return: None
        """
        source_dir = os.path.dirname(inspect.getfile(grizzly_main.iac_pulumi.aws.pulumi_projects.spark_emr_serverless))
        files_list = os.listdir(source_dir)
        # Keep only "dev" environment file name
        files_list = [
            file
            for file in files_list
            if not (
                (file.startswith("Pulumi.") and file.endswith(".yaml") and "dev" not in file) and file != "Pulumi.yaml"
            )
            and file != "__pycache__"
        ]
        print(f"\nThe Pulumi code will be copied from the directory: {source_dir}")
        if not os.path.exists(self.pulumi_dir):
            os.makedirs(self.pulumi_dir)
        else:
            if os.listdir(self.pulumi_dir):
                raise ValueError(f"Destination directory {self.pulumi_dir} is not empty")
        new_file_list = []
        for file in files_list:
            if file == "Pulumi.dev.yaml":
                if self.pulumi_stack:
                    new_file = file.replace("dev", self.pulumi_stack)
                else:
                    raise ValueError("Missing self.pulumi_stack")
            else:
                new_file = file
            new_file_dir = f"{os.path.abspath(self.pulumi_dir)}/{new_file}"
            shutil.copyfile(src=f"{source_dir}/{file}", dst=new_file_dir)
            new_file_list.append(new_file)
        print(f"The folowing files have been created in {self.pulumi_dir}: {new_file_list}")

    def _update_pulumi_project_name(self) -> None:
        """
        Update the Pulumi project name in the Pulumi project configuration (Pulumi.yaml)
        :return: None
        """
        config_file = f"{self.pulumi_dir}/Pulumi.yaml"
        data = ruamel.yaml.YAML().load(open(config_file, "r"))
        data["name"] = self.pulumi_project
        yaml = ruamel.yaml.YAML()
        with open(config_file, "w") as fp:
            yaml.dump(data, fp)
        print(f"The Pulumi Project name {self.pulumi_project} has been updated in the 'Pulumi.yaml' file.")

    def _update_aws_account_id(self) -> None:
        """
        Update the AWS account id in the Pulumi stack configuration (Pulumi.<stack>.yaml)
        :return: None
        """
        if self.pulumi_stack:
            self.stack_config_file = f"{self.pulumi_dir}/Pulumi.{self.pulumi_stack}.yaml"
        else:
            raise ValueError("Missing self.pulumi_stack")
        print(
            f"\nIn the stack configuration file ({self.stack_config_file}), there is the aws_account_id pending to be "
            f"filled. This account requires programmatic access with rights to deploy and manage resources handled "
            f"through Pulumi, as described in: "
            f"https://www.pulumi.com/docs/get-started/aws/begin/#configure-pulumi-to-access-your-aws-account"
        )
        aws_account_id = Prompt.ask(  # type: ignore
            prompt="[bold blue]\nPlease type your AWS account id",
        )
        data = ruamel.yaml.YAML().load(open(self.stack_config_file, "r"))
        data["config"]["aws_account_id"] = aws_account_id
        self.idle_timeout_minutes = data["config"]["idle_timeout_minutes"]
        yaml = ruamel.yaml.YAML()
        with open(self.stack_config_file, "w") as fp:
            yaml.dump(data, fp)
        print(f"\nThe AWS account has been updated in {self.stack_config_file}. The file content is printed below:\n")
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
                f"'create_spark_emr_serverless_architecture' function used in {self.pulumi_dir}/__main__.py "
            )
            print("print(create_spark_emr_serverless_architecture.__doc__)\n")
            print(create_spark_emr_serverless_architecture.__doc__)

    def _create_pulumi_stack(self) -> None:
        """
        Create a Pulumi stack if it does not exist already, otherwise select that stack
        :return: None
        """
        print("\nNow we are going to create a new stack (or select it, if already exists) using the following command:")
        rich_print("\n[bold italic]pulumi stack select <org-name>/<stack> --create")  # type: ignore
        print(
            "\nNote that <org-name> can be either the Pulumi organization where the stack will be created, or your "
            "\nPulumi individual Account ID if you don't belong to an organization."
            "\nFor more info about this command, read: https://www.pulumi.com/docs/reference/cli/pulumi_stack_select/"
        )
        self.pulumi_organization = Prompt.ask(  # type: ignore
            prompt="[bold blue]\nPlease type the target <org-name>",
        )
        pulumi_command = f"pulumi stack select {self.pulumi_organization}/{self.pulumi_stack} --create"
        rich_print(f"\nPulumi command: [bold italic]{pulumi_command}")
        self._ask_user_confirmation_to_execute_pulumi_command(pulumi_command=pulumi_command)

    def _deploy_infrastructure(self) -> None:
        """
        Deploy the infrastructure via Pulumi
        :return: None
        """
        pulumi_command = "pulumi up"
        print(f"\nNow we are going to deploy the infrastructure for the {self.pulumi_stack} stack")
        rich_print(f"\n[bold italic]{pulumi_command}")
        print("\nFor more info about this command, read: https://www.pulumi.com/docs/reference/cli/pulumi_up/")
        self._ask_user_confirmation_to_execute_pulumi_command(pulumi_command=pulumi_command)

    def _run_section_1(self) -> None:
        """
        Run Section 1 to deploy the infrastructure via Pulumi
        :return: None
        """
        rich_print("[bold yellow]\n### SECTION 1 - Deploy the infrastructure ###\n")
        print("In this section we will walk you through the steps to deploy the infrastructure as code using Pulumi.\n")
        self._recommend_pulumi_get_started_tutorial()
        self._set_pulumi_project_and_stack()
        self._copy_pulumi_files()
        self._update_pulumi_project_name()
        self._update_aws_account_id()
        self._create_pulumi_stack()
        self._deploy_infrastructure()
        print("The infrastructure required to run PySpark code on EMR Serverless has been successfully deployed")

    def _copy_files_for_minimal_example(self) -> None:
        """
        Copy files to deploy, trigger and monitor a minimal PySpark example
        :return: None
        """
        source_dir = os.path.dirname(
            inspect.getfile(grizzly_main.deploy.spark.cloud.spark_emr_serverless.grizzly_client_example.files_to_copy)
        )
        dst_dir = os.path.abspath(self.code_dir)
        shutil.copytree(
            src=source_dir,
            dst=dst_dir,
            ignore=shutil.ignore_patterns("README.txt", "__pycache__"),
        )

        print(f"The following files have been copied to the main example directory {self.code_dir}:")
        sd.seedir(dst_dir, style="lines")

    def _read_main_config(self) -> Dict[str, Any]:
        """
        Read main configuration
        :return: Main configuration dictionary
        """
        loader = SourceFileLoader(fullname="main_config_module", path=self.main_config_path)
        mod = types.ModuleType(loader.name)
        loader.exec_module(mod)
        return mod.main_config

    def _update_main_config_with_user_params(self) -> None:
        """
        Update main configuration with user parameters already provided as input in this CLI example or obtained from
        their system.
        :return: None
        """
        main_config_dict = self._read_main_config()
        main_config_dict["pulumi_organization"] = self.pulumi_organization
        main_config_dict["pulumi_project"] = self.pulumi_project
        main_config_dict["pulumi_stack"] = self.pulumi_stack
        poetry_version = subprocess.run(["poetry", "-V"], stdout=subprocess.PIPE).stdout.decode("utf-8")
        regex_version = r"version (\d+\.\d+\.\d+[a-z]?\d?)"
        try:
            poetry_version = re.search(regex_version, poetry_version).group(1)  # type: ignore
        except AttributeError:
            raise ValueError(
                f"Revise if poetry version from str '{poetry_version}' matches the regex format: {regex_version}"
            )
        main_config_dict["poetry_version"] = poetry_version
        main_config_dict["python_version"] = platform.python_version()
        main_config_dict["repository_name"] = (
            subprocess.run(
                "basename `git rev-parse --show-toplevel`",
                shell=True,
                stdout=subprocess.PIPE,
            )
            .stdout.decode("utf-8")
            .replace("\n", "")
        )
        with open(self.main_config_path, "w") as fp:
            fp.write("main_config = " + json.dumps(main_config_dict))
        print(
            f"\nThe main_config dictionary in {self.main_config_path} has been updated according to your "
            f"python and poetry versions and the Pulumi information previously provided in this example.\nFeel free "
            f"to revise the main_config dictionary values.\n"
        )

    def _deploy_venv_and_poetry_package(self) -> None:
        """
        Deploy venv and poetry package wheel files
        :return: None
        """
        file_path = f"{self.code_dir}/deploy_venv_and_poetry_package.py"
        print(
            f"Now, we are going to run the python script: {file_path}\n"
            f"This will create the venv and package wheel files and push them to s3."
        )
        self._run_python_script_from_terminal(
            file_path=file_path,
            success_message="venv and wheel files successfully created and pushed to s3",
        )

    def _run_section_2(self) -> None:
        """
        Run section 2 to deploy the virtual environment and package wheel files
        :return: None
        """
        rich_print("[bold yellow]\n### SECTION 2 -  Deploy the virtual environment and package wheel files ###\n")
        print(
            "For the EMR Serverless app, a custom Poetry virtual environment and package are used to:\n"
            "- Handle all the package dependencies and versioning.\n"
            "- Package all the files from the repository in a single wheel file, which will allow to have relative "
            "imports and thus, use modular code across all the repo.\n"
        )
        print(
            "In this section we will:\n"
            "1. Copy all the required files to run and monitor a minimal PySpark example on EMR Serverless.\n"
            "2. Create the venv and package wheel files and push them to the S3 bucket (already deployed in Section 1"
            " using Pulumi)\n"
        )
        self._copy_files_for_minimal_example()
        self._update_main_config_with_user_params()
        self._deploy_venv_and_poetry_package()

    def _trigger_emr_serverless_job(self) -> str:
        """
        Trigger EMR Serverless Job
        :return: Job ID
        """
        file_path = f"{self.code_dir}/trigger_emr_job.py"
        print(
            f"Now, we are going to run the python script: {file_path}\n\n"
            f"This will trigger the EMR Serverless job using the minimal PySpark code example from: "
            f"{self.code_dir}/pyspark_example.py\n"
            f"Note that multiple examples are available in the pyspark_example.py script (which are retrieved from the "
            f"grizzly_main package). Feel free to modify its __main__ to select a different example\n\n"
            f"The Spark resources used in the EMR job are defined in the main configuration: "
            f"{self.code_dir}/main_config.py\n"
            f"For this minimal example, we have very low computational requirements, so the main config has "
            f"the following specifications for the Spark workers:"
        )
        main_config_dict = self._read_main_config()
        rich_print(main_config_dict["spark_resources_dict"])
        print(
            'Although not required for this example, feel free to modify the "spark_resources_dict" within the '
            "main_config before triggering the job."
        )
        trigger_output = self._run_python_script_from_terminal(
            file_path=file_path,
            success_message="EMR Serverless job trigger was successful. Logs from trigger script:",
            is_capture_output=True,
        )
        out_partitioned = trigger_output.rpartition(", and id: ")  # type: ignore
        if len(out_partitioned) != 3:
            raise ValueError(
                "The prints in script to trigger EMR job might have been modified. We are relying on those"
                "to get the job id. Please, revise that the last print corresponds to: \n"
                "', and id: {job_run_id}'"
            )
        else:
            job_id = out_partitioned[-1].replace("\n", "")
            if job_id.isspace():
                raise ValueError(f"Job id is incorrect, no spaces expected!. Incorrect job_id = {job_id}")
        return job_id

    def _monitor_emr_serverless_job(self, job_id: str) -> None:
        """
        Monitor the progress of an EMR serverless job and provides a script to monitor the job
        using the Python AWS SDK.

        :param job_id: ID of the EMR serverless job that you want to monitor
        :return: None
        """
        file_path = f"{self.code_dir}/analyse_emr_job.py"
        args = f"--job_run_id={job_id}"
        print(
            f"\nYou can monitor the job from the AWS UI using EMR Studio, but we have also provided a script to "
            f"monitor directly the job using the python AWS SDK: {file_path}\n"
            f"Note 1: The logs will be stored in the following folder: {self.code_dir}/logs/\n"
            f"Note 2: We are passing the following argument for the job id: {args}"
        )
        is_monitoring_finished = False
        while not is_monitoring_finished:
            self._run_python_script_from_terminal(
                file_path=file_path,
                success_message="\nEMR Serverless monitoring finished.",
                args=args,
            )
            is_continue_monitoring = Prompt.ask(
                prompt="[bold blue]\nWould you like to repeat running the monitoring script? "
                "(e.g. If the job state was still 'pending' / 'scheduled' / 'running', you could wait a few "
                "minutes for the job to be in 'success' state, so that you can retrieve the complete logs)",
                choices=["y", "n"],
                default="y",
            )
            if is_continue_monitoring == "n":
                is_monitoring_finished = True

    def _run_section_3(self) -> None:
        """
        Run section 3 to trigger and monitor a Spark EMR Serverless Job
        :return: None
        """
        rich_print("[bold yellow]\n### SECTION 3 - Trigger and monitor a Spark EMR Serverless Job ###\n")
        print(
            "In this section we will:\n"
            "1. Trigger a Spark EMR Serverless job using a minimal PySpark code example.\n"
            "2. Monitor the Spark EMR Serverless job.\n"
            "3. [Optionally] Stop the Spark EMR Serverless application once the job has been completed.\n"
        )
        job_id = self._trigger_emr_serverless_job()
        self._monitor_emr_serverless_job(job_id=job_id)
        if self.idle_timeout_minutes is None:
            idle_timeout_minutes_equals = ""
        else:
            idle_timeout_minutes_equals = f" = {self.idle_timeout_minutes} min"
        print(
            "\nNote that the EMR Serverless application will stop automatically after a certain amount of time being "
            f"idle (as configured in the parameter idle_timeout_minutes{idle_timeout_minutes_equals}, in the Pulumi "
            f"stack config file: {self.stack_config_file}).\n"
            "Also, note that there won't be any charges for the time when the application is idle without any "
            "running jobs. But if for any other reason you wanted to manually stop the application, you can do that by "
            f"executing the following script: {self.code_dir}/stop_emr_app.py"
        )

    def _common_steps_guidelines(self, start_num: int, is_select_stack: bool = True) -> str:
        """
        The function `_common_steps_guidelines` returns a string containing common steps for a Pulumi project,
        including  selecting a stack if necessary.

        :param start_num: The `start_num` parameter is an integer that represents the starting number for the steps
        in the list. It is used to generate step numbers for each item in the `common_steps_list`
        :param is_select_stack: The `is_select_stack` parameter is a boolean flag that determines whether or not
        to include the step for selecting a stack in the common steps list. If `is_select_stack` is `True`, the step
        for selecting a stack will be included. If `is_select_stack` is `False`,, defaults to True
        :return: a string that contains a list of common steps or instructions.
        """
        common_steps_list = [
            f'Open a new terminal and go to the Pulumi project directory: "cd {self.pulumi_dir}"\n',
            'If the poetry environment is not activated, execute "poetry shell"\n',
        ]
        if is_select_stack:
            common_steps_list.append(
                "If the Pulumi project has multiple stacks, select the desired stack with the following command: "
                f'"pulumi stack select {self.pulumi_organization}/<pulumi-stack>"\n'
                "For example, if we wanted select the initial stack created in this example, we would replace"
                f"<pulumi-stack> by {self.pulumi_stack} in the command above."
            )
        common_steps = ""
        for i, step in enumerate(common_steps_list):
            common_steps += f"{i+start_num}. step"
        return common_steps

    def _guidelines_option_a(self) -> None:
        """
        Guidelines for option A - Update the infrastructure resources
        :return: None
        """
        common_steps = self._common_steps_guidelines(start_num=2)
        print(
            "In order to update the infrastructure via Pulumi, you should follow the steps below:"
            f"1. Update the Pulumi stack configuration parameters in: {self.stack_config_file}\n"
            f"{common_steps}"
            f'5. Execute "pulumi refresh" to adopt any potential changes in the cloud provider side to the current'
            f" Pulumi stack.\n"
            f'6. Execute "pulumi up" to deploy the infrastructure resources updates.\n'
        )

    def _guidelines_option_b(self) -> None:
        """
        Guidelines for option B - Deploy a new environment and run Spark job on this environment
        :return: None
        """
        common_steps = self._common_steps_guidelines(start_num=1, is_select_stack=False)
        print(
            "These are the recommended steps to deploy a new environment (in the Pulumi commands we have "
            "abstracted the stack name to <stack-name>):"
            f"{common_steps}"
            f"3. Create a new environment, copying the config from the previous environment: "
            f'"pulumi stack init {self.pulumi_organization}/<pulumi-stack> --copy-config-from '
            f'{self.pulumi_organization}/{self.pulumi_stack}"\n'
            f"4. Feel free to  update the parameters in the copied config file: "
            f"{self.pulumi_dir}/Pulumi.<pulumi-stack>.yaml\n"
            f'5. Execute "pulumi up" to deploy the infrastructure resources for the new stack\n'
            f"6. To trigger and monitor a PySpark job on this new environment, you just need to update the "
            f"pulumi_stack value in the main configuration dictionary (in {self.code_dir}/main_config.py). "
            f"Afterwards, you can follow the same procedure as in Section 3 in this example."
        )

    def _guidelines_option_c(self) -> None:
        """
        Guidelines for option C - Destroy a stack and its infrastructure resources
        :return: None
        """
        common_steps = self._common_steps_guidelines(start_num=1)
        print(
            "These are the recommended steps to destroy the infrastructure. Note that this will delete "
            "permanently all the stack resources, so it is irreversible and should be used with great care.\n"
            f"{common_steps}"
            f'4. Execute "pulumi destroy" to delete all the existing resources in the stack.'
            f"5. The stack itself has not deleted at this point. If you would like to delete the stack and its "
            f'config, execute "pulumi stack rm {self.pulumi_organization}/<pulumi-stack>"\n'
        )

    def _run_optional_section(self) -> None:
        """
        Run optional section to trigger and monitor a Spark EMR Serverless Job
        :return: None
        """
        rich_print("[bold yellow]\n### OPTIONAL SECTIONS  ###\n")
        print(
            "Finally, we provide a list of optional sections, in case you would like further guidelines on some of "
            "these topics:\n"
            "A. Update the infrastructure resources.\n"
            "B. Deploy a new environment and trigger an EMR Serverless job for that environment.\n"
            "C. Destroy the infrastructure resources.\n"
        )
        choices = ["A", "B", "C", "exit"]
        choices_to_func_dict = {
            "A": self._guidelines_option_a,
            "B": self._guidelines_option_b,
            "C": self._guidelines_option_c,
        }
        default = "exit"
        option = Prompt.ask(
            prompt='[bold blue]\n Please select an optional section or type "exit" to finish the example:',
            choices=choices,
            default=default,
        )
        is_exit = False
        while not is_exit:
            if option != "exit":
                choices_to_func_dict[option]()
            option = Prompt.ask(
                prompt="[bold blue]\n If you would like to go through another section, please type the corresponding "
                'option or type "exit" to finish the example:',
                choices=choices,
                default=default,
            )

    def run_example(self) -> None:
        """
        Run CLI example
        :return: None
        """
        self._run_section_1()
        self._run_section_2()
        self._run_section_3()
        self._run_optional_section()
        print(
            "\nCongratulations! You have successfully completed this example on how to deploy and run PySpark code "
            "on EMR Serverless."
        )


# For debugging purposes:
# if __name__ in "__main__":
#     self = SparkEmrServerlessCLIExample()
