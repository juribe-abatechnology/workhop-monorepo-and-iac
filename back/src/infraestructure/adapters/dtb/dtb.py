from abc import ABC, abstractmethod
import psycopg2

class DataBase(ABC):

    @abstractmethod
    def postgresql(self, type:str, host:str, username:str, password:str, port:int) -> psycopg2.connect:
        pass

    @abstractmethod
    def mysql(self, host, username, password, port):
        pass 

    @abstractmethod
    def aurora(self):
        pass
