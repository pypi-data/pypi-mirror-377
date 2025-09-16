"""Shared fixture set."""

import os
import pathlib
import shutil
import tempfile
from typing import Union

import pytest
from _pytest.config import ExitCode
from _pytest.fixtures import SubRequest
from _pytest.main import Session

import dagsesh.lazy
from dagsesh.logging_config import log


@pytest.fixture
def working_dir(request: "SubRequest") -> str:
    """Temporary working directory."""

    def fin() -> None:
        """Tear down."""
        log.info('Deleting temporary test directory: "%s"', dirpath)
        shutil.rmtree(dirpath)

    request.addfinalizer(fin)
    dirpath = tempfile.mkdtemp()
    log.info('Created temporary test directory: "%s"', dirpath)

    return dirpath


@pytest.fixture(scope="session")
def dagbag():
    """Set up the Airflow DagBag common to pytest.Session."""
    af_models = dagsesh.lazy.Loader("models", globals(), "airflow.models")

    return af_models.DagBag()


def pytest_sessionstart(session: Session) -> None:  # pylint: disable=unused-argument
    """Set up the Airflow context with appropriate config for test."""
    airflow_home = tempfile.mkdtemp()
    os.environ["AIRFLOW_HOME"] = airflow_home
    log.info('Temporary Airflow home (AIRFLOW_HOME): "%s"', airflow_home)

    project_dir = os.environ.get("PROJECT_SOURCE_DIR")
    if not project_dir:
        cwd = pathlib.Path.cwd()
        project_dir = os.path.join(cwd, cwd.resolve().name.lower().replace("-", "_"))

    os.environ["AIRFLOW__CORE__UNIT_TEST_MODE"] = "true"
    os.environ["AIRFLOW__CORE__DAGS_FOLDER"] = os.path.join(project_dir, "dags")
    os.environ["AIRFLOW__CORE__PLUGINS_FOLDER"] = os.path.join(project_dir, "plugins")
    os.environ["AIRFLOW__CORE__LOAD_EXAMPLES"] = "false"
    os.environ["AIRFLOW__CORE__FERNET_KEY"] = (
        "LFKF4PSrAOG-kbxOouoLj8Du2QCnsp9qw7G21-WPsLU="
    )
    db_url = f"sqlite:///{airflow_home}/airflow.db;Version=3;Journal Mode=Off;"
    os.environ["AIRFLOW__DATABASE__LOAD_DEFAULT_CONNECTIONS"] = "false"
    os.environ["AIRFLOW__DATABASE__SQL_ALCHEMY_CONN"] = db_url

    log.info('Airflow project directory: "%s"', project_dir)
    for key, val in [x for x in os.environ.items() if x[0].startswith("AIRFLOW__")]:
        log.info("Environment Variable %s: %s", key, val)

    if os.environ.get("AIRFLOW__DAGSESH__PRIME_TEST_CONTEXT") == "true":
        log.info("AIRFLOW__DAGSESH__PRIME_TEST_CONTEXT is set")
        utils_db = dagsesh.lazy.Loader("utils_db", globals(), "airflow.utils.db")
        utils_db.upgradedb()


def pytest_sessionfinish(  # pylint: disable=unused-argument
    session: Session,
    exitstatus: Union[int, ExitCode],
) -> None:
    """Tear down the Airflow context."""
    log.info(
        'Deleting working temporary test directory: "%s"', os.environ["AIRFLOW_HOME"]
    )
    shutil.rmtree(os.environ["AIRFLOW_HOME"])
