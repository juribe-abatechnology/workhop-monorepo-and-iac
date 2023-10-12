import yaml

class YAMLConfigLoader:
    """
    Load configurations and credentials from YAML files.

    Methods:
        load_config(): Load configuration from the 'config.yaml' file.
        load_credentials(): Load credentials from the 'credentials.yaml' file.
    """

    def load_config(self) -> dict:
        """
        Load configuration from the 'config.yaml' file.

        Returns:
            dict: A dictionary containing the configuration data.

        Process:
            - Opens the 'yaml/config.yaml' file in read mode.
            - Uses 'yaml.safe_load()' to load the YAML content as a dictionary.
            - Returns the loaded configuration data as a dictionary.
        """
        try:
            with open('yaml_files/config.yaml', 'r') as file:
                config = yaml.safe_load(file)
            return config
        except FileNotFoundError:
            raise FileNotFoundError("Configuration file 'config.yaml' not found.")
        except Exception as e:
            raise Exception(f"Error loading configuration: {str(e)}")

    def load_credentials(self) -> dict:
        """
        Load credentials from the 'credentials.yaml' file.

        Returns:
            dict: A dictionary containing the credentials data.

        Process:
            - Opens the 'yaml/credentials.yaml' file in read mode.
            - Uses 'yaml.safe_load()' to load the YAML content as a dictionary.
            - Returns the loaded credentials data as a dictionary.
        """
        try:
            with open('yaml_files/credentials.yaml', 'r') as file:
                config = yaml.safe_load(file)
            return config
        except FileNotFoundError:
            raise FileNotFoundError("Credentials file 'credentials.yaml' not found.")
        except Exception as e:
            raise Exception(f"Error loading credentials: {str(e)}")
