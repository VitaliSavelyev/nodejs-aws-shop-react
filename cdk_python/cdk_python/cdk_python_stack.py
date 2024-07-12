from aws_cdk import (
    # Duration,
    Stack, aws_s3 as s3,
    RemovalPolicy,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_s3_deployment as s3deploy,
    aws_iam as iam
    # aws_sqs as sqs,
)
from constructs import Construct

class CdkPythonStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(self, 'SavelyevBucket', 
                           removal_policy=RemovalPolicy.DESTROY, 
                           block_public_access=s3.BlockPublicAccess.BLOCK_ALL, 
                           auto_delete_objects=True)

        oai = cloudfront.OriginAccessIdentity(self, "OAInew", comment="OAI xz")

        distribution = cloudfront.Distribution(self, "MyDistribution",
                                                default_behavior=cloudfront.BehaviorOptions(origin=origins.S3Origin(bucket, origin_access_identity=oai),
                                                                                            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS),
                                                default_root_object="index.html")
        
        bucket.add_to_resource_policy(iam.PolicyStatement(
            actions=["s3:GetObject"],
            resources=[bucket.arn_for_objects("*")],
            principals=[iam.ServicePrincipal("cloudfront.amazonaws.com")],
            conditions={
                "StringEquals": {
                    "AWS:SourceArn": f"arn:aws:cloudfront::{self.account}:distribution/{distribution.distribution_id}"
                }
            }
        ))

        oai = cloudfront.OriginAccessIdentity(self, "OAI", comment="OAI xz 2")

        bucket.grant_read(oai)

        s3deploy.BucketDeployment(self, "DeployInvalidation",
                                  sources=[s3deploy.Source.asset("../dist")],
                                  destination_bucket=bucket,
                                  distribution=distribution,
                                  distribution_paths=["/*"]
                                  )