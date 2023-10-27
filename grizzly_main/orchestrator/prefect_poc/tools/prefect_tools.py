from datetime import datetime


def generate_flow_run_name(base_name: str = "") -> str:
    """
    Generate flow run name using an UTC datetime based run id

    :param base_name: Base name / Suffix for the flow run name
    :return: Flow run name
    """
    run_datetime_id = datetime.utcnow().strftime("%Y%m%d%H%M%S_%f")
    if base_name != "":
        return f"{base_name}_{run_datetime_id}"
    return run_datetime_id
