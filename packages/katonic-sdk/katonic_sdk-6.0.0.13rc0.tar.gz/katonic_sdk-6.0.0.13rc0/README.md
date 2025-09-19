<p align="center">
    <a href="https://katonic.ai/">
      <img src="https://katonic.ai/assets/brand/Logo.png" width="550">
    </a>
</p>
<br />

[![Docs Latest](https://img.shields.io/badge/docs-latest-blue.svg)](https://docs.katonic.ai/)
[![License](https://img.shields.io/badge/License-MIT-blue)](https://github.com/katonic-dev/katonic-sdk/blob/master/LICENSE)
[![PYPI](https://img.shields.io/pypi/v/katonic.svg)](https://pypi.python.org/pypi/katonic)

Katonic Python SDK for Complete ML Model Life Cycle.

Katonic Python SDK is a comprehensive package to perform all the Machine Learning and Data Science related operations.

For a complete list of examples and notebooks, please take a look at the [Examples](https://github.com/katonic-dev/Examples/tree/master/katonic-sdk).

## Minimum Requirements
* Katonic Platform 3.3 or Higher.
* Python 3.8 or Higher.

## Download using pip for the base package.
```sh
pip install katonic
```

Katonic base package installation consists log packages to log your standard or custom built model in to Katonic model registry, see example below.

The topics in this page:

- [Connectors](#connectors)
- [Filemanager](#filemanager)
- Feature Engineering
- [Feature Store](#feature-store)
- [Experiment Operations](#experiment-operations)
- [Registry Operations](#registry-operations)
- [Pipeline Operations](#pipeline-operations)
- [Drift](#drift)

### Connectors

A typical AI model life cycle starts with loading the data into your workspace and analyzing it to discover useful insights. for that you can use Katonic's SDK, there are several connectors inside it you can use to load the data and put it where ever you want to work with. Ex. Azure blob, MySql, Postgres etc.

### Install Connectors.
```python
pip install katonic[connectors]
```
### Connector example to get the data from SNOWFLAKE.
*snowflake-credentials.json*

```json
{
    "USER": "username",
    "PASSWORD": "password",
    "ACCOUNT": "id.uae-north.azure",
    "DATABASE": "SNOWFLAKE_SAMPLE_DATA",
    "TABLE_NAME": "CUSTOMER",
    "SCHEMA": "TPCH_SF1",
    "WAREHOUSE": "COMPUTE_WH"
}
```
```python
# Define all your configurations inside a JSON file.
import json

with open('snowflake-credentials.json') as f:
    config = json.load(f)
```
Initializing the SnowFlakeConnector with the provided credentials and configuration.
```python
from katonic.connectors.python.snowflake import SnowFlakeConnector

df = SnowFlakeConnector(
    user=config["USER"],
    password=config["PASSWORD"],
    account=config["ACCOUNT"],
    database=config["DATABASE"],
    table_name=config["TABLE_NAME"],
    schema=config["SCHEMA"],
    warehouse=config["WAREHOUSE"],
    query="SELECT * FROM TPCH_SF1.CUSTOMER",
    output="local",
    file_name="driver_data",
)
```
```python
df.get_data()
```

```output
>>> Connection to snowflake established Successfully.
>>> File saved to your 'local' file system with name 'snowflake_TPCH_SF1_SNOWFLAKE_SAMPLE_DATA_driver_data_2022_04_20_08_46_38.csv' Successfully.
```
You can explore the Connectors examples [here](https://github.com/katonic-dev/Examples/tree/master/katonic-sdk/connectors).

### Filemanager

Once getting the data you can use Katonic Filemanager to Get, Store and Update or manipulate Objects within the file manager with Katonic SDK.

### Install Filemanager.
```python
pip install katonic[filemanager]
```
### Filemanager example to put/move the object from filemanager's public bucket to private bucket.

*filemanager-credentials.json*

```json
{
    "ACCESS_KEY":"TV6WFGHTR3TFBIBAO0R",
    "SECRET_KEY":"BoW+p+iLAMNS4cbUNsSLVEmscITdTDMLXC8Emfz",
    "PRIVATE_BUCKET":"private-storage-6583",
    "PUBLIC_BUCKET":"shared-storage",
}
```
```python
# Define all your configurations inside a JSON file.
import json

with open('filemanager-credentials.json') as f:
    config = json.load(f)
```
Initializing the Filemanager with the provided credentials and configuration.
```python
from katonic.filemanager.session import Filemanager

fm = Filemanager(
    access_key=config["ACCESS_KEY"],
    secret_key=config["SECRET_KEY"],
)

client = fm.clientV1
```
```python
client.fput_object(
    config["BUCKET"],
    "/home/data/sample-file.txt",
    "/data/sample-file.txt"
)
```
You can explore the Filemanager examples [here](https://github.com/katonic-dev/Examples/tree/master/katonic-sdk/filemanager).

### Feature Store

Once you loaded all the necessary data that you want to work with. You'll do the preprocessing of it. Which consists of Handling the missing values, Removing the Outliers, Scaling the Data and Encoding the features etc. Once you've finished preprocessing the data. You need to ingest the data into a Feature store.

By uploading the clean data to a feature store, you can share it across the organization. So that other teams and data scientist working on the same problem can make use of it. By this way you can achieve Feature Reusability.

Training models and making predictions from the Feature store data will improve the consistency between the training data and serving data otherwise it will lead to training-serving skew.

### Install Feature Store.
```python
pip install katonic[fs]
```

You can explore the feature store examples [here](https://github.com/katonic-dev/Examples/tree/master/katonic-sdk/feature-store).

### Experiment Operations

Training Machine Learning models just with one or two lines of code, can be done by the Auto ML component inside the Katonic SDK.

Even all the metrics for Classification and Regression will get catalouged using SDK. Available Metrices are Accuracy score, F-1 score, Precison, Recall, Log loss, Mean Squared Error, Mean Absolute Error and Root Mean Squared Error.

### Install Auto ML.
```python
pip install katonic[ml]
```
### Auto ML Examples.
```python
from katonic.ml.client import set_exp
from katonic.ml.classification import Classifier

# Creating a new experiment using set_exp function from ml client.
exp_name = "customer_churn_prediction"
set_exp(exp_name)

clf = Classifier(X_train,X_test,y_train,y_test, exp_name)

clf.GradientBoostingClassifier()
clf.DecisionTreeClassifier(max_depth=8, criterion="gini")

# Get registered models and metrics in Mlflow
df_runs = clf.search_runs(exp_id)
print("Number of runs done : ", len(df_runs))
```

You can explore the automl examples [here](https://github.com/katonic-dev/Examples/tree/master/katonic-sdk/automl).

### Registry Operations

Once you finished training the models with your data. Katonic's SDK will keep track of all the models and store the Model metadata and metrices inside the Experiment Registry. From there you can choose the best model and send it into Model Registy.

### Install Log.
```python
pip install katonic
```
### Logging ML Model Examples.
```python
from katonic.log.logmodel import LogModel

from xgboost import XGBClassifier

# Creating a new experiment using set_exp function from log client.
exp_name = "diabetes_prediction"
lm = LogModel(exp_name)

clf = XGBClassifier(random_state=0)
clf.fit(X_train, y_train)

artifact_path = # define custom artifact path name (str)
model_mertics = # define custom metric in dictionary form

# Logging ML model
lm.model_logging(
    model_name="xgboost",
    model_type="xgboost",
    model=clf,
    artifact_path=artifact_path,
    current_working_dir="xgboost_model.ipynb",
    metrics=model_mertics
)
```

You can explore the logs examples [here](https://github.com/katonic-dev/Examples/tree/master/katonic-sdk/log).

In Model Registy you can store the Best models according to your performance Metrices. By using the model registy you can tag the models with `staging` or `production`. The models that are with the tag `production` can be Deployed to the production and the models with `staging` tag can get a review check from the QA team and get to the further stages.

### Pipeline Operations

No Data Scientist want to do the same thing again and again, instead of that Data Scientist want to use the previous work that he had done for the future purposes. We can do the same thing inside an AI Model Life Cycle.

We can convert all the work that we had done till now into a Scalable Pipeline. For that you can use the Pipelines component inside the Katonic SDK. If you want to perform the same operations with the different data, you just need to change the data source and run the pipeline. Every thing will get done automatically in a scalable manner.

### Install Pipelines.
```python
pip install katonic[pipeline]
```
## How to create and execute a pipeline using Katonic SDK.

* Create a pipeline function

* create a pipeline by defining task inside a pipeline function
```python
from katonic.pipeline.pipeline import dsl, create_component_from_func

def print_something(data: str):
    print(data)

@dsl.pipeline(
    name='Print Something',
    description='A pipeline that prints some data'
)
def pipeline():
    print_something_op = create_component_from_func(func=print_something)
    data = "Hello World!!"
    print_something_op(data)
```
create_component_from_func is used to convert functions to components that is stored inside print_something, data is passed inside print_something_op to print it.

Compiling And Running: Here pipeline experiment name, function is defined.
```python
from datetime import datetime
import uuid

EXPERIMENT_NAME = "Print_Something"
pipeline_func = pipeline
```
using the pipeline funcion and yaml filename the pipeline is compiled that generated the .yaml file.

kfp.compiler.Compiler.compile() compiles your Python DSL code into a single static configuration (in YAML format) that the Kubeflow Pipelines service can process.

```python
from katonic.pipeline.pipeline import compiler
pipeline_filename = pipeline_func.__name__ + f'{uuid.uuid1()}.pipeline.yaml'
compiler.Compiler().compile(pipeline_func, pipeline_filename)
```
The pipeline is uploaded using the kfp.client() that contains all the pipeline details.

```python
from katonic.pipeline.pipeline import Client

client = Client()
experiment = client.create_experiment(EXPERIMENT_NAME)
run_name = pipeline_func.__name__ + str(datetime.now().strftime("%d-%m-%Y-%H-%M-%S"))
client.upload_pipeline(pipeline_filename)
run_result = client.run_pipeline(experiment.id, run_name, pipeline_filename)
```

You can explore the pipeline examples [here](https://github.com/katonic-dev/Examples/tree/master/katonic-sdk/pipeline).

### Drift

An AI model life cycle will not end with the model deployment. You need to monitor the model's performance continuously in order to detect the model detoriation or model degradation. Drift component from Katonic's SDK will help you to find the Drift inside your data. It will perform certain statistical analysis upon the data in order to check if the upcoming data has any Outliers or the data is abnormal it will let you know through a Visual representaion.

### Install Drift.
```python
pip install katonic[drift]
```

You can explore the drift examples [here](https://github.com/katonic-dev/Examples/tree/master/katonic-sdk/drift).
