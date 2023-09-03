#!/bin/bash

pip3 install -r sagemaker/requirements.txt
python3 sagemaker/create_endpoint.py

cd cdk
cdk deploy --require-approval never
