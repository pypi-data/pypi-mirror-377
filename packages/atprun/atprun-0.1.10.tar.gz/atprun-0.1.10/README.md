# ATP-Run

atprun is a command-line tool that allows you to define and run scripts using a simple YAML configuration file. It is designed to be easy to use and flexible, making it a great choice for **managing** and **executing** scripts in your projects. It supports defining **environment variables**, **multi-line** scripts.
In the project directory, create a file named `atprun.yml` and define your scripts in it.

You can then use the `atprun script <script_name>` to run your scripts.

## Installation

### Pipx

You can install ATP-Run using Pipx, which is a tool to install and run Python applications in isolated environments.

```bash
pipx install atprun
```

### uv tool

You can also install ATP-Run using the `uv tool`, which is a tool to install and run Python applications in isolated environments.

```bash
uv tool install atprun
```

### pip

You can also install ATP-Run using pip:

```bash
pip install atprun
```

### Pipenv

You can also install ATP-Run using Pipenv:

```bash
pipenv install atprun
```

## Usage

Define your scripts in a YAML configuration file (e.g., `atprun.yml`) and use the `atprun script <script_name>` command to run them.

Example: `atprun script my_script`

### Examples `atprun.yml`

Simple script

```yaml
scripts:
  my_script:
    run: "echo Hello, World!"
```

Multiple line script

```yaml
scripts:
  my_script:
    run: |
      echo "First Line"
      echo "Second line"
```

Define environment variables

```yaml
scripts:
  my_script:
    env_var:
      ENV_VAR_TEST: "Hello world 1"
    run: echo "$ENV_VAR_TEST"
```
