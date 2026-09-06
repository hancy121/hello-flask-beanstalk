#!/usr/bin/env python3

import aws_cdk as cdk

from hello_beanstalk.hello_beanstalk_stack import HelloBeanstalkStack


app = cdk.App()

HelloBeanstalkStack(
    app,
    "HelloBeanstalkStack",
)

app.synth()
