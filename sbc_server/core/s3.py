import boto3


class S3:
    def __init__(self):
        # Get sorterbot bucket name
        self.ssm = boto3.client("ssm")
        self.bucket_name = self.ssm.get_parameter(Name="SORTERBOT_BUCKET_NAME")["Parameter"]["Value"]

        # Create temporary client
        self.s3_client = boto3.client("s3")

        # Reassign client with the bucket's location (otherwise generate_presigned_url would not work)
        self.s3_client = boto3.client("s3", self.s3_client.get_bucket_location(Bucket=self.bucket_name)["LocationConstraint"])

    def get_signed_url(self, s3_path):
        return self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": s3_path},
            ExpiresIn=36000
        )
