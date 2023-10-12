# Use the official Python runtime as the base image
FROM public.ecr.aws/lambda/python:3.10-x86_64

# Copy function code to the container image
COPY . /var/task

# Set the environment variable to your lambda handler name
ENV AWS_LAMBDA_FUNCTION_HANDLER=main.lambda_handler

# Install the project dependencies
RUN pip install -r requirements.txt --target /var/task

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "main.lambda_handler" ]
# CMD [ "python3","main.py" ]