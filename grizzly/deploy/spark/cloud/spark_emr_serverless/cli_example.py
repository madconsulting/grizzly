import os
import typer
import inspect
from distutils.dir_util import copy_tree

import grizzly.iac_pulumi.aws.pulumi_projects.spark_emr_serverless


class SparkEmrServerlessCLIExample:

    def __init__(self):
        pass

    def _copy_pulumi_files(self):
        source_dir = os.path.dirname(inspect.getfile(grizzly.iac_pulumi.aws.pulumi_projects.spark_emr_serverless))
        print(f"Copying Pulumi code from directory: {source_dir}")
        # copy_tree(
        #     src=os.path.abspath("grizzly/iac_pulumi/aws/pulumi_projects/spark_emr_serverless"),
        #     dst=
        # )

    def run_example(self):
        self._copy_pulumi_files()


