#!/usr/bin/env python3
import aws_cdk as cdk
import helpers

from synapse_jenkins.synapse_jenkins_stack import SynapseJenkinsStack

app = cdk.App()
try:
  context, app_config = helpers.get_app_config(app)
except Exception as err:
  raise SystemExit(err)

synapse_jenkins_stack = SynapseJenkinsStack(app, context, app_config)

app.synth()
