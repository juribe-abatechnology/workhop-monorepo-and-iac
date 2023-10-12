from services.eiv_services import EIVService
from connectors.interface_connection import InterfaceConnection
from util.util import response_json, response_error_json, receive_json
from typing import List
import json
import pandas as pd
import pickle
from util.pickle_manager import PickleManager
from services.eiv_helper import check_bool_values, check_percent, \
                                check_fundingType, check_ids, \
                                check_multiplan_variable, \
                                check_quantities_vob, check_user_name


class EIVController:
    """
    Manage data and start services for cashflow prediction.

    Attributes:
        time_services (TimeService): The TimeService instance.
        cash_services (CashService): The CashService instance.
        interface_connectors (List[InterfaceConnector]): List of
        InterfaceConnector instances.

    Methods:
        predict_cashflow: Predict cashflow and return the result.

    """
    def __init__(self, interface_connectors: List[InterfaceConnection]):
        """
        Initialize the CashflowController.

        Parameters:
            interface_connectors (List[InterfaceConnection]): List of
            InterfaceConnection instances.

        Process:
            - Create TimeService and CashService instances.
            - Save the InterfaceConnection instances.
        """
        try:
            self.eiv_services = EIVService(interface_connectors)
        except Exception as e:
            raise Exception(f"Error initializing EIVController: {str(e)}")

    def handle_request(self, event, context):
        """
        To make predictions and return the result.

        Parameters:
            event (JSON): AWS Lambda event data.
            context : AWS Lambda context.

        Returns:
            dict: A dictionary with the prediction result.

        Process:
            - Catch data from the AWS Lambda event.
            - Run the predict_pipeline functions in EIV model.
            - Return the prediction result.
        """
        try:
            # Read data sent by the user
            body = self.create_dataframe_from_lambda_data(event)

        except json.JSONDecodeError as e:
            error_message = f"JSONDecodeError: {str(e)}"
            response_error = response_error_json(400, error_message)
            return response_error

        except KeyError as e:
            error_message = f"KeyError: {str(e)}"
            response_error = response_error_json(400, error_message)
            return response_error

        except ValueError as e:
            error_message = f"Error in the data entries: {str(e)}"
            response_error = response_error_json(400, error_message)
            return response_error

        except Exception as e:
            error_message = f"Data input error: {str(e)}"
            response_error = response_error_json(500, error_message)
            return response_error

        else:
            try:
                df_eiv = self.predict_pipeline(body)

            except FileNotFoundError as e:
                return response_error_json(400, str(e))

            except PermissionError as e:
                return response_error_json(400, str(e))

            except pickle.UnpicklingError as e:
                return response_error_json(400, str(e))

            except ValueError as e:
                return response_error_json(400, str(e))

            except TypeError as e:
                return response_error_json(400, str(e))

            except NameError as e:
                return response_error_json(400, str(e))

            except Exception as e:
                return response_error_json(400, str(e))

            else:
                data = []
                # Data for json
                for row in range(0, df_eiv.shape[0]):
                    row_dict = {}
                    if not body.loc[row, 'SCA']:
                        row_dict = {'OON': {
                                        'EIVPercentage': df_eiv.loc[row, 'NSCA_EIV_percentage'],
                                        'EIVValue': df_eiv.loc[row, 'NSCA_EIV_money'],
                                        'EIVClientType': df_eiv.loc[row, 'NSCA_client_type'],
                                        'PercClientType': df_eiv.loc[row, 'NSCA_probability'],
                                        'EIVZscore': df_eiv.loc[row, 'NSCA_z_score'],
                                        'FinancialStatus': df_eiv.loc[row, 'NSCA_financial_status']
                                    }}
                    else:
                        row_dict = {'SCA': {
                                        'EIVPercentage': df_eiv.loc[row, 'SCA_EIV_percentage'],
                                        'EIVValue': df_eiv.loc[row, 'SCA_EIV_money'],
                                        'EIVClientType': df_eiv.loc[row, 'SCA_client_type'],
                                        'PercClientType': df_eiv.loc[row, 'SCA_probability'],
                                        'EIVZscore': df_eiv.loc[row, 'SCA_z_score'],
                                        'FinancialStatus': df_eiv.loc[row, 'SCA_financial_status']
                                    }}
                    data.append(row_dict)

                return response_json(data)

    def create_dataframe_from_lambda_data(self, lambda_data_json) -> pd.DataFrame:

        """
        Check variables types and values, raise value errors if those are
        incorrect. Create a Pandas DataFrame from lambda data.

        Args:
            lambda_data_json (json): A dictionary containing lambda data.

        Returns:
            pd.DataFrame: A DataFrame with lambda data.

        Raises:
            ValueError: If a column is not found in the lambda data.
            TypeError: If a column doesn't have the expected data type.
        """
        _variable_types = {
            "ClientTrackingID": str,
            "ClientName": str,
            "VOBID": str,
            "SCA": bool,
            "OONBenefits": bool,
            "Subscriber": str,
            "Payor": str,
            "GroupID": str,
            "PolicyID": str,
            "FundingType": str,
            "PolicyType": str,
            "Copay": float,
            "CoinsuranceOON": float,
            "Deductible": float,
            "OutOfBucket": float,
            "State": str,
            "Multiplan": bool
        }

        body = str(lambda_data_json['body']).replace("'", '"')
        lambda_data = receive_json(body)

        data = {}

        for var_name, _ in _variable_types.items():
            if var_name not in lambda_data:
                raise KeyError(f"Column '{var_name}' not found in the input.")

        data["ClientTrackingID"] = check_ids("ClientTrackingID",
                                             lambda_data["ClientTrackingID"])
        data["ClientName"] = check_user_name(lambda_data["ClientName"])
        data["VOBID"] = check_ids("VOBID", lambda_data["VOBID"])
        data["SCA"] = check_bool_values("SCA",  lambda_data["SCA"])
        data["OONBenefits"] = check_bool_values("OONBenefits",
                                                lambda_data["OONBenefits"])
        data["Subscriber"] = check_user_name(lambda_data["Subscriber"])
        data["Payor"] = lambda_data["Payor"]
        data["GroupID"] = check_ids("GroupID", lambda_data["GroupID"])
        data["PolicyID"] = check_ids("PolicyID", lambda_data["PolicyID"])
        data["FundingType"] = check_fundingType(lambda_data["FundingType"])
        data["PolicyType"] = lambda_data["PolicyType"]
        data["Copay"] = check_percent(lambda_data["Copay"])
        data["CoinsuranceOON"] = check_percent(lambda_data["CoinsuranceOON"])
        data["Deductible"] = check_quantities_vob(lambda_data["Deductible"])
        data["OutOfBucket"] = check_quantities_vob(lambda_data["OutOfBucket"])
        data["State"] = lambda_data["State"]
        data["Multiplan"] = check_multiplan_variable(lambda_data["Multiplan"])

        df = pd.DataFrame([data])

        return df

    def predict_pipeline(self, body: pd.DataFrame) -> pd.DataFrame:
        """
        Initializes and Execute all the pipeline for prediction.

        Parameters:
            DataFrame: A DataFrame containing the data for predictions.

        Returns:
            DataFrame: predicted data from the model
        """
        # Columns used by the model
        cols = ['PREFIX_$', 'PAYOR_$', 'REGION_$', 'SUBS_$', 'GROUP_$',
                'FUNDED_$', 'OON_BENEFITS', 'WATERFALL RESULT']

        # Quantities to impute
        impute_EIV = {
                    'PREFIX_$': 0.1752023489,
                    'PAYOR_$': 0.31409723805,
                    'STATE_$': 0.28720960417,
                    'SUBS_$': 1.0,
                    'GROUP_$': 0.205473112,
                    'FUNDED_$': 0.28596408507,
                    'OON_BENEFITS': False,
                    'MASTER_COLLECTED': 0.329085900650,
                    }

        # Load models and preprocessors
        scaler_EIV = PickleManager('pickle/').load_pickle('EIV_Scaler.pkl')
        model_pt_EIV = PickleManager('pickle/').load_pickle('EIV_PT_Model.pkl')
        model_probabilities_EIV = PickleManager('pickle/').load_pickle('xgb_model.pkl')

        # Execute pipeline
        df_snowflake = self.eiv_services.load_data_from_snowflake()
        df_original = self.eiv_services.load_data_to_dataframe(body,
                                                               df_snowflake)

        df_include = self.eiv_services.include_columns(df_original)

        df_impute = self.eiv_services.impute_null_values(df_include,
                                                         impute_EIV)
        df_type = self.eiv_services.type_data(df_impute)

        df_transform = self.eiv_services.transform_columns(df_type)

        df_scale = self.eiv_services.scale_values(df_transform[cols],
                                                  scaler_EIV)

        # SCA
        df_scale['SCA_FLAG'] = 1.0
        df_sca = df_scale
        df_predict_pt_sca = self.eiv_services.model_predict(df_sca,
                                                            model_pt_EIV)

        df_predict_proba_sca = self.eiv_services.model_predict_proba(df_sca[['PREFIX_$', 'PAYOR_$', 'REGION_$',
                                                                             'GROUP_$', 'FUNDED_$', 'OON_BENEFITS']],
                                                                     model_probabilities_EIV)

        # NSCA
        df_scale['SCA_FLAG'] = -1.0
        df_nsca = df_scale
        df_predict_pt_nsca = self.eiv_services.model_predict(df_nsca,
                                                             model_pt_EIV)
        df_predict_proba_nsca = self.eiv_services.model_predict_proba(df_nsca[['PREFIX_$', 'PAYOR_$', 'REGION_$',
                                                                               'GROUP_$', 'FUNDED_$', 'OON_BENEFITS']], 
                                                                      model_probabilities_EIV)

        df_save = self.eiv_services.create_prediction_dataframe(df_original,
                                                                df_predict_pt_sca,
                                                                df_predict_proba_sca[:2],
                                                                df_predict_pt_nsca,
                                                                df_predict_proba_nsca[:2],
                                                                vob=(df_original['DEDUCTIBLE'][0],
                                                                     df_original['OUT_OF_POCKET'][0]))

        df_save = df_save.iloc[[0]]

        # Save into RDS
        self.eiv_services.save_data_with_cashrepository(df_save, 'eiv')

        return df_save
