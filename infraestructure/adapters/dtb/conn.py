from infraestructure.adapters.dtb.dtb import DataBase
import psycopg2

class ConnDTB(DataBase):
    
    def postgresql(self, type:str, host:str, username:str, password:str, port:int) -> psycopg2.connect:
        conn = psycopg2.connect(database = type, 
                        user = username, 
                        host= host,
                        password = password,
                        port = port)
        return conn

    def mysql(self):
        return "mysql"

    def aurora(self):
        return 
