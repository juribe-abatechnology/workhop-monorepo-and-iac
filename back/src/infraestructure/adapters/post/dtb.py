import boto3 as boto
import json

from domain.post.service.post import ServicePost
from infraestructure.adapters.dtb.dtb import DataBase
from infraestructure.adapters.cloud.secrets import SecretsManager
from infraestructure.adapters.post.query import courses

secretManager = SecretsManager(boto.client('secretsmanager'))
secretManager.name = "PostgreSQLDEV" # TODO: environment
credentials = secretManager.get_value()
refatctor = json.loads(credentials['SecretString'])

class PostDTB(ServicePost):
    
    def __init__(self, database:DataBase):
        self.__database = database.postgresql(
            type="postgres",
            host=refatctor['host'],
            password=refatctor['password'], 
            port=5432,
            username=refatctor['username'],
        )

    def get(self, post_id:int):
        print("4. send paymen")
        conn = self.__database
        cur = conn.cursor()
        cur.execute(courses)
        post = cur.fetchall()
        return post

    def save():
        pass
    
