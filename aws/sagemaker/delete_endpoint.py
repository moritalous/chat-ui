import boto3

if __name__ == '__main__':

  llm_parameter = boto3.client('ssm').get_parameter(
    Name='chatui-llm-endpoint_name'
  )

  endpoint = llm_parameter['Parameter']['Value']
  
  print(f"Delete: {endpoint}")
  boto3.client('sagemaker').delete_endpoint(EndpointName=endpoint)

  boto3.client('ssm').delete_parameter(
    Name='chatui-llm-endpoint'
  )

  boto3.client('ssm').delete_parameter(
    Name='chatui-llm-endpoint_name'
  )
