import pandas as pd
import numpy as np
from datetime import datetime
import re


def assign_region(state):
    if state == 'FL':
        return 'ABACOF'
    elif state in ['MA', 'NH']:
        return 'ABACOA'
    elif state == 'NJ':
        return 'ABACONJ'
    else:
        return None


def extract_prefix(input_str, length):
    if isinstance(input_str, str):
        return input_str.strip()[:length].upper()
    return input_str


def search_and_get_first_value(dataframe, search_column, target_name,
                               value_column, sca_flag):

    if target_name is None:
        return None

    result = dataframe[dataframe[search_column].str.upper() == str(target_name).upper()]
    result = result[result['SCA_FLAG'].str.upper() == str(sca_flag).upper()]

    if not result.empty:
        return result.iloc[0][value_column]

    return None


def search_specific_and_get_first_value(dataframe, client_name, prefix, payor,
                                        state, subscriber, group_number,
                                        funded_status, value_column):
    querys = []

    if client_name is not None:
        querys.append(f'CLIENT_NAME.str.upper() == "{str(client_name).upper()}"')
    if prefix is not None:
        querys.append(f'PREFIX.str.upper() == "{str(prefix).upper()}"')
    if payor is not None:
        querys.append(f'PAYOR.str.upper() == "{str(payor).upper()}"')
    if state is not None:
        querys.append(f'STATE.str.upper() == "{str(state).upper()}"')
    if subscriber is not None:
        querys.append(f'SUBSCRIBER.str.upper() == "{str(subscriber).upper()}"')
    if group_number is not None:
        querys.append(f'GROUP_NUMBER.str.upper() == "{str(group_number).upper()}"')
    if funded_status is not None:
        querys.append(f'FUNDED_STATUS.str.upper() == "{str(funded_status).upper()}"')

    if len(querys) < 1:
        return None

    query = ' and '.join(querys)

    result = dataframe.query(query)

    if not result.empty:
        return result.iloc[0][value_column]

    return None


# Assuming you have a DataFrame named 'data'
# Define a custom function to apply the condition to each row
def calculate_master_collected(row):
    if pd.notnull(row['SUBS_$']) and pd.notnull(row['SUBS_CLAIMS']) and row['SUBS_CLAIMS'] > 5:
        return row['SUBS_$']
    elif pd.notnull(row['SUBS_$_PY']) and pd.notnull(row['SUBS_CLAIMS_PY']) and row['SUBS_CLAIMS_PY'] > 5:
        return row['SUBS_$_PY']
    elif pd.notnull(row['GROUP_$']) and pd.notnull(row['GROUP_CLAIMS']) and row['GROUP_CLAIMS'] > 5:
        return row['GROUP_$']
    elif pd.notnull(row['GROUP_$_PY']) and pd.notnull(row['GROUP_CLAIMS_PY']) and row['GROUP_CLAIMS_PY'] > 5:
        return row['GROUP_$_PY']
    elif pd.notnull(row['PREFIX_$']) and pd.notnull(row['PREFIX_CLAIMS']) and row['PREFIX_CLAIMS'] > 5:
        return row['PREFIX_$']
    elif pd.notnull(row['PREFIX_$_PY']) and pd.notnull(row['PREFIX_CLAIMS_PY']) and row['PREFIX_CLAIMS_PY'] > 5:
        return row['PREFIX_$_PY']
    elif pd.notnull(row['PAYOR_$']) and pd.notnull(row['PAYOR_CLAIMS']) and row['PAYOR_CLAIMS'] > 5:
        return row['PAYOR_$']
    elif pd.notnull(row['PAYOR_$_PY']) and pd.notnull(row['PAYOR_CLAIMS_PY']) and row['PAYOR_CLAIMS_PY'] > 5:
        return row['PAYOR_$_PY']
    elif pd.notnull(row['FUNDED_$']) and pd.notnull(row['FUNDED_CLAIMS']) and row['FUNDED_CLAIMS'] > 5:
        return row['FUNDED_$']
    elif pd.notnull(row['FUNDED_$_PY']) and pd.notnull(row['FUNDED_CLAIMS_PY']) and row['FUNDED_CLAIMS_PY'] > 5:
        return row['FUNDED_$_PY']
    elif pd.notnull(row['STATE_$']) and pd.notnull(row['STATE_CLAIMS']) and row['STATE_CLAIMS'] > 5:
        return row['STATE_$']
    elif pd.notnull(row['STATE_$_PY']) and pd.notnull(row['STATE_CLAIMS_PY']) and row['STATE_CLAIMS_PY'] > 5:
        return row['STATE_$_PY']
    else:
        return np.nan


