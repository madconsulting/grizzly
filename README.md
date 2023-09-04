# **Grizzly**

## Pre-commit hooks

The recommended usage of pre-commit hooks is the following:

1) Before any commit, you should run `pre-commit run --all-files` iteratively until fixing all the errors raised
   by the hooks. Note that the pre-commit hooks include automatic formatting (_isort_ and _black_) and generation of
   HTML documentation (_pdoc3_). If any modifications were automatically made, these hooks would fail. The next time
   that those hooks are run no  additional modifications will be made and thus, _isort_, _black_ and _pdoc3_ should show
   a pass.

2) Once all the other hooks have passed without errors, you can add your files to git (`git add .`) and commit them
   (`git commit -m "your commit message"`) and push them (`git push origin <branch name>`)

NOTE: It's possible to disable the hooks in the commit and push commands by adding the `--no-verify` flag, but this
is highly discouraged.

Below there are additional explanations and guidelines on the pre-commit hooks:
   - The hook's dependencies have also been included in the Poetry environment (_pyproject.toml_ file), to be able
     to run them independently at any time.
   - The setup for some hooks (e.g. maximum line length) is provided via the _setup.cfg_ file and in _pyproject.toml_,
     ensuring consistency in these hooks settings when executed manually via the Poetry environment or triggered
     running a git command.
   - There is a separate configuration for _pylint_: _.pylintrc_ file. This contains all the Pylint errors to be
     neglected across all the grizzly repo.
   - Most hooks offer a methodology to disable some errors or warnings at a very granular level in the code. For
     example:
     - pylint: Using the `# pylint: disable=<error_code>` methodology, as explained in:
               https://pylint.pycqa.org/en/latest/user_guide/messages/message_control.html#block-disables
     - mypy: Using `# type: ignore`, as explained in:
             https://mypy.readthedocs.io/en/stable/common_issues.html#spurious-errors-and-locally-silencing-the-checker
     - flake8: Using `# noqa: <error_code>`, as explained in:
               https://flake8.pycqa.org/en/latest/user/violations.html#in-line-ignoring-errors
     - black: It disables the formatting for lines that end with `# fmt: skip` or blocks the ones that start with
              `# fmt: off` and end with `# fmt: on`
              (https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html#code-style)
     If you encounter with other hooks' errors that need to be neglected at the code level and not described here,
     please read the specific library documentation and update this README.md file accordingly.

