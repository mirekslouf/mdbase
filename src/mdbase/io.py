'''
mdbase.io
-----------
Input/output functions for package MDBASE.

* MDBASE joins multiple XLSX databases into one pandas.DataFrame object.
* This module provides functions for XLSX inputs and TXT outputs.
'''
    
import sys,os
import numpy as np
import pandas as pd
import mdbase.const

def read_single_database(excel_file, sheet_name, delipidation=True):   
    # Read file pandas.DataFrame and try to catch possible errors/exceptions
    try:
        df = pd.read_excel(
            excel_file, sheet_name, skiprows=mdbase.const.XLS_SKIPROWS)
    except OSError as err:
        # Something went wrong...
        print('OSError:', err)
        sys.exit()
    # Delipidation
    if delipidation == True:
        df = df[df.Delipidation == 'Yes']
    # Non-numeric values
    df = df.replace('x',np.nan)
    df = df.replace('n',np.nan)
    # Return pd.DataFrame
    return(df)

def read_multiple_databases(excel_files, sheet_names, delipidation=True):
    df = pd.DataFrame()
    for file in excel_files:
        for sheet in sheet_names:
            temp = read_single_database(file, sheet, delipidation)
            df = pd.concat([df, temp])
    return(df)

class Logger(object):
    '''
    Class that duplicates sys.stdout to a log file.
    
    * source: https://stackoverflow.com/q/616645
    * slightly modified & corrected buff=0 => buff=1
    * it is useful also in Spyder - see Usage #3 below
    
    Usage #1 (classic: open-close):
        Log=Logger('log.out')
        print('Something...')
        Log.close()
    
    Usage #1 (modern: with-block):
        with Logger('log.out'):
            print('Something...')
            
    Usage #3 (Spyder console, copy output to a text file):
        with Logger('log.out'): runfile('myprog.py')
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
