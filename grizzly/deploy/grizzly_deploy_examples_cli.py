import typer

from grizzly.deploy.spark.cloud.spark_emr_serverless.cli_example import SparkEmrServerlessCLIExample

app = typer.Typer(
    rich_markup_mode="rich"
)


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

