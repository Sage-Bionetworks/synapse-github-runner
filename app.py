#!/usr/bin/env python3
import aws_cdk as cdk
import helpers

from common.vpc_stack import VpcStack
from synapse_jenkins.synapse_jenkins_stack import SynapseJenkinsStack

app = cdk.App()
try:
  context, app_config = helpers.get_app_config(app)
except Exception as err:
  raise SystemExit(err)

vpc_stack = VpcStack(app, context, app_config)
synapse_jenkins_stack = SynapseJenkinsStack(app, context, app_config, vpc=vpc_stack.vpc)
synapse_jenkins_stack.add_dependency(vpc_stack)

app.synth()
