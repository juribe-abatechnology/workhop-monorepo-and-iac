import json


def serialize_dataframe_to_json(dataframe):
    json_data = dataframe.to_json(orient='records')
    return json_data


def pretty_json(json_data):
    parsed_data = json.dumps(json.loads(json_data), indent=4)
    return parsed_data


def response_error_json(code, error_message):  # we can make this function a class that inherits from BaseException
    if code == 400:
        json_data = '''{
                "statusCode": 400,
                "body": '''+json.dumps({'error': f'{error_message}'})+'''
            }'''''
    elif code == 500:
        json_data = '''{
                "statusCode": 500,
                "body": '''+json.dumps({'error': f'{error_message}'})+'''
            }'''
    return pretty_json(json_data)


def response_json(data):
    json_data = '''{
        "statusCode": 200,
        "body": "Data published successfully",
        "data": '''+json.dumps(str(data))+''',
        "length": '''+str(len(data))+'''
    }'''

    return pretty_json(json_data)


def receive_json(data):
    return json.loads(data)