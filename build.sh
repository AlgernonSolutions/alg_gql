#!/usr/bin/env bash
aws \
    cloudformation package \
    --profile dev --template template.yaml \
    --s3-bucket algernonsolutions-templates-dev \
    --output-template .artifacts/templated.yml \
&&
aws \
    cloudformation deploy \
    --profile dev \
    --template .artifacts/templated.yml \
    --stack-name alg-gql-dev-2 \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides \
        GqlApiName=algernonDev \
        IndexTableArn=arn:aws:dynamodb:us-east-1:726075243133:table/Indexes \
        NeptuneClusterArn=arn:aws:rds:us-east-1:726075243133:cluster:leech-cluster \
        NeptuneClusterEndpoint=leech-cluster.cluster-cnd32dx4xing.us-east-1.neptune.amazonaws.com \
        NeptuneClusterReadEndpoint=leech-cluster.cluster-ro-cnd32dx4xing.us-east-1.neptune.amazonaws.com \
        NeptuneSecurityGroupIds=sg-0d07ed715d9cb6795 \
        NeptuneSubnetIds="subnet-0734aaf101c01d188, subnet-01369a7332c93b3d9, subnet-0f080a702392e8892" \
        SensitivesTableArn=arn:aws:dynamodb:us-east-1:726075243133:table/Sensitives \
        IsDev=True \
    --force-upload