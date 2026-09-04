from aws_cdk import (
    Stack,
    aws_elasticbeanstalk as elasticbeanstalk,
)
from constructs import Construct


class CdkStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs
    ) -> None:

        super().__init__(scope, construct_id, **kwargs)

        # -----------------------------------
        # Elastic Beanstalk Application
        # -----------------------------------
        application = elasticbeanstalk.CfnApplication(
            self,
            "HelloFlaskApplication",
            application_name="hello-flask-app",
        )

        # -----------------------------------
        # Elastic Beanstalk Environment
        # -----------------------------------
        environment = elasticbeanstalk.CfnEnvironment(
            self,
            "HelloFlaskEnvironment",
            application_name=application.application_name,
            environment_name="hello-flask-env",
            solution_stack_name="64bit Amazon Linux 2023 v4.7.0 running Docker",
        )

        # -----------------------------------
        # Environment configuration
        # -----------------------------------
        environment.add_property_override(
            "OptionSettings",
            [
                {
                    "Namespace": "aws:elasticbeanstalk:environment",
                    "OptionName": "EnvironmentType",
                    "Value": "LoadBalanced",
                },
                {
                    "Namespace": "aws:elasticbeanstalk:environment",
                    "OptionName": "LoadBalancerType",
                    "Value": "application",
                },
            ],
        )