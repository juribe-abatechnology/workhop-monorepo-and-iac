
exports.handler = async(event, context, callback) => {

    response = {
        statusCode: 200,
        body: JSON.stringify(event.queryStringParameters['abatech'])
    }

    return response;


}