import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
// import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as ec2 from 'aws-cdk-lib/aws-ec2'
import * as iam from 'aws-cdk-lib/aws-iam'
import { Asset } from 'aws-cdk-lib/aws-s3-assets';

export class ChatUiCdkStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const vpc = new ec2.Vpc(this, 'VPC', {
      natGateways: 0
    })

    const instance = new ec2.Instance(this, 'cuatui', {
      vpc:vpc,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PUBLIC
      },
      associatePublicIpAddress: true,
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.T2, ec2.InstanceSize.SMALL),
      machineImage: ec2.MachineImage.latestAmazonLinux2023(),
      requireImdsv2: true
    })


    const instancePolicy = [
      'AmazonSSMManagedEC2InstanceDefaultPolicy',
      'AmazonSageMakerFullAccess', 
      'AmazonSSMReadOnlyAccess'
    ]
    instancePolicy.forEach(policy => { instance.role.addManagedPolicy(
        iam.ManagedPolicy.fromAwsManagedPolicyName(policy)
      )
    });

    instance.connections.allowFromAnyIpv4(ec2.Port.tcp(80))

    const userdataAsset = new Asset(this, 'userdata', {
      path: './asset/userdata.sh'
    });

    const envAsset = new Asset(this, 'env', {
      path: './asset/.env.local'
    });

    const chatuiServiceAsset = new Asset(this, 'chatuiService', {
      path: './asset/chatui.service'
    });

    const mongodbServiceAsset = new Asset(this, 'mongodbService', {
      path: './asset/mongodb.service'
    });

    const usedataPath = instance.userData.addS3DownloadCommand({
      bucket: userdataAsset.bucket,
      bucketKey: userdataAsset.s3ObjectKey,
    })

    const envPath = instance.userData.addS3DownloadCommand({
      bucket: envAsset.bucket,
      bucketKey: envAsset.s3ObjectKey,
      localFile: '/opt/chatui/asset/.env.local'
    })

    const chatuiServicePath = instance.userData.addS3DownloadCommand({
      bucket: chatuiServiceAsset.bucket,
      bucketKey: chatuiServiceAsset.s3ObjectKey,
      localFile: '/opt/chatui/asset/chatui.service'
    })

    const mongodbServicePath = instance.userData.addS3DownloadCommand({
      bucket: mongodbServiceAsset.bucket,
      bucketKey: mongodbServiceAsset.s3ObjectKey,
      localFile: '/opt/chatui/asset/mongodb.service'
    })

    instance.userData.addExecuteFileCommand({
      filePath:usedataPath,
    });

    userdataAsset.grantRead(instance.role);
    envAsset.grantRead(instance.role)
    chatuiServiceAsset.grantRead(instance.role)
    mongodbServiceAsset.grantRead(instance.role)

    new cdk.CfnOutput(this, 'chat-ui-site-url', {
      value: `http://${instance.instancePublicDnsName}:80`
    })

  }
}
