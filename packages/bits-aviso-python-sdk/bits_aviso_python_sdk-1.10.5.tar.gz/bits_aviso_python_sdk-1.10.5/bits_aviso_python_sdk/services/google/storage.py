"""
This module provides a class to interact with Google Cloud Storage.
If no service account credentials are provided, the SDK will attempt to use the default credentials.

## Usage
The following are examples of how to use the Storage class:

### Upload a file to Google Cloud Storage
```python
from bits_aviso_python_sdk.services.google.storage import Storage

# initialize Storage client
storage_client = Storage()

# file to upload
file_to_upload = "path/to/your/file.txt"

# upload a file
storage_client.upload("your_bucket_name", "prefix", "file.txt", file_to_upload)
```

### Get the total size of a bucket (in bytes)
```python
from bits_aviso_python_sdk.services.google.storage import Storage

# initialize Storage client
storage_client = Storage()

# get the total size of a bucket in bytes
bucket_size_bytes = storage_client.get_bucket_size("your_bucket_name")
print(f"Bucket size: {bucket_size_bytes} bytes")
```

The `get_bucket_size` method uses Google Cloud Monitoring (MQL via REST API) to fetch the latest total size of the specified bucket in bytes. It returns 0 if no data is found or if there is an error. All errors are logged and raised as `ValueError`.

---
"""
import google.auth
import google.auth.exceptions
import io
import json
import logging
import requests
from google.api_core import exceptions, retry
from google.cloud import storage, exceptions
from google.auth.transport.requests import Request
from bits_aviso_python_sdk.helpers.bigquery import parse_to_nldjson
from bits_aviso_python_sdk.services.google import authenticate_google_service_account


