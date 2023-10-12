from abc import ABC, abstractmethod
from typing import List
from connectors.interface_connection import InterfaceConnection

class InterfaceRepository(ABC):
    """
    Interface for TimeRepository and CashRepository classes.

    Variables:
        connectors (List[InterfaceConnection]): A list of database connectors (e.g., PostgreSQLConnection, SnowflakeConnection).

    Interactions:
        - Interacts with PostgreSQLConnection and SnowflakeConnection classes for database operations.
    """

    def __init__(self, connectors: List[InterfaceConnection]):
        """
        Initializes the InterfaceRepository object.

        Parameters:
            connectors (List[InterfaceConnection]): A list of InterfaceConnection objects.

        Returns:
            None

        Process:
            - Saves the provided InterfaceConnection objects as class attributes.
        """
        self.connectors = connectors

    @abstractmethod
    def retrieve_data(self, query: str):
        """
        Abstract method to retrieve data from the database.

        Parameters:
            query (str): SQL query to retrieve data.

        Returns:
            None
        """
        pass

    @abstractmethod
    def save_data(self, data, table_name: str):
        """
        Abstract method to save data to the database.

        Parameters:
            data: Data to be saved (format may vary depending on the repository).
            table_name (str): Name of the table to save the data.

        Returns:
            None
        """
        pass
