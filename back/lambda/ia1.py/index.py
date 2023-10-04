
def handler(event, context):
    message = 'Ia team {} {}!'.format(event['first_name'], event['last_name'])
    return {
        'message': message
    }