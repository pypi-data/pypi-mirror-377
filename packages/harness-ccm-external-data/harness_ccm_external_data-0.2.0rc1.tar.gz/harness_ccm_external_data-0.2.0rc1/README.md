# harness-ccm-external-data

![PyPI - Version](https://img.shields.io/pypi/v/harness_ccm_external_data)
![Docker Image Version](https://img.shields.io/docker/v/harnesscommunity/harness-ccm-external-data)

tools to help manage ingesting external data in harness ccm

the project is split into several parts:
- creating raw data
- converting external data formats to a compatible format for harness (focus)
- uploading the converted data to the harness platform

## loading data

when loading in a billing export we can apply a few modifications of the data to prepare it for ingestion into harness.

first, we convert any non-focus fields to their focus equivalent. this is done by providing a map of focus fields to their corresponding non-focus fields.

```python
mapping = {
    "BillingAccountId": "Organization ID",
    "BillingAccountName": "Organization Name",
    ...
}
```

if only a subset of fields need remapping you can specify only those which need changed.

next we create a `Focus` object, specifying the platform, local billing export file, field mappings (if needed) and any data modifications needed:

```python
from harness_ccm_external_data import Focus

my_data = Focus(
    # name of the provider where the billing data came from
    provider="CloudABC",
    # name of this particular data source from the above provider
    data_source="ABC Payer Account 1",
    # csv with focus data
    filename="abc_billing_export.csv",
    # focus to non focus mappings (if they exist)
    mapping={
        "BillingAccountId": "Organization ID",
        "BillingAccountName": "Organization Name",
        ...
    },
    # skip the first n rows of the billing data
    skip_rows=100,
    # you can also specify specific rows to skip
    # skip_rows=[0, 2, 4, 6, 8],
    # apply a multiplier to the cost (account for discounts not shown in the export?)
    cost_multiplier=0.95
    # if the csv is in a non-standard format
    separator=";"
    # apply a function to any column value
    converters={
        "ChargeCategory": lambda x: lower(x)
    },
    # fill in missing required fields with static data if needed
    additional_columns={
        "ConsumedQuantity": 1,
    },
    # for data upload to harness
    harness_account_id=getenv("HARNESS_ACCOUNT_ID"),
    harness_platform_api_key=getenv("HARNESS_PLATFORM_API_KEY"),
)
```

now we can render the data to the harness platform format to be uploaded by hand in the UI:

```
my_data.render_file("harness_focus_my_billing_export.csv")
```

### building data

you can also build cost data on the fly by building a dataframe and passing that to the constructor:

```python
from harness_ccm_external_data import Focus

data = [
    [
        1234567890123,
        "SunBird",
        "2025-6-01 00:00:00",
        "2025-5-01 00:00:00",
        "Usage",
        "2024-09-18 22:00:00",
        "2024-09-18 23:00:00",
        2.0,
        0.0,
        "AWS",
        "arn:ats:sqs:us-test-2:347410479675:mibelllmel-i-032l64f2065481b12",
        "US West (Oregon)",
        "Amazon Simple Queue Service",
        51738928782,
        "G95FST5FTYV3JSRX",
        "Atlas Nimbus",
    ],
    [
        1234567890124,
        "SunBird2",
        "2025-6-01 00:00:00",
        "2025-5-01 00:00:00",
        "Usage",
        "2024-09-30 22:00:00",
        "2024-09-30 23:00:00",
        0.00200749,
        0.0,
        "AWS",
        "arn:ats:emastilmoalfamanling:us-test-2:586597448978:moalfamanler/app/tungsten-lonbmuenle-amf/l365455f461l4e4a",
        "US West (Oregon)",
        "Elastic Load Balancing",
        43883916739,
        "2ETY8Y426S4237JU",
        "Zenith Eclipse",
        '{"application": "BrightLensMatrix", "environment": "dev", "business_unit": "ViennaAI"}',
    ],
]

my_data = Focus(
    provider="CloudABC",
    data_source="ABC Payer Account 1",
    source=Focus.create_dataset(data),
)
```

the data defined should have the harness focus feilds as defined in [HARNESS_FIELDS](https://github.com/harness-community/harness-ccm-external-data/blob/main/src/harness_ccm_external_data/focus_data.py#L9-L27)

## uploading data

uploading the data to harness is as simple as executing the upload function, there is no need to render the data to a file before doing so:

```python
my_data.upload()
```

this will auto-detect the invoice period from the data, upload it, and trigger ingestion

## docker

there is a docker image available to enable running the automation via docker or a plugin in a harness pipeline:

```
docker run --rm -it \
  -v ${PWD}/focus_sample.csv:/focus_sample.csv \
  -v ${PWD}:/output \
  -e CSV_FILE=/focus_sample.csv \
  -e PROVIDER=CloudABC \
  -e DATA_SOURCE="ABC Payer Account 1" \
  -e RENDER_FILE=/output/docker_focus.csv # optional \
  -e UPLOAD=true # optional \
  harnesscommunity/harness-ccm-external-data
```

### drone plugin

the container can also be used as a drone/harness plugin:

```yaml
- step:
    type: Plugin
    name: upload
    identifier: upload
    spec:
        connectorRef: account.buildfarm_container_registry_cloud
        image: harnesscommunity/harness-ccm-external-data
        settings:
            PROVIDER: CloudABC
            DATA_SOURCE: ABC Payer Account 1
            CSV_FILE: /harness/focus_sample.csv
            HARNESS_ACCOUNT_ID: <+account.identifier>
            HARNESS_PLATFORM_API_KEY: <+secrets.getValue("account.account_admin")>
            UPLOAD: "true" # optional
            RENDER_FILE: /harness/harness_focus_sample.csv # optional
```

## modules

there are patterns provided for extracting, transforming, and loading external data into harness under the `modules` folder:

- aws: s3+lambda function

### data loading settings

- `RENDER_FILE`: file path to render harness-focus data to
- `PROVIDER`: 
- `CSV_FILE`: 
- `MAPPING`: 
- `SKIP_ROWS`: 
- `COST_MULTIPLIER`: 
- `VALIDATE`: 

## development

pull the example focus csv: `curl -LO https://raw.githubusercontent.com/FinOps-Open-Cost-and-Usage-Spec/FOCUS-Sample-Data/refs/heads/main/FOCUS-1.0/focus_sample.csv`

install [poetry](https://python-poetry.org/docs/#installation)

testing: `make test`

## built-in focus conversions

users may contribute a platform-specific subclass of the focus object to handle special cases in their billing exports.

### mongodb atlas

```python
from harness_ccm_external_data import MongoDBAtlas

atlas = MongoDBAtlas(
    "MongoDB Atlas",
    "My Company Inc.",
    "usage-summary-8765434567887656789-20250201.csv",
    harness_account_id=getenv("HARNESS_ACCOUNT_ID"),
    harness_platform_api_key=getenv("HARNESS_PLATFORM_API_KEY"),
)
atlas.upload()
```
