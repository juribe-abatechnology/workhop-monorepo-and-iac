from connectors.postgresql_connection import PostgreSQLConnection
from connectors.snowflake_connection import SnowflakeConnection
from controller.eiv_controller import EIVController
from util.yaml_config_loader import YAMLConfigLoader
import warnings


def lambda_request(event, context):

    # Extract information of the config
    config = YAMLConfigLoader().load_config()
    credentials = YAMLConfigLoader().load_credentials()

    # Instance the connection with RDS
    db_rds = PostgreSQLConnection(config['rds']['host'],
                                  config['rds']['port'],
                                  config['rds']['database'],
                                  credentials['rds']['user'],
                                  credentials['rds']['password'])
    db_snowflake = SnowflakeConnection(config['snowflake']['account'],
                                       credentials['snowflake']['user'],
                                       credentials['snowflake']['password'],
                                       config['snowflake']['database'],
                                       config['snowflake']['schema'],
                                       config['snowflake']['warehouse'],
                                       config['snowflake']['role'])

    eiv_controller = EIVController([db_rds, db_snowflake])

    return eiv_controller.handle_request(event, context)


def lambda_handler(event, context):
    warnings.filterwarnings("ignore")

    # Call handler for AWS Lambda
    return lambda_request(event, context)
