'''
Module: mdbase.data
-------------------
Data-related functions for package MDBASE.

Content of the module

* Two key functions: Named `read_*` and reading XLSX data to pandas.DataFrame. 
* Aux class: Auxiliary functions that can modify data read to pandas.DataFrame.
* Logger class: A class that duplicates sys.stdout to a log file.
'''

import sys, os
import numpy as np
import pandas as pd


def read_single_database(
        excel_file, sheet_name, skiprows=3, delipidation=True):
    '''
    Read a single sheet from a single XLS file to a pandas.DataFrame.

    Parameters
    ----------
    excel_file : str or pathlike object
        Name of the XLS file.
    sheet_name : str
        Name of the sheet containing the data.
    skiprows : int, optional, default is 3
        Rows to skip in the sheet with the data.
        In current version of database, we should skip 3 rows.
        In the previous versions it was more - this can be adjusted here.
    delipidation : bool, optional, default is True
        If True, consider only delipidated samples.

    Returns
    -------
    df : pandas.DataFrame object
        The XLS sheet read into the dataframe.
    '''
    
    # Read file pandas.DataFrame and try to catch possible errors/exceptions
    try:
        df = pd.read_excel(
            excel_file, sheet_name, skiprows=skiprows)
    except OSError as err:
        # Something went wrong...
        print('OSError:', err)
        sys.exit()
    
    # Delipidation
    # (if delipidation argument is True, consider only delipidated samples
    if delipidation == True:
        df = df[df.Delipidation == 'Yes']
    
    # Replace comments and unknown values
    # (a) BEFORE replacements, switch off the (deprecated) silent downcasting
    # (this is necessary to avoid FutureWarning on the stdout
    pd.set_option('future.no_silent_downcasting', True)
    # (b) Replace non-numeric values
    df = df.replace('x',np.nan)
    df = df.replace('n',np.nan)
    # (c) Replace commented values = values starting with #
    df = df.replace(regex=r'^#.*', value=np.nan)
    
    # Return pd.DataFrame
    return(df)


def read_multiple_databases(
        excel_files, sheet_names, skiprows=3, delipidation=True):
    '''
    Read multiple XLS files with multiple sheets to a pandas.DataFrame.

    Parameters
    ----------
    excel_files : list of strings or pathlike objects
        Name of the XLS files.
    sheet_names : list of strings
        Name of the sheets containing the data.
    skiprows : int, optional, default is 3
        Rows to skip in the sheet with the data.
        In current version of database, we should skip 3 rows.
        In the previous versions it was more - this can be adjusted here.
    delipidation : bool, optional, default is True
        If True, consider only delipidated samples.

    Returns
    -------
    df : pandas.DataFrame object
        The XLS files/sheets read into one dataframe.
    '''
    
    # Create empty dataframe
    df = pd.DataFrame()
    
    # Read and add data from all excel_files and sheet_names
    for file in excel_files:
        for sheet in sheet_names:
            # Read given file/sheet combination to temporary dataframe
            temp_df = read_single_database(file, sheet, skiprows, delipidation)
            # Exclude empty columns from the newly read dataframe
            # (reason: concatenation of df's with empty columns is deprecated
            temp_df = temp_df.dropna(axis='columns',how='all')
            # If temp_df is not empty, concatenate the databases
            # (reason: concatenation of empty df's is deprecated
            if not(temp_df.empty):
                df = pd.concat([df, temp_df], ignore_index=True)
    
    # Return the final combined database
    return(df)

class Aux:
    '''   
    A class that contains small auxiliary functions.
    
    * The simple functions could be hard-coded in scripts using MDBASE.
    * To avoid the repeated coding, the functions are collected below.
    '''
    
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
        LengthInVivo = Aux.replace_unknown_values(df.LengthInVivo)
        OI_ave_W     = Aux.replace_unknown_values(df.OI_ave_W)
        OI_max_W     = Aux.replace_unknown_values(df.OI_max_W)
        OI_ave_U     = Aux.replace_unknown_values(df.OI_ave_U)
        OI_max_U     = Aux.replace_unknown_values(df.OI_max_U)
        OI_ave       = Aux.replace_unknown_values(df.OI_ave)
        OI_max       = Aux.replace_unknown_values(df.OI_max)
        
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
        
        # (0) BEFORE replacements, switch off the (deprecated) silent downcasting
        # (this is necessary to avoid FutureWarning on the stdout
        pd.set_option('future.no_silent_downcasting', True)
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



class Logger(object):
    '''
    A class that duplicates sys.stdout to a log file.
    
    * Source: https://stackoverflow.com/q/616645
    * The source was slightly modified & corrected: buff=0 => buff=1
    * The class can be useful also in Spyder Console - see Usage #3 below
    
    Usage #1 (classic: open-close):
    
    >>> Log=Logger('log.out')
    >>> print('Something...')
    >>> Log.close()
    
    Usage #2 (modern: with-block):
    
    >>> with Logger('log.out'):
    >>>     print('Something...')
            
    Usage #3 (iPython, Spyder Console, copy output to a text file):
    
    >>> with Logger('log.out'):
    >>>     runfile('myprog.py')
    '''
    
    
    def __init__(self, filename="logger.txt", mode="w", buff=1):
        self.stdout = sys.stdout
        self.file = open(filename, mode, buff)
        sys.stdout = self

    
    def __del__(self):
        self.close()

    
    def __enter__(self):
        pass

    
    def __exit__(self, *args):
        self.close()

    
    def write(self, message):
        self.stdout.write(message)
        self.file.write(message)

    
    def flush(self):
        self.stdout.flush()
        self.file.flush()
        os.fsync(self.file.fileno())

    
    def close(self):
        if self.stdout != None:
            sys.stdout = self.stdout
            self.stdout = None
        if self.file != None:
            self.file.close()
            self.file = None