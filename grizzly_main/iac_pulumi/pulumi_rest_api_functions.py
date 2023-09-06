import json
import logging
import os
import sys
from typing import Any

import requests  # type: ignore

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def get_pulumi_stack_state(
    pulumi_organization: str,
    pulumi_project: str,
    pulumi_stack: str,
    is_allow_input_token: bool = False,
) -> dict[str, Any]:
    """
    Get the stack state using the Pulumi REST API
    https://www.pulumi.com/docs/reference/service-rest-api/#get-stack-state
    :param pulumi_organization: Pulumi organization
    :param pulumi_project: Pulumi project
    :param pulumi_stack: Pulumi stack name
    :param is_allow_input_token: True if allowing to input PULUMI_ACCESS_TOKEN, False if required as an environment
                                 variable.
    :return: Stack state dictionary
    """
    pulumi_access_token = os.environ.get("PULUMI_ACCESS_TOKEN")
    if pulumi_access_token is None:
        msg = "PULUMI_ACCESS_TOKEN environment variable not defined."
        if is_allow_input_token:
            logging.warning(msg)
            pulumi_access_token = input(
                "Please run the process again with the PULUMI_ACCESS_TOKEN env var defined," " or input the value here:"
            )
        else:
            raise ValueError(msg)
    response = requests.get(
        url=f"https://api.pulumi.com/api/stacks/{pulumi_organization}/{pulumi_project}/{pulumi_stack}/export",
        headers={
            "Accept": "application/vnd.pulumi+8",
            "Content-Type": "application/json",
            "Authorization": f"token {pulumi_access_token}",
        },
        timeout=30,
    )
    return json.loads(response.text)


if __name__ == "__main__":
    res = get_pulumi_stack_state(
        pulumi_organization="victor-vila",
        pulumi_project="spark_emr_serverless",
        is_allow_input_token=True,
        pulumi_stack="dev",
    )
