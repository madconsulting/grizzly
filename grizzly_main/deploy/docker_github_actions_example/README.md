# **Docker & GitHub Actions**

Minimal "Hello, world!" example to build and run docker image within GitHub actions. We are using the repo's
Poetry environment within Docker. As it includes all the required dependencies, it is very straightforward
to extend this example to run or test anything within the repo in the GitHub actions workflow.


## Steps

1) To build and run locally the "Hello, world" example in the docker container, execute the following
   commands from the repo's root folder (grizzly/):
`docker build -f grizzly_main/deploy/docker_github_actions_example/Dockerfile -t hello_world .`
`docker run -it hello_world poetry run python grizzly_main/deploy/docker_github_actions_example/hello_world.py`

2) To test GitHub Actions' workflows locally:

- Install act (installation guidelines in https://github.com/nektos/act). For example via a bash command:
`curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash`
Ensure that you have the bin/ directory where act has been installed in your 'PATH':
`export PATH="$PATH:/path_to_grizzly_bin"`

- Run the following command from the repo's root folder (grizzly/) to run all .github/workflows:
`act`

3) To run GitHub Actions workflows, simply create a GitHub event that will trigger the workflow, such as code pushes,
   pull requests, etc.
