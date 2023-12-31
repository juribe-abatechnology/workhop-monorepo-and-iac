#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { ServerlessNodejs, ServerlessPython } from '../lib/serverless';
import { InfraEcsCompute } from '../lib/ecs-compute';
import { InfraStackEcr } from '../lib/stack-ecr';

const app = new cdk.App();
const config = app.node.tryGetContext('config')

switch(config){

  case process.env.STACK_CONFIG_LAMBDA:
    if(process.env.AWS_SDK === 'nodejs'){
      const lambda = new ServerlessNodejs(app, String(process.env.STACK_NAME), {
        env: {
          account: process.env.AWS_ACCOUNT_ID,
          region: process.env.AWS_REGION
        }
      });
      taggingStack(lambda, 'pc-1', 'hexagonal', 'dev', 'cc-0001203', 'na', 'na')
    }
    if(process.env.AWS_SDK === 'python'){
      const lambda = new ServerlessPython(app, String(process.env.STACK_NAME), {
        env: {
          account: process.env.AWS_ACCOUNT_ID,
          region: process.env.AWS_REGION
        }
      });
      taggingStack(lambda, 'pc-1', 'hexagonal', 'dev', 'cc-0001203', 'na', 'na')
    }
    break;

    case 'EcsComputing':
      const infraEcsCompute = new InfraEcsCompute(app, String(process.env.STACK_NAME), {
        env: {
          account: process.env.AWS_ACCOUNT_ID,
          region: process.env.AWS_REGION
        }
      })
      
      taggingStack(infraEcsCompute, 'pc-1', 'ecs', 'dev', 'cc-0001203', 'na', 'na')
      break;

    case 'infraECR':
        const infraEcr = new InfraStackEcr(app, String(process.env.INFRA_STACK_NAME), {
        env: {
          account: process.env.ACCOUNT_ID,
          region: process.env.REGION
        }
        });
        taggingStack(infraEcr, 'pc-1', 'whitelabel', 'dev', 'cc-0001203', 'na', 'na')
          break;
    

}
function taggingStack(
  stack: Construct, 
  projectCode:string, 
  businessService:string,
  projectName:string,
  environment:string,
  costCenter:string,
  schedule:string,
  ){

  cdk.Tags.of(stack).add('proyecto:project-code', projectCode)
  cdk.Tags.of(stack).add('abatech:bussiness-service', businessService)
  cdk.Tags.of(stack).add('abatech:project-name', projectName)
  cdk.Tags.of(stack).add('abatech:environment', environment)
  cdk.Tags.of(stack).add('abatech:cost-center', costCenter)
  cdk.Tags.of(stack).add('abatech:shedule', schedule)

}