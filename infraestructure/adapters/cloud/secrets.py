import logging
from botocore.exceptions import ClientError
logger = logging.getLogger(__name__)

class SecretsManager:

    def __init__(self, secretsmanager_client):
        self.secrets_manager_client = secretsmanager_client
        self.name = None

    def _clear(self):
        self.name = None

    def create(self, name, secret_value):
        """
        Creates a new secret, the secret value can be a string or bytes.

        :param name: The name of the secret to create.
        :paran secret_value: The value of the secret.
        :return: Metadata about the newly created secret.
        """
        self._clear()
        try:
            kwargs = {'Name': name}
            if isinstance(secret_value, str):
                kwargs['SecretString'] = secret_value
            elif isinstance(secret_value, bytes):
                kwargs['SecretBytes'] = secret_value
            response = self.secrets_manager_client.create_secret(**kwargs)
            self.name = name
            logger.info("Created Secret %s", name)

        except ValueError:
            logger.exception("Couldn't get secret %s.", name)
            raise
        else:
            return response
        
    def delete(self, without_recovery):
        """
        Delete the secret.

        :param without_recovery: Permantly deletes the secret immediately when True;
                                 Otherwise, the deleted secret can be restored within 
                                 the recovery window. The default recovery window is 30 days
        """

        if self.name is None:
            raise ValueError
        
        try:
            self.secrets_manager_client.delete_secret(
                SecretId=self.name,
                ForceDeleteWithoutRecovery=without_recovery
            )
            logger.info("Deleted secret %s.", self.name)
            self._clear()
        except ValueError:
            logger.error("Deleted Secret %s.", self.name)
            raise 

    def describe(self, name=None):
        """
        Gets metadata about a secret

        :param name: the name of the secret to load. If the name is None, metadata about
                    the current secret is retrieved.
        :return: Metadata about the secret.
        """
        
        if self.name is None and name is None:
            raise ValueError
        if name is None:
            name = self.name
        self._clear()
        try:
            response =  self.secrets_manager_client.describe_secret(SecretId=name)
            self.name = name
            logger.info("Got secret metadata for %s.", name)
        except ValueError:
            logger.error("Couldn't get secret metadata for %s.", name)
            raise 
        else:
            return response
        
    def get_value(self, stage=None):
        """
        Gets the value of a secret

        :param stage: The stage of the secret to retrieve. If this is None, the current stage is retrieved.
        :return: The value of the secret. When the secret is a string, the value is contained in the SecretString
                 field. When the secret is bytes, it is contained in the SecretBinary field
        """
        
        if self.name is None:
            raise ValueError
        
        try:
            kwargs = {'SecretId': self.name}
            if stage is not None:
                kwargs['VersionStage'] = stage
            response = self.secrets_manager_client.get_secret_value(**kwargs)
            logger.info("Got value for secret %s.", self.name)
        except ClientError as e:
            logger.error("Couldn't get value for secret %s.", self.name)
            raise e

        else:
            return response
        
    def list(self, max_results):
        """
        Lists secrets for the current account.
        
        :param max_results: the maximum number of results to return.
        :return: Yields secrets one at a time.
        """

        try:
            paginator = self.secrets_manager_client.get_paginator('list_secrets')
            for page in paginator.paginate(PaginationConfig={'MaxItems': max_results}):
                for secret in page['SecretList']:
                    yield secret 
        except ValueError:
            logger.error("Couldn't list secrets.")
            raise