#!/bin/bash

TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"`
REGION=`curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/placement/region`

dnf install -y git docker python3-pip nodejs


systemctl enable docker
systemctl start docker

# Install App

mkdir -p /opt/chatui
cd /opt/chatui

git clone https://github.com/moritalous/chat-ui.git

## edit .env.local
cp /opt/chatui/asset/.env.local /opt/chatui/chat-ui/.env.local
LLM_ENDPOINT=`aws ssm get-parameter --name chatui-llm-endpoint --region ${REGION} | jq -r .Parameter.Value`
sed -i -e "s|<<LLM_ENDPOINT_URL>>|${LLM_ENDPOINT}|g" /opt/chatui/chat-ui/.env.local

## build
cd /opt/chatui/chat-ui
npm install
npm run build

# Run monogdb
cp /opt/chatui/asset/mongodb.service /etc/systemd/system/mongodb.service
systemctl enable mongodb.service
systemctl start mongodb.service

# Run App
cp /opt/chatui/asset/chatui.service /etc/systemd/system/chatui.service
systemctl enable chatui.service
systemctl start chatui.service
