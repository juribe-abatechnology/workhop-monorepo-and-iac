"""
Model ia UR 
"""


def handler(event, context):
    message = 'Model UR - by {}!'.format(event['first_name'])
    return {
        'message': message
    }