import boto3


class S3:
    def __init__(self):
        self.s3_client = boto3.client("s3")

    def get_signed_url(self, s3_path):
        return self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": "sorterbot", "Key": s3_path},
            ExpiresIn=3600
        )
