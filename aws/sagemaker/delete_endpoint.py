import boto3

client = boto3.client('sagemaker')

target_tag = {'Key': 'app_name','Value': 'chatui'}

if __name__ == '__main__':

  endpoints = client.list_endpoints(MaxResults=100)

  for endpoint in endpoints['Endpoints']:
    arn = endpoint['EndpointArn']
    tags = client.list_tags(ResourceArn=arn)

    if len(list(filter(lambda x: x == target_tag, tags['Tags']))) > 0:
      print(f"Delete: {endpoint['EndpointName']}")
      client.delete_endpoint(EndpointName=endpoint['EndpointName'])
