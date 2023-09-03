#!/bin/bash

python3 sagemaker/delete_endpoint.py

cd cdk
cdk destroy --require-approval never