# Assuming you have a DataFrame named 'data'
# Define a custom function to apply the condition to each row
def calculate_claim_amount_paid(row):
    if pd.notnull(row['CLIENT_BILL']) and pd.notnull(row['CLIENT_CLAIMS']) and row['CLIENT_CLAIMS'] > 5:
        return row['CLIENT_BILL']
    if pd.notnull(row['CLIENT_BILL_PY']) and pd.notnull(row['CLIENT_CLAIMS_PY']) and row['CLIENT_CLAIMS_PY'] > 5:
        return row['CLIENT_BILL_PY']
    elif pd.notnull(row['SUBS_BILL']) and pd.notnull(row['SUBS_CLAIMS']) and row['SUBS_CLAIMS'] > 5:
        return row['SUBS_BILL']
    if pd.notnull(row['SUBS_BILL_PY']) and pd.notnull(row['SUBS_CLAIMS_PY']) and row['SUBS_CLAIMS_PY'] > 5:
        return row['SUBS_BILL_PY']
    elif pd.notnull(row['GROUP_BILL']) and pd.notnull(row['GROUP_CLAIMS']) and row['GROUP_CLAIMS'] > 5:
        return row['GROUP_BILL']
    if pd.notnull(row['GROUP_BILL_PY']) and pd.notnull(row['GROUP_CLAIMS_PY']) and row['GROUP_CLAIMS_PY'] > 5:
        return row['GROUP_BILL_PY']
    elif pd.notnull(row['PREFIX_BILL']) and pd.notnull(row['PREFIX_CLAIMS']) and row['PREFIX_CLAIMS'] > 5:
        return row['PREFIX_BILL']
    if pd.notnull(row['PREFIX_BILL_PY']) and pd.notnull(row['PREFIX_CLAIMS_PY']) and row['PREFIX_CLAIMS_PY'] > 5:
        return row['PREFIX_BILL_PY']
    elif pd.notnull(row['PAYOR_BILL']) and pd.notnull(row['PAYOR_CLAIMS']) and row['PAYOR_CLAIMS'] > 5:
        return row['PAYOR_BILL']
    if pd.notnull(row['PAYOR_BILL_PY']) and pd.notnull(row['PAYOR_CLAIMS_PY']) and row['PAYOR_CLAIMS_PY'] > 5:
        return row['PAYOR_BILL_PY']
    elif pd.notnull(row['FUNDED_BILL']) and pd.notnull(row['FUNDED_CLAIMS']) and row['FUNDED_CLAIMS'] > 5:
        return row['FUNDED_BILL']
    if pd.notnull(row['FUNDED_BILL_PY']) and pd.notnull(row['FUNDED_CLAIMS_PY']) and row['FUNDED_CLAIMS_PY'] > 5:
        return row['FUNDED_BILL_PY']
    elif pd.notnull(row['STATE_BILL']) and pd.notnull(row['STATE_CLAIMS']) and row['STATE_CLAIMS'] > 5:
        return row['STATE_BILL']
    if pd.notnull(row['STATE_BILL_PY']) and pd.notnull(row['STATE_CLAIMS_PY']) and row['STATE_CLAIMS_PY'] > 5:
        return row['STATE_BILL_PY']
    else:
        return np.nan


