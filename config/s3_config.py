import os

import boto3
from dotenv import load_dotenv

load_dotenv()


def s3_connection():
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
