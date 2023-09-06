import subprocess


def test_hello_world_output() -> None:
    """
    Run the "Hello, world!" example and verify that the output is correct.
    :return: None
    """
    expected_output = "Hello, world!"
    completed_process = subprocess.run(
        ["poetry", "run", "python", "grizzly_main/deploy/docker_github_actions_example/hello_world.py"],
        capture_output=True,
        text=True,
        check=True,
    )
    actual_output = completed_process.stdout.strip()
    assert actual_output == expected_output, f"Expected '{expected_output}', but got '{actual_output}'"
