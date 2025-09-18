# ATP-Run

`atprun` is a command-line tool that allows you to define and run scripts using a simple YAML configuration file. It is designed to be easy to use and flexible, making it a great choice for **managing** and **executing** scripts in your projects. It supports defining **environment variables**, **multi-line** scripts.
In the project directory, create a file named `atprun.yml` and define your scripts in it.

You can then use the `atprun script <script_name>` to run your scripts.

## 1. Installation

### 1.1. Pipx

You can install ATP-Run using Pipx, which is a tool to install and run Python applications in isolated environments.

```bash
pipx install atprun
```

### 1.2. uv tool

You can also install ATP-Run using the `uv tool`, which is a tool to install and run Python applications in isolated environments.

```bash
uv tool install atprun
```

### 1.3. pip

You can also install ATP-Run using pip:

```bash
pip install atprun
```

### 1.4. Pipenv

You can also install ATP-Run using Pipenv:

```bash
pipenv install atprun
```

## 2. Usage

Define your scripts in a YAML configuration file (e.g., `atprun.yml`) and use the `atprun script <script_name>` command to run them.

Example: `atprun script my_script`

### 2.1. Examples `atprun.yml`

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

## 3. Settings

### 3.1 Configuration File

Default: `atprun.yml` (current directory)

You can change the path to the configuration file using the `--config-path` option.

Example:

```bash
atprun --config-path path/to/your_config.yml script my_script
```

or by setting environment variable `ATPRUN_CONFIG_PATH`

Example:

```bash
export ATPRUN_CONFIG_PATH=path/to/your_config.yml
```