class Storage:
    def __init__(self, service_account_credentials=None, project_id=None):
        """
        Initialize the Storage class for interacting with Google Cloud Storage.

        Args:
            service_account_credentials (dict or str, optional): Service account credentials as a dict or path to the credentials file. If not provided, uses default credentials.
            project_id (str, optional): The project ID to use. If not provided, uses the default project.
        """
        if service_account_credentials:
            credentials = authenticate_google_service_account(
                service_account_credentials)
            if project_id:
                self.client = storage.Client(
                    credentials=credentials, project=project_id)
            else:
                self.client = storage.Client(credentials=credentials)
        else:
            try:
                if project_id:
                    self.client = storage.Client(project=project_id)
                else:
                    self.client = storage.Client()
            except google.auth.exceptions.DefaultCredentialsError as e:
                logging.error(f"Unable to authenticate service account. {e}")
                self.client = None

    def download_blob_to_file(self, bucket_name, blob_name, file_path, prefix=None):
        """
        Download a blob from a bucket to a local file.

        Args:
            bucket_name (str): The name of the bucket.
            blob_name (str): The name of the blob.
            file_path (str): The path to save the downloaded file.
            prefix (str, optional): The prefix (folder) for the blob. Defaults to None.

        Returns:
            str: The path to the downloaded file.

        Raises:
            ValueError: If the blob is not found in the bucket.
        """
        try:
            # get the blob
            blob = self.get_blob(bucket_name, blob_name, prefix)
            # download the blob to the file
            logging.info(
                f"Downloading [{blob_name}] from {bucket_name} to [{file_path}]...")
            blob.download_to_filename(file_path)
            logging.info(
                f"Downloaded [{blob_name}] from {bucket_name} to [{file_path}].")

            return file_path

        except exceptions.NotFound:
            message = f"Blob [{blob_name}] not found in {bucket_name}."
            logging.error(message)

            raise ValueError(message)

    @staticmethod
    def create_blob(bucket, prefix, blob_name):
        """Creates a blob in the specified bucket.

        Args:
            bucket (google.cloud.storage.bucket.Bucket): The bucket to create the blob in.
            prefix (string): The prefix to use for the blob. Typically, this is the name of the folder.
            blob_name (string): The name of the blob.

        Returns:
            google.cloud.storage.blob.Blob: The created blob.

        Raises:
            ValueError: If the bucket is not found.
        """
        try:
            # create the blob
            logging.info(
                f"Creating blob {prefix}/{blob_name} in bucket {bucket}...")
            blob = bucket.blob(f"{prefix}/{blob_name}")
            logging.info(
                f"Created blob {prefix}/{blob_name} in bucket {bucket}.")

            return blob  # return the blob

        except exceptions.NotFound:
            message = f"Bucket {bucket} not found. Cannot proceed with creating blob {prefix}/{blob_name}."
            logging.error(message)

            raise ValueError(message)

    def get_blob(self, bucket_name, blob_name, prefix=None):
        """
        Retrieve a blob object from a bucket.

        Args:
            bucket_name (str): The name of the bucket.
            blob_name (str): The name of the blob (file).
            prefix (str, optional): The prefix (folder) for the blob. Defaults to None.

        Returns:
            google.cloud.storage.blob.Blob: The blob object.

        Raises:
            ValueError: If the blob is not found in the bucket.
        """
        # check if the prefix is provided
        if prefix:
            if prefix.endswith("/"):
                blob_name = f"{prefix}{blob_name}"
            else:
                blob_name = f"{prefix}/{blob_name}"

        try:
            # get the bucket
            bucket = self.get_bucket(bucket_name)
            # get the blob from the bucket
            logging.info(f"Retrieving blob {blob_name} from {bucket_name}...")
            blob = bucket.blob(f"{blob_name}")

            return blob

        except exceptions.NotFound:
            message = f"Blob {blob_name} not found in {bucket_name}."
            logging.error(message)

            raise ValueError(message)

    def get_blob_dict(self, bucket_name, blob_name, prefix=None):
        """
        Get metadata for a blob as a dictionary.

        Args:
            bucket_name (str): The name of the bucket.
            blob_name (str): The name of the blob.
            prefix (str, optional): The prefix (folder) for the blob. Defaults to None.

        Returns:
            dict: Metadata for the specified blob.
        """
        # get the blob
        blob = self.get_blob(bucket_name, blob_name, prefix)
        # parse the data for the blob
        blob_data = {
            "id": blob.id,
            "name": blob.name,
            "bucket": blob.bucket.name,
            "cache_control": blob.cache_control,
            "chunk_size": blob.chunk_size,
            "client": blob.client,
            "component_count": blob.component_count,
            "content_disposition": blob.content_disposition,
            "content_encoding": blob.content_encoding,
            "content_language": blob.content_language,
            "content_type": blob.content_type,
            "crc32c": blob.crc32c,
            "custom_time": blob.custom_time,
            "etag": blob.etag,
            "event_based_hold": blob.event_based_hold,
            "generation": blob.generation,
            "hard_delete_time": blob.hard_delete_time,
            "md5_hash": blob.md5_hash,
            "media_link": blob.media_link,
            "metadata": blob.metadata,
            "metageneration": blob.metageneration,
            "owner": blob.owner,
            "path": blob.path,
            "public_url": blob.public_url,
            "retention_mode": blob.retention,
            "retention_expiration_time": blob.retention_expiration_time,
            "self_link": blob.self_link,
            "size": blob.size,
            "soft_delete_time": blob.soft_delete_time,
            "storage_class": blob.storage_class,
            "temporary_hold": blob.temporary_hold,
            "time_created": blob.time_created,
            "time_deleted": blob.time_deleted,
            "updated": blob.updated,
            "user_project": blob.user_project
        }

        return blob_data

    def get_bucket(self, bucket_name):
        """
        Retrieve a bucket object by name.

        Args:
            bucket_name (str): The name of the bucket.

        Returns:
            google.cloud.storage.bucket.Bucket: The bucket object.

        Raises:
            ValueError: If the bucket is not found.
        """
        if not self.client:
            message = "Storage client is not initialized."
            logging.error(message)
            raise ValueError(message)
        try:
            # get_bucket the bucket
            logging.info(f"Retrieving bucket {bucket_name}...")
            bucket = self.client.get_bucket(bucket_name)
            logging.info(f"Retrieved bucket {bucket_name}.")

            return bucket

        except exceptions.NotFound:
            message = f"Bucket {bucket_name} not found."
            logging.error(message)

            raise ValueError(message)

    def get_bucket_dict(self, bucket_name=None, bucket_obj=None):
        """
        Get metadata for a bucket as a dictionary.

        Args:
            bucket_name (str, optional): The name of the bucket. Defaults to None.
            bucket_obj (google.cloud.storage.bucket.Bucket, optional): The bucket object. Defaults to None.

        Returns:
            dict: Metadata for the specified bucket.
        """
        # check if the bucket object is provided
        if bucket_obj:
            bucket = bucket_obj

        elif bucket_name:
            bucket = self.get_bucket(bucket_name)

        else:
            message = "No bucket name or object provided."
            logging.error(message)
            raise ValueError(message)

        # parse the data for the bucket
        bucket_data = {
            "id": bucket.id,
            "name": bucket.name,
            "cors": bucket.cors,
            "etag": bucket.etag,
            "labels": bucket.labels,
            "lifecycle_rules": bucket.lifecycle_rules,
            "location": bucket.location,
            "location_type": bucket.location_type,
            "metageneration": bucket.metageneration,
            "object_retention_mode": bucket.object_retention_mode,
            "owner": bucket.owner,
            "path": bucket.path,
            "project_number": bucket.project_number,
            "requester_pays": bucket.requester_pays,
            "retention_period": bucket.retention_period,
            "retention_policy_effective_time": bucket.retention_policy_effective_time,
            "retention_policy_locked": bucket.retention_policy_locked,
            "self_link": bucket.self_link,
            "soft_delete_policy": bucket.soft_delete_policy,
            "size": self.get_bucket_size(bucket),
            "storage_class": bucket.storage_class,
            "time_created": bucket.time_created,
            "updated": bucket.updated,
            "user_project": bucket.user_project,
            "versioning_enabled": bucket.versioning_enabled
        }

        return bucket_data

    def get_bucket_size(self, bucket):
        """
        Get the total size of a bucket in bytes using Cloud Monitoring (MQL via REST API).

        Args:
            bucket (str or google.cloud.storage.bucket.Bucket): The bucket name as a string, or a Bucket object.

        Returns:
            int: The total size of the bucket in bytes. Returns 0 if no data is found.

        Raises:
            ValueError: If the storage client is not initialized, or if there is an error querying or parsing the Monitoring API response.
        """
        if isinstance(bucket, str):
            bucket_name = bucket
        else:
            bucket_name = bucket.name

        if not self.client or not hasattr(self.client, "project"):
            raise ValueError("Storage client is not initialized or missing project attribute.")
        project = self.client.project

        # Get credentials and access token
        credentials, _ = google.auth.default(scopes=[
            "https://www.googleapis.com/auth/cloud-platform"
        ])
        credentials.refresh(Request())
        access_token = credentials.token

        url = f"https://monitoring.googleapis.com/v3/projects/{project}/timeSeries:query"

        mql_query = f"""
            fetch gcs_bucket
            | metric 'storage.googleapis.com/storage/total_bytes'
            | filter resource.bucket_name == '{bucket_name}'
            | within 1d
            | group_by [], [max_total_bytes: max(value.total_bytes)]
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        body = {"query": mql_query}

        try:
            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()

        except requests.HTTPError as http_err:
            logging.error(f"HTTP error when querying Monitoring API for bucket {bucket_name}: {http_err} | Response: {getattr(http_err.response, 'text', None)}")
            raise ValueError(f"Failed to fetch bucket size for {bucket_name}: {http_err}")
        except Exception as req_err:
            logging.error(f"Unexpected error when querying Monitoring API for bucket {bucket_name}: {req_err}")
            raise ValueError(f"Failed to fetch bucket size for {bucket_name}: {req_err}")

        try:
            data = response.json()

        except Exception as json_err:
            logging.error(f"Failed to parse Monitoring API response for bucket {bucket_name}: {json_err}")
            raise ValueError(f"Failed to parse Monitoring API response for {bucket_name}: {json_err}")

        try:
            latest = None
            latest_time = None
            for ts in data.get("timeSeriesData", []):
                for point in ts.get("pointData", []):
                    values = point.get("values", [])
                    if values:
                        v = values[0]
                        val = v.get("int64Value")
                        if val is None:
                            val = v.get("doubleValue")
                        t = point.get("timeInterval", {}).get("endTime")
                        if val is not None and (latest_time is None or t > latest_time):
                            latest = val
                            latest_time = t
            if latest is not None:
                return int(float(latest))
            logging.warning(f"No bucket size data found for {bucket_name} in Monitoring API response.")
            return 0

        except Exception as parse_err:
            logging.error(f"Error parsing MQL response for bucket {bucket_name}: {parse_err}")
            raise ValueError(f"Failed to parse bucket size for {bucket_name}: {parse_err}")

    def list_blobs(self, bucket_name, prefix=None, delimiter=None):
        """
        List all blobs in a bucket, optionally filtering by prefix and delimiter.

        Args:
            bucket_name (str): The name of the bucket.
            prefix (str, optional): The prefix (folder) to filter blobs. Defaults to None.
            delimiter (str, optional): The delimiter to restrict results. Defaults to None.

        Returns:
            list: List of blob objects in the bucket.
        """
        # list the blobs in the bucket
        logging.info(
            f"Listing blobs in [{bucket_name}] with prefix [{prefix}] and delimeter [{delimiter}]...")
        if not self.client:
            message = "Storage client is not initialized."
            logging.error(message)
            raise ValueError(message)
        return list(self.client.list_blobs(bucket_name, prefix=prefix, delimiter=delimiter))

    def list_blobs_dict(self, bucket_name, prefix=None, delimiter=None):
        """
        List all blobs in a bucket and return their metadata as dictionaries.

        Args:
            bucket_name (str): The name of the bucket.
            prefix (str, optional): The prefix (folder) to filter blobs. Defaults to None.
            delimiter (str, optional): The delimiter to restrict results. Defaults to None.

        Returns:
            list: List of dictionaries representing the blobs in the bucket.
        """
        logging.info(
            f"Getting blob dict data in [{bucket_name}] with prefix [{prefix}] and delimeter [{delimiter}]...")
        blobs = self.list_blobs(
            bucket_name, prefix=prefix, delimiter=delimiter)
        blobs_dict = []
        for b in blobs:
            blobs_dict.append(self.get_blob_dict(bucket_name, b.name, prefix))

        logging.info(f"Finished getting blob dict data in [{bucket_name}].")
        return blobs_dict

    def list_buckets(self):
        """
        List all buckets in the project.

        Returns:
            list: List of bucket objects in the project.
        """
        logging.info("Getting all bucket objects...")
        if not self.client:
            message = "Storage client is not initialized."
            logging.error(message)
            raise ValueError(message)
        return list(self.client.list_buckets())

    def list_buckets_dict(self):
        """
        List all buckets in the project and return their metadata as dictionaries.

        Returns:
            list: List of dictionaries representing the buckets in the project.
        """
        logging.info("Getting all bucket dict data...")
        if not self.client:
            message = "Storage client is not initialized."
            logging.error(message)
            raise ValueError(message)
        buckets = self.client.list_buckets()
        buckets_dict = []
        for b in buckets:
            buckets_dict.append(self.get_bucket_dict(b.name, bucket_obj=b))

        logging.info("Finished getting all bucket dict data.")
        return buckets_dict

    def update_bucket_labels(self, bucket_name, labels, append=True):
        """
        Update the labels for a bucket.

        Args:
            bucket_name (str): The name of the bucket.
            labels (dict): The labels to update the bucket with.
            append (bool, optional): If True, append to existing labels; if False, replace them. Defaults to True.

        Returns:
            google.cloud.storage.bucket.Bucket: The updated bucket object.

        Raises:
            ValueError: If the bucket is not found or if there is an error updating the labels.
        """
        try:
            # get the bucket
            bucket = self.get_bucket(bucket_name)
            # check for existing labels
            existing_labels = bucket.labels or {}

            # check if the labels are valid
            if not isinstance(labels, dict):
                message = "Labels must be a dictionary."
                logging.error(message)
                raise ValueError(message)

            # check if the labels are empty
            if not labels:
                message = "No labels provided to update."
                logging.error(message)
                raise ValueError(message)

            # check whether to append or replace the labels
            if append:
                # append the new labels to the existing labels
                logging.info(
                    f"Appending new labels to existing labels for bucket {bucket_name}...")
                labels = {**existing_labels, **labels}

            # update the labels
            logging.info(f"Updating labels for bucket {bucket_name}...")
            bucket.labels = labels
            bucket.patch()  # apply the changes
            logging.info(f"Updated labels for bucket {bucket_name}.")

            return bucket

        except exceptions.NotFound:
            message = f"Bucket {bucket_name} not found."
            logging.error(message)

            raise ValueError(message)

        except exceptions.GoogleCloudError as e:
            message = f"Error updating labels for bucket {bucket_name}: {e}"
            logging.error(message)

            raise ValueError(message)

    def upload(self, bucket_name, prefix, blob_name, data, content_type='application/json', nldjson=False):
        """
        Upload data to a bucket as a blob.

        Args:
            bucket_name (str): The name of the bucket.
            prefix (str): The prefix (folder) for the blob.
            blob_name (str): The name of the blob.
            data (str, dict, list): The data to upload.
            content_type (str, optional): The content type of the data. Defaults to 'application/json'.
            nldjson (bool, optional): If True, convert data to newline-delimited JSON. Defaults to False.

        Raises:
            TypeError: If the data cannot be converted to newline-delimited JSON.
            ValueError: If the data cannot be uploaded to the bucket.
        """
        try:
            # get_bucket the bucket
            bucket = self.get_bucket(bucket_name)
            # create the blob
            blob = self.create_blob(bucket, prefix, blob_name)
            # set chunk size for resumable uploads
            blob.chunk_size = 5 * 1024 * 1024  # 5 MB
            # set retry policy
            retry_policy = retry.Retry()

            # check if the data needs to be converted to newline delimited json
            if nldjson:
                try:
                    data = parse_to_nldjson(data)

                except TypeError as e:  # data is not a dictionary or a list of dictionaries, probably already converted
                    raise ValueError(
                        f"Unable to convert data to newline delimited json. {e}")

            # check if the data is a string, if not convert it to string
            if isinstance(data, dict) or isinstance(data, list):
                data = json.dumps(data)

            # convert string to bytes stream
            stream = io.BytesIO(data.encode("utf-8"))

            # upload the data
            logging.info(f"Uploading {prefix}/{blob_name} to {bucket_name}...")
            blob.upload_from_file(stream, retry=retry_policy,
                                  content_type=content_type, timeout=120)
            logging.info(f"Uploaded {prefix}/{blob_name} to {bucket_name}.")

        except (ValueError, AttributeError) as e:
            message = f"Unable to upload {blob_name} to {bucket_name}. {e}"
            logging.error(message)

            raise ValueError(message)  # raise an error with the message
