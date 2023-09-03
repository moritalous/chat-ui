#!/bin/bash

pip3 install -r sagemaker/requirements.txt
python3 sagemaker/create_endpoint.py

sudo npm install -g aws-cdk

cd cdk
npm i

cdk deploy --require-approval never
