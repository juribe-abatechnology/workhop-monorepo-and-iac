import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { 
    Role, 
    ServicePrincipal, 
    PolicyStatement,
    Effect
} from 'aws-cdk-lib/aws-iam';
import * as lambda from '@aws-cdk/aws-lambda-python-alpha'
import { Runtime } from 'aws-cdk-lib/aws-lambda'
import { join } from 'path';

export class Serverless extends cdk.Stack {

    constructor(app:Construct, id:string, props: cdk.StackProps){
        super(app, id, props)

        const role = new Role(this, String(process.env.LAMBDA_NAME), {
            assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
            roleName: `${process.env.LAMBDA_NAME}-role`
        });
        
        const lambdaHandler =  new lambda.PythonFunction(this, String(process.env.LAMBDA_NAME), {
            entry: join(
                __dirname,
                "../../back/lambda/hexagonal/handler.py"
            ),
            runtime: Runtime.PYTHON_3_11,
            role: role,
            functionName: String(process.env.LAMBDA_NAME),
            description: String(process.env.LAMBDA_DESCRIPTION),
            memorySize: 256,
            environment: {
                SECRET_MANAGER: String(process.env.SECRET_MANAGER)
            },
            layers: [
                new lambda.PythonLayerVersion(this, String(process.env.LAMBDA_NAME)+'-layer', {
                    entry: join(
                        __dirname,
                        "../../back/lambda/hexagonal"
                    ),
                })
            ]
        });

        lambdaHandler.addToRolePolicy(new PolicyStatement({
            effect: Effect.ALLOW,
            resources: [String(process.env.ARN_RDS)],
            actions: ['rds:*']
        }))

        new cdk.CfnOutput(this, String(process.env.LAMBDA_NAME), {
            value: lambdaHandler.functionName,
            description: String(process.env.LAMBDA_DESCRIPTION)
        })

    }

}