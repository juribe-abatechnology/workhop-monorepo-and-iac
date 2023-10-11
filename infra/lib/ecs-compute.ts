import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as iam from 'aws-cdk-lib/aws-iam';
import { AutoScalingGroup } from "aws-cdk-lib/aws-autoscaling";
import {Bucket} from 'aws-cdk-lib/aws-s3';
import { ClusterUtils } from './utils/cluster';


const clusterUtils = new ClusterUtils()

export class InfraEcsCompute extends cdk.Stack {

    constructor(scope?: Construct, id?: string, props?: cdk.StackProps){
        super(scope, id, props)
        console.log('Deploy our stack cluster AWS ECS 🚀', process.env.CALLER_IDENTITY_ARN)
        const stack = new cdk.Stack(scope, String(process.env.INFRA_ECS_VPC_CLUSTER), {
                env: {
                    account: process.env.AWS_ACCOUNT_ID,
                    region: process.env.AWS_REGION
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
        
        const autoScalingGroup = new AutoScalingGroup(stack, 'ASG', {
                vpc,
                instanceType: new ec2.InstanceType('t3.micro'),
                machineImage: ecs.EcsOptimizedImage.amazonLinux(),
                maxCapacity: 3
        });

        
        const capacityProvider = new ecs.AsgCapacityProvider(stack, 'AsgCapacityProvider', {
            autoScalingGroup,
          });
        
        cluster.addAsgCapacityProvider(capacityProvider);

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
        
        const taskDefinition = new ecs.Ec2TaskDefinition(this, 'TaskDef'+String(process.env.STACK_NAME), {

        })
        
        taskDefinition.addToExecutionRolePolicy(executionRolePolicy)

        /*
        taskDefinition.addToTaskRolePolicy(
            new iam.PolicyStatement({
                effect: iam.Effect.ALLOW,
                resources: [resourcesArns[0]],
                actions: ['s3:*'],
            })
        )
        */
        
        const containerEc2 = taskDefinition.addContainer(String(process.env.STACK_NAME), {
            image: ecs.ContainerImage.fromRegistry(String(process.env.ECR_IMAGE_URI)),
            logging: ecs.LogDrivers.awsLogs({streamPrefix: 'abatech-' + String(process.env.STACK_NAME),}),
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

        new cdk.CfnOutput(this, 'Container'+String(process.env.STACK_NAME), {
            value: containerEc2.containerName,
            description: "the name of the container ecr",
            exportName: containerEc2.containerName,
        });

        const securityGroup = new ec2.SecurityGroup(this, 'sgEc2'+String(process.env.STACK_NAME), {
            vpc:vpc,
            securityGroupName: 'securityGroup'+String(process.env.STACK_NAME)
        });
        securityGroup.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(80));

        const service = new ecs.Ec2Service(this, 'Service'+String(process.env.STACK_NAME), {
          cluster,
          taskDefinition,
          serviceName: String(process.env.STACK_NAME),
          desiredCount:1,
        });

        // Setup AutoScaling policy
        const scaling = service.autoScaleTaskCount({ maxCapacity: 3, minCapacity: 1 });
        scaling.scaleOnCpuUtilization('CpuScaling'+String(process.env.STACK_NAME), {
            targetUtilizationPercent: 50,
            scaleInCooldown: cdk.Duration.seconds(60),
            scaleOutCooldown: cdk.Duration.seconds(60)
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