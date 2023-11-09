'''
mdbase.io
---------
Input/output functions for package MDBASE.

* MDBASE joins multiple XLSX databases into one pandas.DataFrame object.
* This module provides functions for XLSX inputs and TXT outputs.
'''

    
import sys,os
import numpy as np
import pandas as pd


def read_single_database(
        excel_file, sheet_name, skiprows=3, delipidation=True):
    '''
    Read a single sheet from a single XLSX file to a pandas.DataFrame.

    Parameters
    ----------
    excel_file : str or pathlike object
        Name of the XLSX file.
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
        The XLSX sheet read into the dataframe.
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
    
    # Replace non-numeric values
    df = df.replace('x',np.nan)
    df = df.replace('n',np.nan)
    
    # Replace commented values = values starting with #
    df = df.replace(regex=r'^#.*', value=np.nan)
    
    # Return pd.DataFrame
    return(df)

def read_multiple_databases(
        excel_files, sheet_names, skiprows=3, delipidation=True):
    '''
    Read multiple XLSX files with multiple sheets to a pandas.DataFrame.

    Parameters
    ----------
    excel_files : list of strings or pathlike objects
        Name of the XLSX files.
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
        The XLSX files/sheets read into one dataframe.
    '''
    
    # Create empty dataframe
    df = pd.DataFrame()
    
    # Read and add data from all excel_files and sheet_names
    for file in excel_files:
        for sheet in sheet_names:
            temp = read_single_database(file, sheet, skiprows, delipidation)
            df = pd.concat([df, temp], ignore_index=True)
    
    # Return the final combined database
    return(df)



class Logger(object):
    '''
    A class that duplicates sys.stdout to a log file.
    
    * source: https://stackoverflow.com/q/616645
    * slightly modified & corrected buff=0 => buff=1
    * it is useful also in Spyder - see Usage #3 below
    
    Usage #1 (classic: open-close):
    
    >>> Log=Logger('log.out')
    >>> print('Something...')
    >>> Log.close()
    
    Usage #2 (modern: with-block):
    
    >>> with Logger('log.out'):
    >>>     print('Something...')
            
    Usage #3 (iPython, Spyder console, copy output to a text file):
    
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
