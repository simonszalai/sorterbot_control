"""
S3 client to get signed URLs for the stitched images to be used as img src on the frontend.

"""

import os
import boto3


class S3:
    """
    Since the S3 buckets names has to be globally unique, to avoid clashes, they contain a random string. That string is generated deploy time and saved
    as an SSM parameter. It is retrieved here.

    """

    def __init__(self):
        # Get sorterbot bucket name
        session = boto3.Session(region_name=os.getenv("DEPLOY_REGION"))
        self.ssm = session.client("ssm")
        self.bucket_name = f'sorterbot-{self.ssm.get_parameter(Name="RESOURCE_SUFFIX")["Parameter"]["Value"]}'

        # Create temporary client
        self.s3_client = session.client("s3")

        # Reassign client with the bucket's location (otherwise generate_presigned_url would not work)
        self.s3_client = session.client("s3", self.s3_client.get_bucket_location(Bucket=self.bucket_name)["LocationConstraint"])

    def get_signed_url(self, s3_path):
        """
        Gets a signed URL for an S3 path.

        Parameters
        ----------
        s3_path : str
            Path of the S3 object to which a signed URL has to be retrieved.

        Returns
        -------
        presigned_url : str
            Presigned URL that can be used as img src on the frontend.

        """

        return self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": s3_path},
            ExpiresIn=36000
        )
