'''
mdbase.data
-----------
Additional manipulations with data in package MDBASE.

* This package contains small auxiliary functions.
* The simple functions could be hard-coded in scripts using MDBASE.
* Nevertheless, the repeated coding of the functions would be impractical.
'''


import numpy as np


def add_normalized_OI(df):
    '''
    Add normalized OI values to database.
    
    * database = pandas.Dataframe object
    * normalized OI values = OI values divided by LenghtInVivo

    Parameters
    ----------
    df :  pandas.DataFrame object
        Original database containing all data (from joined XLS databases).

    Returns
    -------
    df : pandas.DataFrame object
        Augmented database with newly inserted columns.
    '''
    
    # (1) Replace strings representing unknown values with np.nan's
    LengthInVivo = replace_unknown_values(df.LengthInVivo)
    OI_ave_W     = replace_unknown_values(df.OI_ave_W)
    OI_max_W     = replace_unknown_values(df.OI_max_W)
    OI_ave_U     = replace_unknown_values(df.OI_ave_U)
    OI_max_U     = replace_unknown_values(df.OI_max_U)
    OI_ave       = replace_unknown_values(df.OI_ave)
    OI_max       = replace_unknown_values(df.OI_max)
    
    # (2) Add colums with normalized OI's
    df['OI_ave_W_n'] = OI_ave_W / LengthInVivo
    df['OI_max_W_n'] = OI_max_W / LengthInVivo
    df['OI_ave_U_n'] = OI_ave_U / LengthInVivo
    df['OI_max_U_n'] = OI_max_U / LengthInVivo
    df['OI_ave_n']   = OI_ave  / LengthInVivo
    df['OI_max_n']   = OI_max   / LengthInVivo
    
    # (3) Return the modified database
    return(df)


def replace_unknown_values(
        df, unknown_values=[['?','x','n','???']]):
    '''
    In DataFrame *df* replace all unknown values with np.nan.

    Parameters
    ----------
    df : pandas DataFrame
        Database in which the replacement should be made.
    unknown_values : list of str, optional
        List of strings that represent unknown values.
        In our database, these strings are, for example: '?','n','x'...
        
    Returns
    -------
    ds : pandas Dataframe
        Database with unknown values replaced by np.nan's.
        
    Note
    ----
    This function is used, among others, in data.add_normalized_OI.
    '''
    
    # (1) Get length of array containing unknown values
    n = len(unknown_values)
    # (2) Create an array with equivalent lenght with np.nan values
    replacements = np.full(n, np.nan)
    # (3)) Do the replacement = replace all 
    ds = df.replace(unknown_values, replacements)
    # (4) Return the modified array
    return(ds)


def subdatabase_without_missing_values(df, properties):
    '''
    Create a sub-database with selected properties and exclude missing values.

    Parameters
    ----------
    df : pandas.DataFrame object
        Database, from which we will select a sub-database.
    properties : list of strings
        Names of the properties/columns that should be in the sub-database.

    Returns
    -------
    df : pandas.DataFrame object
        A sub-database that contains only
        selected properties (= selected columns)
        and within the selected properties/columns no missing values.
    '''
    ds = df[properties]
    ds = ds.dropna()
    return(ds)


def exclude_too_early_explants(df, minimum_in_vivo=0.1):
    '''
    Auxiliary function: Exclude explants with too short LenghtInVivo.
    '''
    ds = df[df.FinalEvaluation != 'new_liner']
    ds = ds[ds.LengthInVivo >= minimum_in_vivo]
    return(ds)


def exclude_too_high_oxidations(df, OI_limit = 3):
    '''
    Auxiliary function: Exclude explants with too high OI_max.
    '''
    ds = df[df.OI_max < OI_limit]
    return(ds)