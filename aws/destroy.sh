#!/bin/bash

python3 sagemaker/delete_endpoint.py

sudo npm install -g aws-cdk

cd cdk
cdk destroy -f
