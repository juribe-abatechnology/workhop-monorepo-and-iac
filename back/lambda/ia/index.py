
def handler(event, context):
    message = 'Abatech {} {}!'.format(event['first_name'], event['last_name'])
    return {
        'message': message
    }