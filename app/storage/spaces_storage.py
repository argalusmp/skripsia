import boto3
import os
from botocore.client import Config
from app.config import settings


class SpacesStorage:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            region_name=settings.DO_SPACE_REGION,
            endpoint_url=settings.DO_SPACE_ENDPOINT,
            aws_access_key_id=settings.DO_SPACE_KEY,
            aws_secret_access_key=settings.DO_SPACE_SECRET,
            config=Config(signature_version='s3v4')
        )
        self.bucket = settings.DO_SPACE_NAME

    def upload_file(self, file_path, object_name=None):
        """Upload a file to a Space"""
        if object_name is None:
            object_name = os.path.basename(file_path)

        try:
            self.s3.upload_file(
                file_path,
                self.bucket,
                object_name,
                ExtraArgs={'ACL': 'public-read'})
            # Generate a URL that will be valid for 1 hour
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': object_name},
                ExpiresIn=3600
            )
            return object_name
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None

    def download_file(self, object_name, file_path):
        """Download a file from a Space"""
        try:
            self.s3.download_file(self.bucket, object_name, file_path)
            return True
        except Exception as e:
            print(f"Error downloading file: {e}")
            return False

    def delete_file(self, object_name):
        """Delete a file from a Space"""
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=object_name)
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

    def get_presigned_url(self, object_name, expires_in=3600):
        """Generate a presigned URL for an object"""
        try:
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': object_name},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            print(f"Error generating presigned URL: {e}")
            return None
