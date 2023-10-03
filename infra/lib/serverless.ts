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

export class ServerlessNodejs extends cdk.Stack {

    constructor(app:Construct, id:string, props: cdk.StackProps){
        super(app, id, props)

        console.log("desplegando la infraestructura: ", process.env.AWS_SDK)

        const role = new Role(this, String(process.env.LAMBDA_NAME)+'-role', {
            assumedBy: new ServicePrincipal(String(process.env.SERVICE_ROLE)),
            roleName: `${process.env.LAMBDA_NAME}-role`
        });

            console.log("Deploying lambda with sdk nodejs")
            const lambdaNode =new NodejsFunction(this, String(process.env.LAMBDA_NAME)+'-lambda', {
                entry: join(
                    __dirname,
                    String(process.env.ENTRY_PATH)
                ),
                depsLockFilePath: join(
                    __dirname,
                    String(process.env.DEPS_LOCK_FILE_PATH)
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
                resources: [String(process.env.ARN_DYNAMODB)],
                actions: [String(process.env.ACTION_DYNAMODB)]
            }));

            new cdk.CfnOutput(this, String(process.env.LAMBDA_NAME)+'-cnf', {
                value: lambdaNode.functionName,
                description: String(process.env.LAMBDA_DESCRIPTION)
            })
    }

}

export class ServerlessPython extends cdk.Stack {

    constructor(app:Construct, id:string, props: cdk.StackProps){
        super(app, id, props)

        console.log("desplegando la infraestructura: ", process.env.AWS_SDK)

        const role = new Role(this, String(process.env.LAMBDA_NAME)+'-role', {
            assumedBy: new ServicePrincipal(String(process.env.SERVICE_ROLE)),
            roleName: `${process.env.LAMBDA_NAME}-role`
        });
        
        if(String(process.env.AWS_SDK === "python")){

            const lambdaHandler =  new lambda.PythonFunction(this, String(process.env.LAMBDA_NAME)+'-lambda', {
                entry: join(
                    __dirname,
                    String(process.env.ENTRY_PATH)
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
                            String(process.env.ENTRY_PATH)
                        ),
                        compatibleRuntimes: [Runtime.PYTHON_3_11]
                    })
                ]
            });

            lambdaHandler.addToRolePolicy(new PolicyStatement({
                effect: Effect.ALLOW,
                resources: [String(process.env.ARN_RDS)],
                actions: [String(process.env.ACTION_RDS)]
            }))

            new cdk.CfnOutput(this, String(process.env.LAMBDA_NAME)+'-cnf', {
                value: lambdaHandler.functionName,
                description: String(process.env.LAMBDA_DESCRIPTION)
            })
        }
    }

}