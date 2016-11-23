import cloudstorage as gcs
import uuid

import settings

def uploadBillImageToStaging(file_data):
    filename = file_data.filename
    bucket_name = settings.STAGING_FILE_BUCKET
    file_type = file_data.type
    data = file_data.value

    staging_filepath= '/' + bucket_name + '/' + str(uuid.uuid4()) + '/' + filename
    write_retry_params = gcs.RetryParams(backoff_factor=1.1)
    gcs_file = gcs.open(
        staging_filepath,
        'w',
        content_type=file_type,
        options={},
        retry_params=write_retry_params
        )
    gcs_file.write(data)
    gcs_file.close()

    return staging_filepath