def verify_data_categories(df_snowflake: pd.DataFrame,
                           feature: str,
                           column_name: str,
                           apply_filter: bool = True):
    """
    Verify the categories for PAYOR, REGION, STATE, POLICY_TYPE, PAYOR_TYPE
    of the incoming feature, if it is an allowed feature category it is
    returned otherwise an exception is raise

    Args:
        df_snowflake (pd.DataFrame): category of the feature to check
        feature (str): Orginial DataFrame from the Database with the allowed categories
        apply_filter (bool, optional): option to skip  this data verification. Defaults to True.

    Returns:
        feature (str):
    """
    # Define the allowed categories from df_snowflake
    if apply_filter:
        try:
            match column_name:
                case 'PAYOR':
                    _PAYOR_CATEGORIES = df_snowflake['PAYOR'].unique().tolist()
                    if feature.item() not in _PAYOR_CATEGORIES:
                        raise ValueError(f"Feature: {feature.item()}, not in ALLOWED PAYOR CATEGORIES")

                case 'REGION':
                    _REGION_CATEGORIES = df_snowflake['REGION'].unique().tolist()
                    if feature.item() not in _REGION_CATEGORIES:
                        raise ValueError(f"Feature {feature.item()}: not in ALLOWED REGION CATEGORIES")

                case 'STATE':
                    _STATE_CATEGORIES = df_snowflake['STATE'].unique().tolist()
                    if feature.item() not in _STATE_CATEGORIES:
                        raise ValueError(f"Feature {feature.item()}: not in ALLOWED STATE CATEGORIES")

                case 'POLICY_TYPE':
                    _POLICY_TYPE_CATEGORIES = df_snowflake['POLICY_TYPE'].unique().tolist()
                    if feature.item() not in _POLICY_TYPE_CATEGORIES:
                        raise ValueError(f"Feature {feature.item()}: not in ALLOWED POLICY_TYPE CATEGORIES")

                case 'PAYOR_TYPE':
                    _PAYOR_TYPE_CATEGORIES = df_snowflake['PAYOR_TYPE'].unique().tolist()
                    if feature.item() not in _PAYOR_TYPE_CATEGORIES:
                        raise ValueError(f"Feature {feature.item()}: not in ALLOWED PAYOR_TYPE CATEGORIES")

                case None:
                    pass

        except Exception as e:
            raise Exception(f'Error: {e}')
        else:
            return feature.item()
    else:
        return feature


def extract_and_provide_vob(vob: tuple):
    """
    This function is going to provide the vob = OOP + Deductible

    Args:
        vob (tuple): contains the original 'DEDUCTIBLE' and 'OUT_OF_POCKET'
        of the client
    Returns:
        vob (float): vob = OOP + Deductible if both are different from None,
        else zero
    """
    # Check if the tuple contains two elements
    if len(vob) != 2:
        raise ValueError('Input tuple must contain exactly two elements of VOB: Deduct + OOP')

    # Extract the values and replace None with Zero math.isnan(vob[0])
    deductible = vob[0] if vob[0] else 0
    oop = vob[1] if vob[1] else 0

    return deductible + oop


def calculate_weeks_to_reset_day(reset_day: str):
    """
    Calculate the number of weeks to reset day of the client

    Args:
        reset_day (str): in format '%Y-%m-%d'
    Return:
        weeks (int): Number of weeks to reset day

    """
    # Convert the target_date string to a datetime object
    target_date = datetime.strptime(reset_day, '%Y-%m-%d')

    # Get the current date
    current_date = datetime.now()

    # Calculate the difference in days between the target date and current date
    delta = target_date - current_date

    # Calculate the number of weeks (rounded up)
    weeks = round(delta.days / 7, 2)

    return weeks


def calculate_adjusted_eiv(eiv_pt: float, vob: tuple, reset_day='2023-12-31') -> float:
    """
    Calculate the adjusted value of EIV to the specified date (reset day)
    of the client

    Args:
        eiv_pt (float): predicted pt of the model
        reset_day (str): reset day of the insurance of the client e.g '2023-12-31'
        vob (float): $ in this case as s proxy, OOP + Deductible
    """
    # cost of the unit for CPT 97153
    cost_unit_53 = 285

    # Estimated number of hours a week of the Tx (CPT 97153)
    hrs_tx_week = 25

    # Convertion from hours to units
    conv_hr_to_units = 4

    # Calculate the number of weeks to reset day of the client
    weeks = calculate_weeks_to_reset_day(reset_day)

    # Calculate vob
    vob = extract_and_provide_vob(vob)

    # Calculate the EIV*, This can be the summation over the CPT codes(with its respectives hrs/week, cost, weeks)
    eiv_star = hrs_tx_week*conv_hr_to_units*cost_unit_53*weeks

    # Calculte the EIV money
    eiv_money = eiv_pt * eiv_star  # - vob

    return eiv_money


