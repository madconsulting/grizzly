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
