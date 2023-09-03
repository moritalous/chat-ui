import json, time

import sagemaker
from sagemaker.huggingface.model import HuggingFaceModel
from sagemaker.huggingface import get_huggingface_llm_image_uri

import boto3

app_name = 'chatui'

execution_role_name = 'AmazonSageMaker-ExecutionRole-for-chatui'

model_id = 'elyza/ELYZA-japanese-Llama-2-7b-fast-instruct'
instance_type = 'ml.g4dn.12xlarge'
gpus = '4'

account_id = boto3.client('sts').get_caller_identity()['Account']
region_name = boto3.session.Session().region_name

tag = {'Key':'app_name', 'Value': app_name}

def get_sagemaker_execution_role_arn():
  try:
    role = sagemaker.get_execution_role()
  except ValueError:
    iam = boto3.client('iam')

    try:
      response = iam.create_role(
        RoleName=execution_role_name,
        AssumeRolePolicyDocument=json.dumps({
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Principal": {
                "Service": "sagemaker.amazonaws.com"
              },
              "Action": "sts:AssumeRole"
            }
          ]
        })
      )

      time.sleep(5)

      iam.attach_role_policy(
        RoleName=execution_role_name, 
        PolicyArn='arn:aws:iam::aws:policy/AmazonSageMakerFullAccess')

      time.sleep(5)
  
    except Exception as e:
      pass

    role = iam.get_role(RoleName=execution_role_name)['Role']['Arn']

  return role


def create_endpoint():
  
  image_uri = get_huggingface_llm_image_uri(
    backend='huggingface', # or lmi
    # region=region,
  )

  # Hub model configuration <https://huggingface.co/models>
  hub = {
    'HF_MODEL_ID': model_id,        # model_id from hf.co/models
    'HF_TASK':'text-generation',    # NLP task you want to use for predictions
    'SM_NUM_GPUS': gpus,
    # 'HF_MODEL_QUANTIZE':'bitsandbytes',
  }

  # create Hugging Face Model Class
  huggingface_model = HuggingFaceModel(
    env=hub,                   # configuration for loading model from Hub
    role=get_sagemaker_execution_role_arn(),   # IAM role with permissions to create an endpoint
    image_uri=image_uri,
  )

  # deploy model to SageMaker Inference
  predictor = huggingface_model.deploy(
    # endpoint_name=sagemaker_endpoint_name, 
    initial_instance_count=1,
    instance_type=instance_type,
    container_startup_health_check_timeout=600,
    tags=[tag]
  )

  return predictor


def put_parameter(endpoint_name: str):
  boto3.client('ssm').put_parameter(
    Type='String', 
    Name='chatui-llm-endpoint',
    Value=f'https://runtime.sagemaker.{region_name}.amazonaws.com/endpoints/{endpoint_name}/invocations',
    Overwrite=True,
  )


if __name__ == '__main__':
  predictor = create_endpoint()
  endpoint_name = predictor.endpoint_name
  put_parameter(endpoint_name=endpoint_name)

  print('Success create endpoint')