def check_multiplan_variable(multiplan: bool) -> bool:
    """

    Check if multiplan is of bool type or None, and handle accordingly.

    multiplan: The variable to check and convert.
    :return: multiplan if the variable is a bool, or False if it is None.
    :raises ValueError: If the variable is not a bool and not None.

    Args:
        Multiplan (bool):
    """
    if multiplan is None:
        return False
    elif isinstance(multiplan, bool):
        return multiplan
    else:
        raise ValueError(f"multiplan should be of type bool or None, but it is of type {type(multiplan).__name__}")


def check_bool_values(var_name: str, var: bool) -> bool:
    """
    Check if var -> {SCA or OONBenefits} is of bool type and handle accordingly, this
    is a required variable

    Args:
        var (bool): SCA or OONBenefits
    Returns:
        bool: var if the variable is a bool else raise ValueError
    """
    if var is None:
        return False
    elif isinstance(var, bool):
        return var
    else:
        raise ValueError(f"'{var_name}' should be of type bool, but it is of type {type(var).__name__}")


def check_fundingType(fundingType: str) -> str:
    """

    Check if a variable is in the categories {'Self funded', 'Fully Funded'} and handle accordingly.
    If the variable is None, it is cast to 'Self funded'.

    :fundingType: The variable to check and convert.
    :return: The variable if it is in the specified categories, 'Self funded' if it is None.
    :raises ValueError: If the variable is not in the specified categories.
    Args:
        fundingType (str)
    Returns:
        str:
    """
    valid_categories = {"Self funded", "Fully Funded"}

    if fundingType is None:
        return "Self funded"
    elif fundingType in valid_categories:
        return fundingType
    else:
        raise ValueError("Variable should be in categories 'Self funded' or 'Fully Funded'.")


def check_user_name(username: str) -> str:
    """
    Function to validate the names of the users, if invalid raise a 

    Args:
        username (str): 

    Returns:
        str: username
    """
    # Define a regular expression pattern to match names and surnames
    name_pattern = r'^[A-Za-z\'\-]+(?:[, ]+[A-Za-z\'\-]+)*$'

    if username is None:
        raise ValueError("Provide a valid name and lastname")
    elif not isinstance(username, str):
        raise ValueError("Invalid username")
    elif re.search(r'\d', username):
        raise ValueError(f"Invalid username, contains numbers: {username}")

    username = username.strip()
    name_parts = re.split(r'[,\s]+', username)

    if len(name_parts) < 2:
        raise ValueError("Provide user name and lastname")

    # Catch invalid names or lastnames with more than three letters repeated
    for part in name_parts:
        if re.search(r'(\w)\1{3,}', part):
            raise ValueError(f"Invalid Name or Lastname: {part}")

    # Use the re.match function to check if the input string matches the pattern
    if re.match(name_pattern, username):
        return username
    else:
        ValueError("Invalid name. The name should contain only letters and not be empty.")


def check_ids(name_id: str, id: str) -> str:
    if id is None:
        return id
    if isinstance(id, str):
        return id
    else:
        raise ValueError(f"'{name_id}' should be of type str, but it is of type {type(id).__name__}")


def check_percent(val: float) -> float:
    """
    This function is going to check the percentage value of the copay and CoinsuranceOON to be float

    Args:
        val (float): copay or CoinsuranceOON

    Raises:
        ValueError: if the value if it is negative or above 100
        ValueError: is not a valid data type

    Returns:
        float: val percentage value
    """
    if val is None:
        return val
    elif isinstance(val, float) or isinstance(val, int):
        if 0 <= val <= 100:  # if value is between [0, 100%] fixed to [0, 1] otherwise
            return val
        else:
            raise ValueError("Copay or CoinsuranceOON should be positive and [0, 100]")
    else:
        raise ValueError("Copay or CoinsuranceOON should be a float")


def check_quantities_vob(quantity_vob) -> float:
    if quantity_vob is None:
        return quantity_vob
    elif isinstance(quantity_vob, float) or isinstance(quantity_vob, int):
        if quantity_vob >= 0:
            return float(quantity_vob)
        else:
            raise ValueError("Deductible or OutOfPocket should be positive")
    else:
        raise ValueError(f"Deductible and OutOfPocket should be numeric or None, but it is of type {type(quantity_vob).__name__}")


if __name__ == "__main__":
    pass
