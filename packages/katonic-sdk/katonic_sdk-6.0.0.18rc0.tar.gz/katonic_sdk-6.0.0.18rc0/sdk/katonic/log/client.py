#!/usr/bin/env python
#
# Copyright (c) 2023 Katonic Pty Ltd. All rights reserved.
#
import logging
import os
import traceback
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import mlflow
from katonic.version import get_version
from mlflow.exceptions import RestException


mlflow.set_tracking_uri(os.environ["MLFLOW_BASE_URL"])
client = mlflow.tracking.MlflowClient(os.environ["MLFLOW_BASE_URL"])
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)


def set_exp(exp_name: str) -> Any:
    """
    Set given experiment as active experiment. If experiment does not exist, create an experiment with provided name.

    Args:
        exp_name (str): Case sensitive name of an experiment to be activated.
    """
    return mlflow.set_experiment(exp_name)


def load_model(model_uri: str) -> Any:
    """
    Load a model stored in Python function format.

    Args:
        model_uri: The location, in URI format, of the MLflow model.
        example:
        - ``/Users/me/path/to/local/model``
        - ``relative/path/to/local/model``
        - ``s3://my_bucket/path/to/model``
        - ``runs:/<mlflow_run_id>/run-relative/path/to/model``
        - ``models:/<model_name>/<model_version>``
        - ``models:/<model_name>/<stage>``
        - ``mlflow-artifacts:/path/to/model``
    """
    try:
        return mlflow.pyfunc.load_model(model_uri)
    except Exception as e:
        print(e)


def spark_udf(
    spark,
    model_uri: str,
    result_type: str = "double",
    env_manager: str = "local",
) -> Any:
    """
    A Spark UDF that can be used to invoke the Python function formatted model.

    Parameters passed to the UDF are forwarded to the model as a DataFrame where the column names
    are ordinals (0, 1, ...). On some versions of Spark (3.0 and above), it is also possible to
    wrap the input in a struct. In that case, the data will be passed as a DataFrame with column
    names given by the struct definition (e.g. when invoked as my_udf(struct('x', 'y')), the model
    will get the data as a pandas DataFrame with 2 columns 'x' and 'y').

    If a model contains a signature, the UDF can be called without specifying column name
    arguments. In this case, the UDF will be called with column names from signature, so the
    evaluation dataframe's column names must match the model signature's column names.

    The predictions are filtered to contain only the columns that can be represented as the
    ``result_type``. If the ``result_type`` is string or array of strings, all predictions are
    converted to string. If the result type is not an array type, the left most column with
    matching type is returned.

    Args:
        spark: A SparkSession object.
        model_uri: The location, in URI format, of the MLflow model with the
                    :py:mod:`mlflow.pyfunc` flavor. For example:

                    - ``/Users/me/path/to/local/model``
                    - ``relative/path/to/local/model``
                    - ``s3://my_bucket/path/to/model``
                    - ``runs:/<mlflow_run_id>/run-relative/path/to/model``
                    - ``models:/<model_name>/<model_version>``
                    - ``models:/<model_name>/<stage>``
                    - ``mlflow-artifacts:/path/to/model``

                    For more information about supported URI schemes, see
                    `Referencing Artifacts <https://www.mlflow.org/docs/latest/concepts.html#
                    artifact-locations>`_.

        result_type: the return type of the user-defined function. The value can be either a
            ``pyspark.sql.types.DataType`` object or a DDL-formatted type string. Only a primitive
            type or an array ``pyspark.sql.types.ArrayType`` of primitive type are allowed.
            The following classes of result type are supported:

            - "int" or ``pyspark.sql.types.IntegerType``: The leftmost integer that can fit in an
            ``int32`` or an exception if there is none.

            - "long" or ``pyspark.sql.types.LongType``: The leftmost long integer that can fit in an
            ``int64`` or an exception if there is none.

            - ``ArrayType(IntegerType|LongType)``: All integer columns that can fit into the requested
            size.

            - "float" or ``pyspark.sql.types.FloatType``: The leftmost numeric result cast to
            ``float32`` or an exception if there is none.

            - "double" or ``pyspark.sql.types.DoubleType``: The leftmost numeric result cast to
            ``double`` or an exception if there is none.

            - ``ArrayType(FloatType|DoubleType)``: All numeric columns cast to the requested type or
            an exception if there are no numeric columns.

            - "string" or ``pyspark.sql.types.StringType``: The leftmost column converted to ``string``.

            - "boolean" or "bool" or ``pyspark.sql.types.BooleanType``: The leftmost column converted
            to ``bool`` or an exception if there is none.

            - ``ArrayType(StringType)``: All columns converted to ``string``.

        env_manager: The environment manager to use in order to create the python environment
                        for model inference. Note that environment is only restored in the context
                        of the PySpark UDF; the software environment outside of the UDF is
                        unaffected. Default value is ``local``, and the following values are
                        supported:

                        - ``virtualenv``: Use virtualenv to restore the python environment that
                        was used to train the model.
                        - ``conda``: (Recommended) Use Conda to restore the software environment
                        that was used to train the model.
                        - ``local``: Use the current Python environment for model inference, which
                        may differ from the environment used to train the model and may lead to
                        errors or invalid predictions.

    Returns:
        Spark UDF that applies the model's ``predict`` method to the data and returns a
        type specified by ``result_type``, which by default is a double.
    """
    try:
        return mlflow.pyfunc.spark_udf(
            spark=spark,
            model_uri=model_uri,
            result_type=result_type,
            env_manager=env_manager,
        )
    except Exception as e:
        print(e)


