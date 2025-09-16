# Dagsesh: Airflow DAG Session Manager

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [(macOS Users) Upgrading GNU Make](#macos-users-upgrading-gnu-make)
  - [Creating the Local Environment](#creating-the-local-environment)
  - [Local Environment Maintenance](#local-environment-maintenance)
- [Help](#help)
- [Running the Test Harness](#running-the-test-harness)
- [Using `dagsesh` Plugin in your Project's Test Suite](#using-dagsesh-plugin-in-your-projects-test-suite)
- [FAQs](#FAQs)

## Overview
An Apache Airflow session context manager that overrides the default `AIRFLOW_HOME` path with a random, ephemeral alternate.

Why is this useful? As per the [Airflow configuration docs](https://airflow.apache.org/docs/apache-airflow/stable/howto/set-config.html):

> The first time you run Airflow, it will create a file called `airflow.cfg` in your `$AIRFLOW_HOME` directory (`~/airflow` by default).

Dagsesh delays the creation of `AIRFLOW_HOME` using a lazy-loading facility whilst injecting it with a random alternate. Great if you want to create a pristine Airflow environment for repeatable testing.

Dagsesh can be used as a convenient [pytest](https://docs.pytest.org/en/latest/contents.html) plugin to prime an Airflow environment for testing.

[top](#dagsesh-airflow-dag-session-manager)

## Prerequisites
- [GNU make](https://www.gnu.org/software/make/manual/make.html)
- Python 3 Interpreter. [We recommend installing pyenv](https://github.com/pyenv/pyenv)
- [Docker](https://www.docker.com/)

[top](#dagsesh-airflow-dag-session-manager)

## Getting Started
[Makester](https://loum.github.io/makester/) is used as the Integrated Developer Platform.

### (macOS Users) Upgrading GNU Make
Follow [these notes](https://loum.github.io/makester/macos/#upgrading-gnu-make-macos) to get [GNU make](https://www.gnu.org/software/make/manual/make.html).

### Creating the Local Environment
Get the code and change into the top level `git` project directory:
```
git clone git@github.com:loum/dagsesh.git && cd dagsesh
```

> **_NOTE:_** Run all commands from the top-level directory of the `git` repository.

For first-time setup, get the [Makester project](https://github.com/loum/makester.git):
```
git submodule update --init
```

Initialise the environment:
```
make init-dev
```

#### Local Environment Maintenance
Keep [Makester project](https://github.com/loum/makester.git) up-to-date with:
```
git submodule update --remote --merge
```

[top](#dagsesh-airflow-dag-session-manager)

## Help
There should be a `make` target to get most things done. Check the help for more information:
```
make help
```
[top](#dagsesh-airflow-dag-session-manager)

## Running the Test Harness
We use [pytest](https://docs.pytest.org/en/latest/). To run the tests:
```
make tests
```

[top](#dagsesh-airflow-dag-session-manager)

## Using `dagsesh` Plugin in your Project's Test Suite
Add the `dagsesh` package as a dependency to your project's development environment so that the plugin is installed and visible in your `PYTHONPATH`.  `dagsesh` takes care of the distribution's entry point so that `pytest` automatically finds the plugin module.  Nothing else needs to be done.

> **_NOTE:_** See [Making your plugin installable by others](https://docs.pytest.org/en/latest/how-to/writing_plugins.html#making-your-plugin-installable-by-others) for more information.

---
[top](#dagsesh-airflow-dag-session-manager)
