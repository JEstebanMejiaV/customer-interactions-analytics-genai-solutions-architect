#!/usr/bin/env python3
import aws_cdk as cdk

from interactions_stack import InteractionsStack

app = cdk.App()
InteractionsStack(app, "InteractionsStack")

app.synth()
