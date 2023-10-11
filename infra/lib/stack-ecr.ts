import * as cdk from 'aws-cdk-lib'
import * as ecr from 'aws-cdk-lib/aws-ecr'
import { ArnPrincipal, Effect, PolicyStatement } from 'aws-cdk-lib/aws-iam'
import { Construct } from 'constructs'

export class InfraStackEcr extends cdk.Stack {
	constructor(scope: Construct, id: string, props?: cdk.StackProps) {
		super(scope, id, props)

		console.log('deploy our ecr 🚀')

		if (
			process.env.ECR_REPOSITORIES !== undefined &&
			process.env.INFRA_STACK_NAME !== undefined
		) {
			const ecrPolicyStatement = new PolicyStatement({
				sid: process.env.INFRA_STACK_NAME + 'AllowPushPull',
				effect: Effect.ALLOW,
				principals: [new ArnPrincipal('arn:aws:iam::738453287931:user/JorgeUribe')],
				actions: [
					'ecr:GetDownloadUrlForLayer',
					'ecr:BatchGetImage',
					'ecr:BatchCheckLayerAvailability',
					'ecr:PutImage',
					'ecr:InitiateLayerUpload',
					'ecr:UploadLayerPart',
					'ecr:CompleteLayerUpload',
				],
			})
			const ecrImages = process.env.ECR_REPOSITORIES.split(',')
			for (let i = 0; i < ecrImages.length; i++) {
				const repository = new ecr.Repository(
					this,
					String(ecrImages[i]) + 'Ecr',
					{
						repositoryName: ecrImages[i],
					}
				)
				repository.addLifecycleRule({ maxImageCount: 9 })
				repository.addToResourcePolicy(ecrPolicyStatement)
			}
		}
	}
}
