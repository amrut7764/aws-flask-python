import os
from flask import Flask, jsonify, Response, request
from lib import *
app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello AWS CLOUD World!"


@app.route("/ec2/")
def listAllEC2Instances():
    try:
        ec2 = awsEC2().allInstances(instanceId=[])
        return responseBuilder(app, jsonify(ec2))
    except Exception as e:
        return exceptionBuilder(app, e)


@app.route("/ec2/<string:instanceId>")
def listEC2Instance(instanceId):
    try:
        ec2 = awsEC2().allInstances(instanceId=instanceId)
        return responseBuilder(app, jsonify(ec2))
    except Exception as e:
        return exceptionBuilder(app, e)


@app.route("/rds/<string:dbInstanceId>")
def listRDSInstance(dbInstanceId):
    try:
        rds = awsRDS().RDSInstances(dbInstanceId=dbInstanceId)
        return responseBuilder(app, jsonify(rds))
    except Exception as e:
        return exceptionBuilder(app, e)


@app.route("/rds/")
def listAllRDSInstances():
    try:
        rds = awsRDS().RDSInstances()
        return responseBuilder(app, jsonify(rds))
    except Exception as e:
        return exceptionBuilder(app, e)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
