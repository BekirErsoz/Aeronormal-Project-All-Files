import boto3
from botocore.exceptions import NoCredentialsError

S3 = boto3.client('s3')

def upload_to_s3(file_name, bucket, object_name=None):
    try:
        S3.upload_file(file_name, bucket, object_name or file_name)
        print(f"{file_name} has been uploaded to {bucket}")
    except NoCredentialsError:
        print("Credentials not available")