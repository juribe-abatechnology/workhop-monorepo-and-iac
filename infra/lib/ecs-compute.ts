import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as iam from 'aws-cdk-lib/aws-iam';
import {Bucket} from 'aws-cdk-lib/aws-s3';
import { ClusterUtils } from './utils/cluster';

const clusterUtils = new ClusterUtils()

export class InfraEcsCompute extends cdk.Stack {

    constructor(scope?: Construct, id?: string, props?: cdk.StackProps){
        super(scope, id, props)
        console.log('Deploy our stack cluster AWS ECS 🚀')
        const stack = new cdk.Stack(scope, String(process.env.INFRA_ECS_VPC_CLUSTER), {
                env: {
                    account: process.env.ACCOUNT_ID,
                    region: process.env.REGION
                }
        });

        const vpc = new ec2.Vpc(stack, String(process.env.INFRA_VPC_NAME), {
            cidr: "10.1.0.0/16",
            subnetConfiguration: [
                {cidrMask: 24, subnetType: ec2.SubnetType.PUBLIC, name: "Public"},
            ],
            maxAzs: 2,
            vpcName: String(process.env.INFRA_VPC_NAME),
        });
    
        const cluster = new ecs.Cluster(stack, String(process.env.INFRA_CLUSTER), {
                clusterName: String(process.env.INFRA_CLUSTER),
                vpc: vpc
        });
        
        cluster.addCapacity('EC2CapacityASG', {
            instanceType: cdk.aws_ec2.InstanceType.of(ec2.InstanceClass.T2, ec2.InstanceSize.MICRO),
        });

        const executionRolePolicy =  new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            resources: ['*'],
            actions: [
                    "ecr:GetAuthorizationToken",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ]
        });
        
        const taskDefinition = new ecs.Ec2TaskDefinition(this, 'TaskDef'+String(process.env.ECR_REPOSITORY), {
        
        })
        
        taskDefinition.addToExecutionRolePolicy(executionRolePolicy)

        const resourcesArns = [];
        if (process.env.S3 && process.env.S3_NAME) {
            console.log('creando el bucket de s3 ✅')
            const s3Bucket = new Bucket(this, String(process.env.INFRA_STACK_NAME).replace(/ /g, '') + String(process.env.S3_NAME).replace(/ /g, '') + 'Bucket', {
              bucketName: String(process.env.S3_NAME),
              publicReadAccess: false,
              removalPolicy: cdk.RemovalPolicy.DESTROY
            });
            resourcesArns.push(s3Bucket.bucketArn);
            resourcesArns.push(s3Bucket.bucketArn + '/*');

            // grant access to ec2
            s3Bucket.addToResourcePolicy(new iam.PolicyStatement({
                sid: process.env.INFRA_STACK_NAME + 'AllowPushPull',
				effect: iam.Effect.ALLOW,
				principals: [new iam.ArnPrincipal(String(process.env.CALLER_IDENTITY_ARN))],
                actions: [
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:DeleteObject",
                    's3:ListBucket'
                ],
                resources: [
                    `${s3Bucket.bucketArn}/*`,
                    s3Bucket.bucketArn
                ],
            }));

            new cdk.CfnOutput(this,  'BucketName' + String(process.env.S3_NAME), { value: s3Bucket.bucketName });
        }
        
        taskDefinition.addToTaskRolePolicy(
            new iam.PolicyStatement({
                effect: iam.Effect.ALLOW,
                resources: [resourcesArns[0]],
                actions: ['s3:*'],
            })
        )
        

        const containerEc2 = taskDefinition.addContainer(String(process.env.ECR_REPOSITORY), {
            image: ecs.ContainerImage.fromRegistry(String(process.env.ECR_IMAGE_URI)),
            logging: ecs.LogDrivers.awsLogs({streamPrefix: 'whitelabel-' + String(process.env.ECR_REPOSITORY),}),
            memoryReservationMiB:512,
            environment: {
                NODE_ENV: String(process.env.NODE_ENV),
                PORT: String(process.env.PORT),
                URL_FRONTEND: String(process.env.URL_FRONTEND),
                DB_HOST: String(process.env.DB_HOST),
                DB_PORT: String(process.env.DB_PORT),
                DB_USER: String(process.env.DB_USER),
                DB_PASSWORD: String(process.env.DB_PASSWORD),
                DB_NAME: String(process.env.DB_NAME),
                
            },
        });
        
        containerEc2.addPortMappings({
          containerPort: 3000,
          hostPort:80,
          protocol: ecs.Protocol.TCP
        });

        new cdk.CfnOutput(this, 'Container'+String(process.env.ECR_REPOSITORY), {
            value: containerEc2.containerName,
            description: "the name of the container ecr",
            exportName: containerEc2.containerName,
        });

        const securityGroup = new ec2.SecurityGroup(this, 'sgEc2'+String(process.env.ECR_REPOSITORY), {
            vpc:vpc,
            securityGroupName: 'securityGroup'+String(process.env.ECR_REPOSITORY)
        });
        securityGroup.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(80));

        const service = new ecs.Ec2Service(this, 'Service'+String(process.env.ECR_REPOSITORY), {
          cluster,
          taskDefinition,
          serviceName: String(process.env.ECR_REPOSITORY),
          desiredCount:1,
        });

        new cdk.CfnOutput(this, 'Service1Arn', {
            value: service.serviceArn,
        });

        this.stopTaskDefinition()
    }

    async stopTaskDefinition() {
       const taskArn =  await clusterUtils.getClusterTasks();
       await clusterUtils.taskDefinitionStop(taskArn);
    }

}