class MLClient:
    """
    A MLClient Object is used to define, create a experiment.

    Args:
        exp_name (str): Case sensitive name of an experiment to be activated.
        source_name (str): Name of the current notebook or script. eg: "sample.ipynb or sample.py"
        features (Optional[List[str]]): Optional List of feature names (str) of the current experiment/modeling.
        artifacts (Optional[Dict[str, str]]): Optional artifacts as dict e.g. dataset path or images folder of the current experiment.
        eg: {"data_path": "data/"}
    """

    def __init__(
        self,
        exp_name: str,
        source_name: str,
        features: Optional[List[str]] = None,
        artifacts: Optional[Dict[str, str]] = None,
    ):

        if not isinstance(exp_name, str):
            raise ValueError("exp_name must be string")
        if not exp_name:
            raise ValueError("exp_name cannot be null or empty string")

        set_exp(exp_name)

        exp_details = mlflow.get_experiment_by_name(exp_name)
        self.name = exp_details.name
        self.location = exp_details.artifact_location
        self.id = exp_details.experiment_id
        self.stage = exp_details.lifecycle_stage
        self.tag = exp_details.tags
        self.source_name = source_name
        self.features = features
        self.username = os.getenv("EXP_USER") or "default"
        self.artifact_paths = artifacts or {}
        logger.info("MLClient successfully instantiated")

    def set_model_tags(self, run_id):

        tags = {
            "version.mlflow": mlflow.__version__,
            "data_path": self.artifact_paths["data_path"]
            if "data_path" in self.artifact_paths.keys()
            else "-",
            "experiment_id": self.id,
            "experiment_name": self.name,
            "mlflow.source.name": self.source_name,
            "mlflow.source.type": "notebook"
            if self.source_name.split(".")[-1] == "ipynb"
            else "script",
            "mlflow.user": self.username,
            "run_id": run_id,
            "features": self.features or "-",
        }
        logger.info(f"logged tags: {tags.keys()}")
        try:
            mlflow.set_tags(tags)
        except Exception:
            logger.warning("Couldn't perform set_tags. Exception:")
            logger.warning(traceback.format_exc())

        self.artifact_paths["source"] = os.path.realpath(self.source_name)
        logger.info(f"logged artifacts: {self.artifact_paths.keys()}")
        try:
            [
                mlflow.log_artifacts(self.artifact_paths[key])
                if os.path.isdir(self.artifact_paths[key])
                else mlflow.log_artifact(self.artifact_paths[key])
                for key in self.artifact_paths.keys()
            ]
        except Exception:
            logger.warning("Couldn't perform log_artifacts. Exception:")
            logger.warning(traceback.format_exc())

    def search_runs(self, exp_id: str):
        """
        This function search runs and return dataframe of runs. It takes exp_id as input
        and returns the list of experiment ids.

        Args:
            exp_id (List[str]): List of experiment IDs. None will default to the active experiment

        Returns:
            A list of experiment ids
        """
        try:
            df = mlflow.search_runs(experiment_ids=exp_id)
            df.columns = df.columns.str.replace("tags.mlflow.runName", "run_name")
            exclude_cols = [
                "tags.mlflow.source.type",
                "tags.mlflow.user",
                "tags.mlflow.source.name",
            ]
            df = df[df.columns.difference(exclude_cols)]
            return df
        except Exception:
            print(f"Experiment id {exp_id} does not exists")

    def register_model(self, model_name: str, run_id: str) -> Any:
        """
        This function register the given model in model registry and create a new version of it (if not registered).

        Args:
            model_name (str): name of the model.
            run_id (str): experiment id.

        Returns:
            A single ModelVersion object.
        """
        try:
            try:
                client.create_registered_model(model_name)
            except RestException:
                print(
                    f"Registered Model (name={model_name}) already exists. Adding new versions to it."
                )

            result = client.create_model_version(
                name=model_name,
                source=f"{self.location}/{run_id}/artifacts/{model_name}",
                run_id=run_id,
            )
            return result.to_proto()
        except Exception:
            print(f"Could not register the model {model_name} with run_id {run_id}")

    def change_stage(self, model_name: str, ver_list: List[str], stage: str) -> Any:
        """
        This function changes stage of model. (Staging, Production or Archived).

        Args:
            model_name (str): name of the model.
            ver_list (List[str]): version list of the model.
            stage (str): Staging, Production and archived.
        """
        try:
            list(
                map(
                    lambda x: client.transition_model_version_stage(  # type: ignore
                        name=model_name, version=x, stage=stage
                    ),
                    ver_list,
                )
            )
        except Exception:
            print(
                f"Could not change the stage of model {model_name} for versions {ver_list}."
            )

    def model_versions(self, model_name: str) -> Any:
        """
        This function returns the model versions if match with filter string.

        Args:
            model_name (str): Name of the model taken as input string.
        """
        try:
            filter_string = f"name='{model_name}'"
            results = client.search_model_versions(filter_string)
        except Exception:
            print(
                f"Could not get the versions of model {model_name}. Try another name "
            )
        return list(map(lambda x: x.version, results))  # type: ignore

    def log_data(self, run_id: str, data_path: str) -> None:
        """
        This function stores joblib objects in model artifact.

        Args:
            run_id (str): run_id of experiment.
            data_path (Any): local dataset path to log.
        """
        client.log_artifact(run_id=run_id, local_path=data_path)

    def delete_model_version(self, model_name: str, ver_list: List[str]) -> Any:
        """
        This function deletes model versions.

        Args:
            model_name (str) : name of the model
            ver_list (List[str]): list of all it"s versions.
        """
        try:
            list(
                map(
                    lambda version: client.delete_model_version(  # type: ignore
                        name=model_name, version=version
                    ),
                    ver_list,
                )
            )
        except Exception:
            print(
                f"Could not delete the respective versions {ver_list} of model {model_name}. Make sure the versions or model exists"
            )

    def delete_reg_model(self, model_name: str):
        """
        This function deletes registered model with all its version.

        Args:
            model_name (str): Name of the registered model to update.
        """
        try:
            return client.delete_registered_model(name=model_name)
        except Exception:
            print(
                f"Could not delete the registered model {model_name}. Make sure the model is registered"
            )

    def delete_run_by_id(self, run_ids: List[str]) -> Any:
        """
        delete runs with the specific run_ids.

        Args:
            run_ids (List[str]): The unique run ids to delete.
        """
        try:
            list(map(lambda run: client.delete_run(run_id=run), run_ids))  # type: ignore
            print(f'{", ".join(run_ids)} run-ids successfully deleted')
        except Exception:
            print(f"Could not delete run_ids {run_ids}. Make sure they exits")

    def version(self) -> str:
        """Returns the version of the current Katonic SDK."""
        return get_version()  # type: ignore
