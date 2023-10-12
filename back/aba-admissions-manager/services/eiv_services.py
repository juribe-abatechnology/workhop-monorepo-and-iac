from typing import Dict, List
from pandas import DataFrame
import pandas as pd
import datetime
from connectors.interface_connection import InterfaceConnection
from repository.eiv_repository import EIVRepository
from sklearn.impute import SimpleImputer
from util.textfile_manager import TextfileManager
from services.eiv_helper import verify_data_categories
from services.eiv_helper import extract_prefix, search_and_get_first_value, \
                                search_specific_and_get_first_value, \
                                calculate_master_collected, \
                                calculate_claim_amount_paid
from services.eiv_helper import calculate_adjusted_eiv
import numpy as np


class EIVService:
    """
    Manage all processes to run an AI model for prediction.

    Variables:
        EIVRepository (EIVRepository): A EIVRepository object for data
        management.

    Interactions:
        None.
    """

    def __init__(self, connectors: List[InterfaceConnection]):
        """
        Initializes the EIVService object.

        Parameters:
            connectors (List[InterfaceConnection]): A list of
            InterfaceConnection objects.

        Returns:
            None

        Process:
            - Creates a EIVRepository object and saves it as a class attribute.
        """
        self.eiv_repository = EIVRepository(connectors)

    def load_data_from_snowflake(self) -> DataFrame:
        """
        Load data from Snowflake using a SQL file.

        Returns:
        dataframe (pd.DataFrame): The loaded data as a pandas DataFrame.
        """
        # Load SQL file
        sql = TextfileManager('sql/').load_textfile('eiv_sql.sql')

        # Call to snowflake database
        df_snowflake = self.eiv_repository.retrieve_data_from_snowflake(sql)

        # Delete some rows from the query for some special inner joins
        # This features are less than 1% of the data
        df_snowflake = df_snowflake.drop_duplicates(['CLIENT_NAME', 'ALLOWED'])

        # Create a column for identifien propouses
        df_snowflake['VOB_ID'] = None

        return df_snowflake

    def load_data_to_dataframe(self, body: DataFrame,
                               df_snowflake: DataFrame) -> DataFrame:
        """
        Create the initial DataFrame for use.

        Returns:
            DataFrame: A DataFrame containing the loaded data.
        Process:
            - Creates every field for the Dataframe for use the model
        """
        try:
            client_name = {'CLIENT_NAME': ['', '']}
            index = [0, 1]  # Only for one client
            data = pd.DataFrame(client_name, index=index)

            # Identification data
            data['VOB_ID'] = body['VOBID']
            data['CLIENT_NAME'] = body['ClientName'] if body['ClientName'] is not None else None
            data['CONNECT_TRACKING_ID'] = body['ClientTrackingID'] if body['ClientTrackingID'] is not None else None

            # Relevant variables for the model
            data['SUBSCRIBER'] = body['Subscriber'].str.upper() if body['Subscriber'] is not None else None
            data['GROUP_NUMBER'] = body['GroupID'].str.upper() if body['GroupID'] is not None else None
            data['PREFIX'] = extract_prefix(body['PolicyID'], 3)

            payor = body['Payor'] if body['Payor'] is not None else None
            data['PAYOR'] = verify_data_categories(df_snowflake=df_snowflake,
                                                   feature=payor,
                                                   column_name='PAYOR',
                                                   apply_filter=True)
            data['FUNDED_STATUS'] = body['FundingType'] if body['FundingType'] is not None else None

            state = body['State'].str.upper() if body['State'] is not None else None
            data['STATE'] = verify_data_categories(df_snowflake=df_snowflake,
                                                   feature=state,
                                                   column_name='STATE',
                                                   apply_filter=True)

            data['DEDUCTIBLE'] = body['Deductible']
            data['OUT_OF_POCKET'] = body['OutOfBucket']
            data['CO_INSURANCE'] = body['CoinsuranceOON']
            data['OON_BENEFITS'] = body['OONBenefits']
            data['SCA_FLAG'] = body['SCA']
            data['MULTIPLAN_FLAG'] = body['Multiplan']

            data['POLICY_TYPE'] = verify_data_categories(df_snowflake=df_snowflake,
                                                         feature=body['PolicyType'],
                                                         column_name='POLICY_TYPE',
                                                         apply_filter=True)

            # Remplace for data be equal to snowflake for querys
            data['OON_BENEFITS'] = data['OON_BENEFITS'].astype(str, errors='ignore').replace({'True': 'Yes',
                                                                                              'False': 'No'})
            data['SCA_FLAG'] = data['SCA_FLAG'].astype(str, errors='ignore').replace({'True': 'Yes',
                                                                                      'False': 'No'})
            data['MULTIPLAN_FLAG'] = data['MULTIPLAN_FLAG'].astype(str, errors='ignore').replace({'True': 'Yes',
                                                                                                  'False': 'No'})

            # Return data from the number of claims in the waterfall
            data['CLIENT_CLAIMS_PY'] = search_and_get_first_value(df_snowflake, 'CLIENT_NAME', data['CLIENT_NAME'][0],'CLIENT_CLAIMS_PY', data['SCA_FLAG'][0])
            data['PREFIX_CLAIMS_PY'] = search_and_get_first_value(df_snowflake, 'PREFIX', data['PREFIX'][0], 'PREFIX_CLAIMS_PY', data['SCA_FLAG'][0])
            data['PAYOR_CLAIMS_PY'] = search_and_get_first_value(df_snowflake, 'PAYOR', data['PAYOR'][0], 'PAYOR_CLAIMS_PY', data['SCA_FLAG'][0])
            data['STATE_CLAIMS_PY'] = search_and_get_first_value(df_snowflake, 'STATE', data['STATE'][0], 'STATE_CLAIMS_PY', data['SCA_FLAG'][0])
            data['SUBS_CLAIMS_PY'] = search_and_get_first_value(df_snowflake, 'SUBSCRIBER', data['SUBSCRIBER'][0], 'SUBS_CLAIMS_PY', data['SCA_FLAG'][0])
            data['GROUP_CLAIMS_PY'] = search_and_get_first_value(df_snowflake, 'GROUP_NUMBER', data['GROUP_NUMBER'][0], 'GROUP_CLAIMS_PY', data['SCA_FLAG'][0])
            data['FUNDED_CLAIMS_PY'] = search_and_get_first_value(df_snowflake, 'FUNDED_STATUS', data['FUNDED_STATUS'][0], 'FUNDED_CLAIMS_PY', data['SCA_FLAG'][0])

            data['CLIENT_CLAIMS'] = search_and_get_first_value(df_snowflake, 'CLIENT_NAME',data['CLIENT_NAME'][0],'CLIENT_CLAIMS', data['SCA_FLAG'][0])
            data['PREFIX_CLAIMS'] = search_and_get_first_value(df_snowflake, 'PREFIX', data['PREFIX'][0], 'PREFIX_CLAIMS', data['SCA_FLAG'][0])
            data['PAYOR_CLAIMS'] = search_and_get_first_value(df_snowflake, 'PAYOR', data['PAYOR'][0], 'PAYOR_CLAIMS', data['SCA_FLAG'][0])
            data['STATE_CLAIMS'] = search_and_get_first_value(df_snowflake, 'STATE', data['STATE'][0], 'STATE_CLAIMS', data['SCA_FLAG'][0])
            data['SUBS_CLAIMS'] = search_and_get_first_value(df_snowflake, 'SUBSCRIBER', data['SUBSCRIBER'][0], 'SUBS_CLAIMS', data['SCA_FLAG'][0])
            data['GROUP_CLAIMS'] = search_and_get_first_value(df_snowflake, 'GROUP_NUMBER', data['GROUP_NUMBER'][0], 'GROUP_CLAIMS', data['SCA_FLAG'][0])
            data['FUNDED_CLAIMS'] = search_and_get_first_value(df_snowflake, 'FUNDED_STATUS', data['FUNDED_STATUS'][0], 'FUNDED_CLAIMS', data['SCA_FLAG'][0])

            # Return data from the pullthrought of claims in the waterfall
            data['CLIENT_$_PY'] = search_and_get_first_value(df_snowflake, 'CLIENT_NAME',data['CLIENT_NAME'][0],'CLIENT_$_PY',data['SCA_FLAG'][0])
            data['PREFIX_$_PY'] = search_and_get_first_value(df_snowflake, 'PREFIX', data['PREFIX'][0], 'PREFIX_$_PY',data['SCA_FLAG'][0])
            data['PAYOR_$_PY'] = search_and_get_first_value(df_snowflake, 'PAYOR', data['PAYOR'][0], 'PAYOR_$_PY',data['SCA_FLAG'][0])
            data['STATE_$_PY'] = search_and_get_first_value(df_snowflake, 'STATE', data['STATE'][0], 'STATE_$_PY',data['SCA_FLAG'][0])
            data['SUBS_$_PY'] = search_and_get_first_value(df_snowflake, 'SUBSCRIBER', data['SUBSCRIBER'][0], 'SUBS_$_PY',data['SCA_FLAG'][0])
            data['GROUP_$_PY'] = search_and_get_first_value(df_snowflake, 'GROUP_NUMBER', data['GROUP_NUMBER'][0], 'GROUP_$_PY',data['SCA_FLAG'][0])
            data['FUNDED_$_PY'] = search_and_get_first_value(df_snowflake, 'FUNDED_STATUS', data['FUNDED_STATUS'][0], 'FUNDED_$_PY',data['SCA_FLAG'][0])

            data['CLIENT_$'] = search_and_get_first_value(df_snowflake, 'CLIENT_NAME', data['CLIENT_NAME'][0],'CLIENT_$', data['SCA_FLAG'][0])
            data['PREFIX_$'] = search_and_get_first_value(df_snowflake, 'PREFIX', data['PREFIX'][0], 'PREFIX_$', data['SCA_FLAG'][0])
            data['PAYOR_$'] = search_and_get_first_value(df_snowflake, 'PAYOR', data['PAYOR'][0], 'PAYOR_$',data['SCA_FLAG'][0])
            data['STATE_$'] = search_and_get_first_value(df_snowflake, 'STATE', data['STATE'][0], 'STATE_$',data['SCA_FLAG'][0])
            data['SUBS_$'] = search_and_get_first_value(df_snowflake, 'SUBSCRIBER', data['SUBSCRIBER'][0], 'SUBS_$',data['SCA_FLAG'][0])
            data['GROUP_$'] = search_and_get_first_value(df_snowflake, 'GROUP_NUMBER', data['GROUP_NUMBER'][0], 'GROUP_$',data['SCA_FLAG'][0])
            data['FUNDED_$'] = search_and_get_first_value(df_snowflake, 'FUNDED_STATUS', data['FUNDED_STATUS'][0], 'FUNDED_$',data['SCA_FLAG'][0])
            data['MASTER_COLLECTED'] = data.apply(calculate_master_collected, axis=1)

            # Return data from the number of claims in the waterfall
            data['CLIENT_BILL_PY'] = search_and_get_first_value(df_snowflake, 'CLIENT_NAME',data['CLIENT_NAME'][0],'CLIENT_BILL_PY', data['SCA_FLAG'][0])
            data['PREFIX_BILL_PY'] = search_and_get_first_value(df_snowflake, 'PREFIX', data['PREFIX'][0], 'PREFIX_BILL_PY',data['SCA_FLAG'][0])
            data['PAYOR_BILL_PY'] = search_and_get_first_value(df_snowflake, 'PAYOR', data['PAYOR'][0], 'PAYOR_BILL',data['SCA_FLAG'][0])
            data['STATE_BILL_PY'] = search_and_get_first_value(df_snowflake, 'STATE', data['STATE'][0], 'STATE_BILL_PY',data['SCA_FLAG'][0])
            data['SUBS_BILL_PY'] = search_and_get_first_value(df_snowflake, 'SUBSCRIBER', data['SUBSCRIBER'][0], 'SUBS_BILL',data['SCA_FLAG'][0])
            data['GROUP_BILL_PY'] = search_and_get_first_value(df_snowflake, 'GROUP_NUMBER', data['GROUP_NUMBER'][0], 'GROUP_BILL_PY',data['SCA_FLAG'][0])
            data['FUNDED_BILL_PY'] = search_and_get_first_value(df_snowflake, 'FUNDED_STATUS', data['FUNDED_STATUS'][0], 'FUNDED_BILL_PY',data['SCA_FLAG'][0])
            
            data['CLIENT_BILL'] = search_and_get_first_value(df_snowflake, 'CLIENT_NAME',data['CLIENT_NAME'][0],'CLIENT_BILL',data['SCA_FLAG'][0])
            data['PREFIX_BILL'] = search_and_get_first_value(df_snowflake, 'PREFIX', data['PREFIX'][0], 'PREFIX_BILL',data['SCA_FLAG'][0])
            data['PAYOR_BILL'] = search_and_get_first_value(df_snowflake, 'PAYOR', data['PAYOR'][0], 'PAYOR_BILL',data['SCA_FLAG'][0])
            data['STATE_BILL'] = search_and_get_first_value(df_snowflake, 'STATE', data['STATE'][0], 'STATE_BILL',data['SCA_FLAG'][0])
            data['SUBS_BILL'] = search_and_get_first_value(df_snowflake, 'SUBSCRIBER', data['SUBSCRIBER'][0], 'SUBS_BILL',data['SCA_FLAG'][0])
            data['GROUP_BILL'] = search_and_get_first_value(df_snowflake, 'GROUP_NUMBER', data['GROUP_NUMBER'][0], 'GROUP_BILL',data['SCA_FLAG'][0])
            data['FUNDED_BILL'] = search_and_get_first_value(df_snowflake, 'FUNDED_STATUS', data['FUNDED_STATUS'][0], 'FUNDED_BILL',data['SCA_FLAG'][0])
            data['CLAIM_AMOUNT_PAID'] = data.apply(calculate_claim_amount_paid, axis=1)

            # This is the tarjet variable - only for train pursoses
            data['PAID_CLAIM_$'] = search_specific_and_get_first_value(df_snowflake, data['CLIENT_NAME'][0], data['PREFIX'][0],
                                                                       data['PAYOR'][0], data['STATE'][0], data['SUBSCRIBER'][0],
                                                                       data['GROUP_NUMBER'][0], data['FUNDED_STATUS'][0], 'PAID_CLAIM_$')
            # Only for unique propouses
            data.iloc[1] = data.iloc[0]

            return data
        except Exception as e:
            raise Exception(f"Error loading data to DataFrame: {str(e)}")

    def include_columns(self, data: DataFrame) -> DataFrame:
        """
        Include columns from the DataFrame.

        Parameters:
            data (DataFrame): The DataFrame containing the data
            to be processed.

        Returns:
            DataFrame: The DataFrame with the select columns.

        Process:
            - Select the specified columns from the DataFrame.
            - Returns the DataFrame with the selected columns.
        """
        _columns_to_include = ['PREFIX_$', 'PAYOR_$', 'STATE_$', 'SUBS_$',
                               'GROUP_$', 'FUNDED_$', 'DEDUCTIBLE',
                               'OUT_OF_POCKET', 'CO_INSURANCE', 'OON_BENEFITS',
                               'SCA_FLAG', 'MASTER_COLLECTED',
                               'MULTIPLAN_FLAG', 'POLICY_TYPE',
                               'CLIENT_NAME', 'CLAIM_AMOUNT_PAID', 'VOB_ID']

        try:
            data = data[_columns_to_include]
            return data
        except KeyError:
            raise KeyError("Column not found (Colums_to_include)")
        except Exception as e:
            raise Exception(f"Error in columns to include: {e}")

    def impute_null_values(self, data: DataFrame,
                           imputers: Dict[str, SimpleImputer]) -> DataFrame:
        """
        Impute null values in selected columns of the DataFrame.

        Parameters:
            data (DataFrame): The DataFrame containing the data to be imputed.
            imputers (Dict[str, SimpleImputer]): A dictionary mapping column names to SimpleImputer objects.

        Returns:
            DataFrame: The DataFrame with null values imputed.

        Process:
            - Applies the specified SimpleImputers to the selected columns in the DataFrame.
            - Returns the DataFrame with null values imputed.
        """
        # Copy the DataFrame to avoid modifying the original one
        imputed_data = data.copy()
        try:
            # Apply simple imputer to the specified columns
            for col, imputer in imputers.items():
                # If columns exist
                if col in data.columns:
                    imputed_data.loc[imputed_data[col].isna(), [col]] = imputer

            return imputed_data

        except KeyError:
            raise KeyError("Column not found: impute null values")

        except Exception as e:
            raise Exception(f"Error imputing null values: {str(e)}")

    def type_data(self, data: DataFrame) -> DataFrame:
        """
        Type the columns of the DataFrame.

        Parameters:
            data (DataFrame): The DataFrame containing the data to be typed.

        Returns:
            DataFrame: The DataFrame with the typed columns.

        Process:
            - Types the columns of the DataFrame according to their specified types.
            - Returns the DataFrame with the typed columns.
        """
        try:
            # Define the column types dictionary based on the provided column data types
            column_types = {
                'PREFIX_$': float,
                'PAYOR_$': float,
                'STATE_$': float,
                'SUBS_$': float,
                'GROUP_$': float,
                'FUNDED_$': float,
                'MASTER_COLLECTED': float
            }

            # Convert the columns to the desired data types
            for col, dtype in column_types.items():
                if col in data.columns:
                    try:
                        data[col] = data[col].astype(dtype, errors='ignore')
                    except (ValueError, TypeError):
                        data[col] = None
                        data[col].astype(dtype, errors='ignore')

            return data

        except Exception as e:
            raise Exception(f"Error typing data: {str(e)}")

    def transform_columns(self, data: DataFrame) -> DataFrame:
        """
        Transform some columns in the DataFrame.

        Parameters:
            data (DataFrame): The DataFrame containing the data to be processed.

        Returns:
            DataFrame: The DataFrame transformed.

        Process:
            - Apply necessary transformations in the DataFrame.
            - Returns the DataFrame with the problems solved.
        """
        try:
            # Do this for don't change the normal flow of next steps of data
            data.rename(columns={"STATE_$": "REGION_$"}, inplace=True)
            data.rename(columns={"MASTER_COLLECTED": "WATERFALL RESULT"},
                        inplace=True)
            data['SCA_FLAG'] = data['SCA_FLAG'].replace({'True': 1, 'False': 0.0,
                                                         'Yes': 1.0, 'No': 0.0})
            data['SCA_FLAG'] = data['SCA_FLAG'].astype(float)
            data['MULTIPLAN_FLAG'] = data['MULTIPLAN_FLAG'].astype(str, errors='ignore').replace({'True': 1.0, 'False': 0.0, 'Yes': 1.0, 'No': 0.0})
            data['MULTIPLAN_FLAG'] = data['MULTIPLAN_FLAG'].astype(float)
            data['OON_BENEFITS'] = data['OON_BENEFITS'].astype(str, errors='ignore').replace({'True': 1.0, 'False': 0.0, 'Yes': 1.0, 'No': 0.0})
            data['OON_BENEFITS'] = data['OON_BENEFITS'].astype(float)
            data = data.replace({True: 1.0, False: 0.0})

            return data

        except KeyError as e:
            raise KeyError(f"Column not found (Transform Column): {e}")
        except Exception as e:
            raise Exception(f"Error in transform columns: {str(e)}")

    def exclude_columns(self, data: DataFrame) -> DataFrame:
        """
        Exclude columns from the DataFrame.

        Parameters:
            data (DataFrame): The DataFrame containing the data to be processed.

        Returns:
            DataFrame: The DataFrame without the excluded columns.

        Process:
            - Drops the specified columns from the DataFrame.
            - Returns the DataFrame without the excluded columns.
        """
        columns_to_exclude = ['CLIENT_NAME', 'CLAIM_AMOUNT_PAID', 'VOB_ID']

        try:
            data = data.drop(columns=columns_to_exclude)
            return data
        except KeyError as e:
            raise KeyError(f"Error excluding columns: {str(e)}")
        except Exception as e:
            raise Exception(f"Exclude columns error: {e}")

    def scale_values(self, data: DataFrame, scalers: StandardScaler) -> DataFrame:
        """
        Scale values in selected columns of the DataFrame.

        Parameters:
            data (DataFrame): The DataFrame containing the data to be scaled.
            StandardScaler: StandardScaler object.

        Returns:
            DataFrame: The DataFrame with scaled values.

        Process:
            - Applies the specified StandardScalers to the selected columns in the DataFrame.
            - Returns the DataFrame with scaled values.
        """
        try:

            # Get the numeric columns to be scaled
            numeric_cols = data.select_dtypes(include='number').columns

            # Apply the column transformer to the DataFrame
            scaled_data = scalers.transform(data[numeric_cols])

            # Create a new DataFrame with the scaled numeric columns
            scaled_df = pd.DataFrame(scaled_data, columns=numeric_cols)

            return scaled_df

        except KeyError as e:
            raise KeyError(f"Columns not found in the scaler during fit: {e}")
        except NameError as e:
            raise NameError(f"Problem with the columns for scaling: {e}")
        except Exception as e:
            raise Exception(f"Error scaling values: {str(e)}")

    def model_predict(self, data: DataFrame, model: object) -> DataFrame:
        """
        Run a model and make predictions with the provided datasets.

        Parameters:
            data (DataFrame): Data features (input variables).
            model (object): Trained model.

        Returns:
            pred (DataFrame): Predicted data.

        Process:
            - Makes predictions on the testing data.
        """
        try:
            pred = model.predict(data)
            return pred

        except ValueError as e:
            raise ValueError(f"Model input does not match the expected shape or dtype:{e}")

        except TypeError as e:
            raise TypeError(f"Incompatible data type for the model: {e}")

        except Exception as e:
            raise Exception(f"Error running and predicting model: {str(e)}")

    def model_predict_proba(self, data: DataFrame, model: object) -> DataFrame:
        """
        Run a model and make predictions with the provided datasets.

        Parameters:
            data (DataFrame): Data features (input variables).
            model (object): Trained model.

        Returns:
            pred (DataFrame): Predicted data.

        Process:
            - Makes predictions on the testing data.
        """
        try:
            pred = model.predict_proba(data)
            pred = np.tile(pred, (data.shape[0], 1))
            return pred

        except ValueError as e:
            raise ValueError(f"Model input does not match the expected shape or dtype:{e}")

        except TypeError as e:
            raise TypeError(f"Incompatible data type for the model: {e}")

        except Exception as e:
            raise Exception(f"Error running and predicting model: {str(e)}")

    def create_prediction_dataframe(self, data: pd.DataFrame,
                                    prediction_data_pt_sca: pd.DataFrame,
                                    prediction_data_prob_sca: pd.DataFrame,
                                    prediction_data_pt_nsca: pd.DataFrame,
                                    prediction_data_prob_nsca: pd.DataFrame,
                                    vob: tuple) -> pd.DataFrame:
        """
        Create a new DataFrame with 'claim_id', 'prediction', and 'prediction_date' columns.

        Parameters:
            data (pd.DataFrame): The DataFrame containing all columns.
            prediction_data_pt (pd.DataFrame): The DataFrame containing the prediction values about pt.
            prediction_data_prob (pd.DataFrame): The DataFrame containing the prediction values about prob.

        Returns:
            pd.DataFrame: The new DataFrame with 'claim_id', 'prediction', and 'prediction_date' columns.

        Process:
            - Selects 'CLAIM_ID' from the 'data' DataFrame.
            - Creates a new DataFrame with 'claim_id' and the prediction values from 'prediction_data'.
            - Adds a new column 'prediction_date' with the current date to the new DataFrame.
            - Returns the new DataFrame.
        """
        try:      
            # Values for Z-Score from test set
            mean_value = 0.2599563082571688 #np.mean(prediction_data_pt_sca)
            std_dev_value = 0.31011404122862357 #np.std(prediction_data_pt_sca)
            
            # Change values because is a regressor
            # Fill the negative prediction with 0, 
            prediction_data_pt_sca[prediction_data_pt_sca < 0] = 0
            prediction_data_pt_nsca[prediction_data_pt_nsca < 0] = 0
                  
            # Create the groups
            conditions = [
                (prediction_data_pt_sca >= 0.45),
                (prediction_data_pt_sca <= 0.06),
                (prediction_data_pt_sca >  0.06) & (prediction_data_pt_sca <  0.45)
            ]
            values = ['Scholarship Provider', 'Scholarship', 'Mid Payor']
            prediction_class_sca = np.select(conditions, values, default='Unknown')
            
            conditions = [
                (prediction_data_pt_nsca >= 0.45),
                (prediction_data_pt_nsca <= 0.06),
                (prediction_data_pt_nsca >  0.06) & (prediction_data_pt_nsca <  0.45)
            ]
            values = ['Scholarship Provider', 'Scholarship', 'Mid Payor']
            prediction_class_nsca = np.select(conditions, values, default='Unknown')
            
            # Select the maximun probability of be in the classification group
            prediction_data_prob_sca = np.max(prediction_data_prob_sca, axis=1)
            prediction_data_prob_nsca = np.max(prediction_data_prob_nsca, axis=1)
            
            # Financial Status
            conditions = [(prediction_class_sca == 'Scholarship') | (prediction_class_sca == 'Mid Payor'), (prediction_class_sca == 'Scholarship Provider')]
            values = ['Not Admitted', 'Admitted']
            financial_status_sca = np.select(conditions, values, default='Unknown')
            
            conditions = [(prediction_class_nsca == 'Scholarship') | (prediction_class_nsca == 'Mid Payor'), (prediction_class_nsca == 'Scholarship Provider')]
            values = ['Not Admitted', 'Admitted']
            financial_status_nsca = np.select(conditions, values, default='Unknown')

            # Create a new DataFrame with original variables and predictions columns
            prediction_df = pd.DataFrame({'VOB_ID': data['VOB_ID'],
                                          'CLIENT_NAME': data['CLIENT_NAME'], 
                                          'SCA_EIV_percentage': prediction_data_pt_sca, 
                                          'SCA_EIV_money': calculate_adjusted_eiv(eiv_pt=prediction_data_pt_sca,
                                                                                  vob=vob,
                                                                                  reset_day='2023-12-31'),
                                          'SCA_client_type': prediction_class_sca,
                                          'SCA_probability': prediction_data_prob_sca,
                                          'SCA_z_score':(prediction_data_pt_sca - mean_value)/ std_dev_value,
                                          'SCA_financial_status': financial_status_sca,
                                          'NSCA_EIV_percentage': prediction_data_pt_nsca, 
                                          'NSCA_EIV_money': calculate_adjusted_eiv(eiv_pt=prediction_data_pt_nsca,
                                                                                   vob=vob,
                                                                                   reset_day='2023-12-31'),
                                          'NSCA_client_type': prediction_class_nsca,
                                          'NSCA_probability': prediction_data_prob_nsca,
                                          'NSCA_z_score':(prediction_data_pt_nsca - mean_value)/ std_dev_value,
                                          'NSCA_financial_status': financial_status_nsca})
    

            # Add a new column 'prediction_date' with the current date
            current_date = datetime.datetime.now().date()
            prediction_df['prediction_date'] = current_date

            return prediction_df.round(2)

        except Exception as e:
            raise Exception(f"Error creating prediction DataFrame: {str(e)}")

    def save_data_with_cashrepository(self, data: DataFrame, table_name: str):
        """
        Save data to the TimeRepository.

        Parameters:
            data (DataFrame): The DataFrame containing the data to be saved.
            table_name (str): The name of the database table to save the data.

        Returns:
            None

        Process:
            - Uses the TimeRepository object to save the provided data in the specified table.
        """
        try:
            self.eiv_repository.save_data(data, table_name)
        except Exception as e:
            raise Exception(f"Error saving data with TimeRepository: {str(e)}")