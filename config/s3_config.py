import os

import boto3
from dotenv import load_dotenv

load_dotenv()


def s3_client_connection():
    try:
        # s3 클라이언트 생성
        s3 = boto3.client(
            service_name="s3",
            region_name="ap-northeast-2",
            aws_access_key_id=os.environ.get("S3_USER_ACCESS_KEY"),
            aws_secret_access_key=os.environ.get("S3_USER_SECRET_KEY"),
        )
    except Exception as e:
        print(e)
    else:
        print("s3 bucket connected!")
        return s3


def s3_bucket():
    s3 = boto3.resource(
        "s3",
        aws_access_key_id=os.environ.get("S3_USER_ACCESS_KEY"),
        aws_secret_access_key=os.environ.get("S3_USER_SECRET_KEY"),
    )
    bucket = s3.Bucket(os.environ.get("S3_BUCKET_NAME"))
    return bucket
