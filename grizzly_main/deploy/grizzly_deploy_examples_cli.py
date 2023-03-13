import typer
from rich.prompt import Prompt
from rich import print as rich_print

from grizzly_main.deploy.spark.cloud.spark_emr_serverless.grizzly_client_example.cli_example import SparkEmrServerlessCLIExample

app = typer.Typer(
    rich_markup_mode="rich"
)


def explain_cli_format():
    is_explain_legend = Prompt.ask(
        prompt="[bold][blue]\nBefore we start the example, would you like an explanation of the formatting used "
               "in the cli?",
        choices=["y", "n"],
        default="y"
    )
    if is_explain_legend == "y":
        print(f"\n - Guidelines will appear in the standard format of your terminal (same as this line)")
        rich_print(f" - [bold][blue]The inputs will be requested with prompts in blue")
        rich_print(f" - [bold][magenta]The request choices will be in magenta within []")
        rich_print(f" - [bold][cyan]The request defaults will be in cyan within (). If you directly type enter, "
                   f"the default value will be used.\n")
    print("Let's start the example!\n")


@app.callback()
def callback():
    """
    [bold][magenta]Grizzly guided examples to deploy PySpark code to cloud platforms using infrastructure as code (using Pulumi)
    """


@app.command(rich_help_panel="Spark - AWS")
def emr_serverless():
    """
    Guided example to deploy Spark in AWS with EMR Serverless
    """
    explain_cli_format()
    SparkEmrServerlessCLIExample().run_example()


@app.command(rich_help_panel="Spark - AWS")
def emr_on_eks():
    """
    [COMING SOON] Guided example to deploy Spark in AWS with EMR on EKS
    """
    print("Example coming soon!")


@app.command(rich_help_panel="Spark - GCP")
def dataproc_serverless():
    """
    [NOT IMPLEMENTED YET] Guided example to deploy Spark in GCP with Dataproc Serverless
    """
    print("Not implemented yet.")

