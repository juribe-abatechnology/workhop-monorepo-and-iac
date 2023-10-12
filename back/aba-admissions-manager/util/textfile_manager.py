import os

class TextfileManager:
    """
    Manage text files (save, load, delete).

    Variables:
        folder_path (str): The path to the folder where text files will be stored.

    Interactions:
        None.
    """

    def __init__(self, folder_path: str):
        """
        Initializes the TextfileManager object.

        Parameters:
            folder_path (str): The path to the folder where text files will be stored.

        Returns:
            None

        Process:
            - Saves the provided folder_path as a class attribute.
        """
        self.folder_path = folder_path

    def save_textfile(self, filename: str, content: str):
        """
        Saves text content as a text file with the given filename.

        Parameters:
            filename (str): The name of the text file (including extension).
            content (str): The text content to be saved.

        Returns:
            None

        Process:
            - Combines the folder_path and filename to create the full file path.
            - Writes the content to the specified file path.
        """
        try:
            file_path = os.path.join(self.folder_path, filename)
            with open(file_path, 'w') as file:
                file.write(content)
        except Exception as e:
            raise Exception(f"Error saving text file: {str(e)}")

    def load_textfile(self, filename: str) -> str:
        """
        Loads text content from a text file with the given filename.

        Parameters:
            filename (str): The name of the text file (including extension).

        Returns:
            str: The content of the text file as a string.

        Process:
            - Combines the folder_path and filename to create the full file path.
            - Reads and returns the content from the specified file path.
        """
        try:
            file_path = os.path.join(self.folder_path, filename)
            with open(file_path, 'r') as file:
                content = file.read()
                return content

        except FileNotFoundError:
            raise FileNotFoundError("Error with the sql query")

        except Exception as e:
            raise Exception(f"Error loading text file: {str(e)}")

    def delete_textfile(self, filename: str):
        """
        Deletes a text file with the given filename.

        Parameters:
            filename (str): The name of the text file (including extension).

        Returns:
            None

        Process:
            - Combines the folder_path and filename to create the full file path.
            - Deletes the file from the specified file path.
        """
        try:
            file_path = os.path.join(self.folder_path, filename)
            os.remove(file_path)
        except FileNotFoundError:
            pass  # File not found, do nothing
        except Exception as e:
            raise Exception(f"Error deleting text file: {str(e)}")