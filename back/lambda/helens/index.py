
def handler(event, context):
    message = 'Helens {} {}!'.format(event['msg'])
    return {
        'message': message
    }