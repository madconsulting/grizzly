import os
import typer
import inspect
from distutils.dir_util import copy_tree
from rich.prompt import Prompt

import grizzly.iac_pulumi.aws.pulumi_projects.spark_emr_serverless


class SparkEmrServerlessCLIExample:

    def __init__(self):
        pass

    def _copy_pulumi_files(self):
        source_dir = os.path.dirname(inspect.getfile(grizzly.iac_pulumi.aws.pulumi_projects.spark_emr_serverless))
        print(f"The Pulumi code will be copied from the directory: {source_dir}")
        dest_dir = Prompt.ask(
            prompt="[blue]Please write down the target directory",
            default="dir"
        )
        copy_tree(
            src=source_dir,
            dst=dest_dir
        )

    def run_example(self):
        self._copy_pulumi_files()


