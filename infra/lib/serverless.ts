import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { 
    Role, 
    ServicePrincipal, 
    PolicyStatement,
    Effect
} from 'aws-cdk-lib/aws-iam';
import * as lambda from '@aws-cdk/aws-lambda-python-alpha';
import { Runtime } from 'aws-cdk-lib/aws-lambda';
import { NodejsFunction } from 'aws-cdk-lib/aws-lambda-nodejs';
import { join } from 'path';

export class Serverless extends cdk.Stack {

    constructor(app:Construct, id:string, props: cdk.StackProps){
        super(app, id, props)

        console.log("desplegando la infraestructura: ", process.env.AWS_SDK)

        const role = new Role(this, String(process.env.LAMBDA_NAME)+'-role', {
            assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
            roleName: `${process.env.LAMBDA_NAME}-role`
        });
        
        if(String(process.env.AWS_SDK === "python")){

            const lambdaHandler =  new lambda.PythonFunction(this, String(process.env.LAMBDA_NAME)+'-lambda', {
                entry: join(
                    __dirname,
                    "../../back/lambda/hexagonal"
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
                        compatibleRuntimes: [Runtime.PYTHON_3_11]
                    })
                ]
            });

            lambdaHandler.addToRolePolicy(new PolicyStatement({
                effect: Effect.ALLOW,
                resources: [String(process.env.ARN_RDS)],
                actions: ['rds:*']
            }))

            new cdk.CfnOutput(this, String(process.env.LAMBDA_NAME)+'-cnf', {
                value: lambdaHandler.functionName,
                description: String(process.env.LAMBDA_DESCRIPTION)
            })
        }

        if(String(process.env.AWS_SK) === 'nodejs'){
            console.log("Deploying lambda with sdk nodejs")
            const lambdaNode =new NodejsFunction(this, String(process.env.LAMBDA_NAME)+'-lambda', {
                entry: join(
                    __dirname,
                    "../../back/lambda/example/handler.js"
                ),
                depsLockFilePath: join(
                    __dirname,
                    "../../back/lambda/example/package-lock.js"
                ),
                runtime: Runtime.NODEJS_18_X,
                timeout: cdk.Duration.minutes(1),
                role: role,
                functionName: String(process.env.LAMBDA_NAME),
                description: String(process.env.LAMBDA_DESCRIPTION),
                memorySize:256, 
                environment:{

                }
            });

            lambdaNode.addToRolePolicy(new PolicyStatement({
                effect: Effect.ALLOW,
                resources: ["arn:aws:dynamodb:us-east-1:408058604061:table/payment"],
                actions: ["dynamodb:*"]
            }));

            new cdk.CfnOutput(this, String(process.env.LAMBDA_NAME)+'-cnf', {
                value: lambdaNode.functionName,
                description: String(process.env.LAMBDA_DESCRIPTION)
            })

        }   
    }

}