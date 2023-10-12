import os
import pickle


class PickleManager:
    """
    Manage pickles for saving, loading, updating, and deleting data.

    Variables:
        folder_path (str): The folder path where pickles will be stored.

    Interactions:
        - No interactions with other classes.
    """

    def __init__(self, folder_path: str):
        """
        Initializes the PickleManager object.

        Parameters:
            folder_path (str): The folder path where pickles will be stored.

        Returns:
            None

        Process:
            - Saves the provided folder path as a class attribute.
            - Checks if the folder path exists; if not, creates the folder.
        """
        self.folder_path = folder_path
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    def save_pickle(self, file_name: str, data):
        """
        Save data as a pickle.

        Parameters:
            file_name (str): The name of the pickle file.
            data: The data to be saved as a pickle.

        Returns:
            None

        Process:
            - Opens the specified file in binary write mode and dumps the data as a pickle.
        """
        try:
            file_path = os.path.join(self.folder_path, file_name)
            with open(file_path, 'wb') as file:
                pickle.dump(data, file)
        except Exception as e:
            raise Exception(f"Error saving pickle: {str(e)}")

    def load_pickle(self, file_name: str):
        """
        Load data from a pickle.

        Parameters:
            file_name (str): The name of the pickle file to load.

        Returns:
            The loaded data from the pickle.

        Process:
            - Opens the specified file in binary read mode and loads the data from the pickle.
        """
        try:
            file_path = os.path.join(self.folder_path, file_name)
            with open(file_path, 'rb') as file:
                data = pickle.load(file)
                return data

        except FileNotFoundError:
            raise FileNotFoundError("Model o preprocessors files not found")

        except PermissionError:
            raise PermissionError("Error with the files permissions")

        except pickle.UnpicklingError:
            raise pickle.UnpicklingError("Error with the model/preprocessors files")

        except Exception as e:
            raise Exception(f"Error loading pickle: {str(e)}")

    def delete_pickle(self, file_name: str):
        """
        Delete a pickle file.

        Parameters:
            file_name (str): The name of the pickle file to delete.

        Returns:
            None

        Process:
            - Deletes the specified pickle file from the folder path.
        """
        try:
            file_path = os.path.join(self.folder_path, file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            raise Exception(f"Error deleting pickle: {str(e)}")