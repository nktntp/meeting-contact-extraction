from aws_cdk import App
from stack import FastAPIStack


app = App()
FastAPIStack(app, "FastAPIStack")
app.synth()
