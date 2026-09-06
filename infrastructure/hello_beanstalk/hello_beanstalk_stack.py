import os
from pathlib import Path

import aws_cdk as cdk
from aws_cdk import aws_elasticbeanstalk as eb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3_assets as s3_assets
from constructs import Construct


class HelloBeanstalkStack(cdk.Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)

        # ---------------------------------------------------------
        # 1. Package the Flask application
        # ---------------------------------------------------------

        app_path = Path(__file__).resolve().parents[2] / "app"

        application_bundle = s3_assets.Asset(
            self,
            "ApplicationBundle",
            path=str(app_path),
        )

        # ---------------------------------------------------------
        # 2. Elastic Beanstalk application
        # ---------------------------------------------------------

        beanstalk_app = eb.CfnApplication(
            self,
            "HelloFlaskApplication",
            application_name="hello-flask",
        )

        # ---------------------------------------------------------
        # 3. Elastic Beanstalk service role
        # ---------------------------------------------------------

        service_role = iam.Role(
            self,
            "ElasticBeanstalkServiceRole",
            assumed_by=iam.ServicePrincipal(
                "elasticbeanstalk.amazonaws.com"
            ),
        )

        service_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSElasticBeanstalkEnhancedHealth"
            )
        )

        # ---------------------------------------------------------
        # 4. EC2 role used by Elastic Beanstalk
        # ---------------------------------------------------------

        ec2_role = iam.Role(
            self,
            "ElasticBeanstalkEC2Role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
        )

        ec2_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AWSElasticBeanstalkWebTier"
            )
        )

        ec2_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AWSElasticBeanstalkWorkerTier"
            )
        )

        ec2_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AWSElasticBeanstalkMulticontainerDocker"
            )
        )

        instance_profile = iam.CfnInstanceProfile(
            self,
            "ElasticBeanstalkInstanceProfile",
            roles=[ec2_role.role_name],
        )

        # ---------------------------------------------------------
        # 5. Elastic Beanstalk application version
        # ---------------------------------------------------------

        git_sha = os.environ.get("GITHUB_SHA", "local")[:12]

        application_version = eb.CfnApplicationVersion(
            self,
            "HelloFlaskApplicationVersion",
            application_name=beanstalk_app.ref,
            source_bundle=eb.CfnApplicationVersion.SourceBundleProperty(
                s3_bucket=application_bundle.s3_bucket_name,
                s3_key=application_bundle.s3_object_key,
            ),
        )

        # ---------------------------------------------------------
        # 6. Elastic Beanstalk environment
        # ---------------------------------------------------------

        environment = eb.CfnEnvironment(
            self,
            "HelloFlaskEnvironment",
            application_name=beanstalk_app.ref,
            environment_name="hello-flask-env",

            solution_stack_name=(
                "64bit Amazon Linux 2023 "
                "v4.13.7 running Python 3.13"
            ),

            version_label=application_version.ref,

            option_settings=[
                eb.CfnEnvironment.OptionSettingProperty(
                    namespace="aws:elasticbeanstalk:environment",
                    option_name="EnvironmentType",
                    value="SingleInstance",
                ),

                eb.CfnEnvironment.OptionSettingProperty(
                    namespace="aws:autoscaling:launchconfiguration",
                    option_name="InstanceType",
                    value="t3.micro",
                ),

                eb.CfnEnvironment.OptionSettingProperty(
                    namespace="aws:autoscaling:launchconfiguration",
                    option_name="IamInstanceProfile",
                    value=instance_profile.ref,
                ),

                eb.CfnEnvironment.OptionSettingProperty(
                    namespace="aws:elasticbeanstalk:environment",
                    option_name="ServiceRole",
                    value=service_role.role_arn,
                ),

                eb.CfnEnvironment.OptionSettingProperty(
                    namespace="aws:elasticbeanstalk:environment:process:default",
                    option_name="Port",
                    value="8000",
                ),
            ],
        )

        # Make the deployment order explicit.
        application_version.add_dependency(beanstalk_app)
        environment.add_dependency(application_version)

        # ---------------------------------------------------------
        # 7. Output
        # ---------------------------------------------------------

        cdk.CfnOutput(
            self,
            "BeanstalkEnvironmentURL",
            value=environment.attr_endpoint_url,
        )
