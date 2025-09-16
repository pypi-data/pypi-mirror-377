import os
from bits_aviso_python_sdk.helpers import initialize_logger
from bits_aviso_python_sdk.services.google.storage import Storage


def test():
    """Tests the Pubsub class."""
    logger = initialize_logger()
    #os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ.get("ARCHIVE_ACCESSOR")

    s = Storage(project_id='')
    bucket = s.list_buckets()[0]
    size = s.get_bucket_size(bucket.name)

    print(bucket.name, size)


if __name__ == '__main__':
    test()
