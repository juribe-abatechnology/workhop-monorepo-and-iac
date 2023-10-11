import * as AWS from 'aws-sdk';

export class ClusterUtils {
    constructor() {
    }
    async getClusterTasks(): Promise<string> {
        const listTasksParams: AWS.ECS.ListTasksRequest = {
            cluster: String(process.env.INFRA_CLUSTER),
            serviceName: String(process.env.ECR_REPOSITORY),
        };
        try {
            const ecs = new AWS.ECS();
            const response = await ecs.listTasks(listTasksParams).promise();
            const taskArns = response.taskArns;
            const task = String(taskArns)
            return task
        } catch (error) {
            return 'Error retrieving cluster tasks:' + error
        }
    }

    async taskDefinitionStop(task: string) {
        try {
            const ecsClient = new AWS.ECS();
            const res = await ecsClient.stopTask({
                cluster: `arn:aws:ecs:us-east-1:526382770485:cluster/${String(process.env.INFRA_CLUSTER)}`,
                task: task
            }).promise();
        }catch (error){
            console.log('Error retrieving the stop task:' + error)
        }
    }

    async getClusterTasksByLaunchTypeAndInstanceDNS(TaskArn: string): Promise<string> {
        const ecs = new AWS.ECS();
        const ec2 = new AWS.EC2();
        const describeTasksParams: AWS.ECS.DescribeTasksRequest = {
            cluster: String(process.env.INFRA_CLUSTER),
            tasks: [TaskArn]
        };
      
        try {
            const response = await ecs.describeTasks(describeTasksParams).promise();
            const tasks = response.tasks || [];
            for (const task of tasks) {
                const instance =String(task.containerInstanceArn);
                
                const instanceResponse = await ecs.describeContainerInstances({ 
                    containerInstances: [instance], 
                    cluster: String(process.env.INFRA_CLUSTER),
                }).promise();

                const object = JSON.parse(JSON.stringify(instanceResponse.containerInstances))

                const describeInstancesParams: AWS.EC2.DescribeInstancesRequest = {
                    InstanceIds: [object[0].ec2InstanceId]
                  };

                const describeInstancesResponse = await ec2.describeInstances(describeInstancesParams).promise();
                const reservations = describeInstancesResponse.Reservations || [];
                const instances = reservations.flatMap(reservation => reservation.Instances || []);
                const instanceDNS = instances[0];

                let dns: string | undefined = '';
                if (instanceDNS) {
                    dns = instanceDNS.PublicDnsName;
                }
                console.log(`Instance DNS: ${dns}`);
                return String(dns)
            }
            return 'undefined: not found dns'
        } catch (error) {
            return 'Error retrieving cluster tasks dns: '+ error
        }
    }
}