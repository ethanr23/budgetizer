import boto3
from botocore.exceptions import ClientError

class S3Client:
    def __init__(self, bucket_name, region_name=None):
        self.bucket_name = bucket_name
        self.s3 = boto3.client('s3', region_name=region_name)

    def upload_file(self, file_path, object_name=None):
        if object_name is None:
            object_name = file_path
        try:
            self.s3.upload_file(file_path, self.bucket_name, object_name)
            return True
        except ClientError as e:
            print(f"Upload failed: {e}")
            return False

    def download_file(self, object_name, file_path):
        try:
            self.s3.download_file(self.bucket_name, object_name, file_path)
            return True
        except ClientError as e:
            print(f"Download failed: {e}")
            return False

    def list_objects(self, prefix=''):
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            return [obj['Key'] for obj in response.get('Contents', [])]
        except ClientError as e:
            print(f"List objects failed: {e}")
            return []

    def delete_object(self, object_name):
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=object_name)
            return True
        except ClientError as e:
            print(f"Delete failed: {e}")
            return False