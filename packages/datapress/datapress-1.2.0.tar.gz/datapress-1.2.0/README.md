# DataPress Python Client

A Python client library for interacting with the [DataPress API](https://datapress.com/docs/api).

## Installation

```bash
pip install datapress
```

## How to Use

Set your API credentials as environment variables:

```bash
export DATAPRESS_API_KEY="your-api-key"
export DATAPRESS_URL="https://your-datapress-instance.com"
```

### Basic Usage

```python
from datapress import DataPressClient

# Initialize client
client = DataPressClient()

# Verify authentication
user_info = client.whoami()
print(f"Logged in as: {user_info['title']}")

# Get a dataset
dataset = client.get_dataset("ab12x")
print(f"Dataset: {dataset['title']}")
```

### Renaming a Dataset

```python
# Rename a dataset using patch operations
patch = [{"op": "replace", "path": "/title", "value": "New Dataset Name"}]
result = client.patch_dataset("ab12x", patch)
print(f"Dataset renamed to: {result['dataset']['title']}")
```

### Adding a File

```python
# Upload a new file to a dataset
result = client.upload_file(
    dataset_id="ab12x",
    file_path="data/sales.csv",
    # Optional parameters:
    title="Sales Data",
    description="Monthly sales figures",
    order=1,
    timeframe={"from": "2024-01", "to": "2025-04"}
)
print(f"File uploaded with ID: {result['resource_id']}")
```

### Replacing a File

```python
# Replace an existing file
result = client.upload_file(
    dataset_id="ab12x",
    file_path="data/updated_spending.csv",
    # Optional parameters:
    resource_id="xyz",  # ID of existing file to replace
    title="Updated Spending Data"
)
print(f"File replaced: {result['resource_id']}")
```

### Uploading a File from S3

You can transfer a file from S3 to a dataset by passing your `boto3.client` instance to the `upload_file_from_s3` method.  This will download the file in 5MB chunks and incrementally upload it to the dataset.

```python
import boto3

session = boto3.session.Session()
s3_client = session.client(
    "s3",
    # ... credentials, endpoints, regions etc
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

# Upload a file from S3 to a dataset
result = client.upload_file_from_s3(
    s3_client=s3_client,
    bucket="your-bucket-name",
    key="your-object-key",
    dataset_id="ab12x",
    # Optional parameters:
    resource_id="xyz",  # ID of existing file to replace
    title="Updated Spending Data",
    description="Monthly spending figures",
    order=1,
    timeframe={"from": "2024-01", "to": "2025-04"}
)
print(f"File uploaded from S3: {result['resource_id']}")
```