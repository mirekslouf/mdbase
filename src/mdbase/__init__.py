'''
mdbase package
--------------
Join and proces multiple XLS files.

List of modules:

* mdbase.io = read multiple XLS files into one single pandas.DataFrame
* mdbase.data = additional, auxiliary functions for data in pandas.DataFrame
* mdbase.stats = key module; statistical calculations and plotting of the data

Simple and minimalistic, but real and working example:

>>> """ MDbase :: correlation plot """
>>> 
>>> import mdbase.io, mdbase.stats
>>> 
>>> # Define directory with databases + XLS database files
>>> DDIR  = r'../../'
>>> DBASE1 = DDIR + r'DBASE/CZ/database_cz_2024-03-11.xlsm'
>>> DBASE2 = DDIR + r'DBASE/IT/database_it_2024-03-11.xlsm'
>>> DBASE3 = DDIR + r'DBASE/ES/database_es_2024-03-11.xlsm'
>>> 
>>> # Join all XLS databases into one pandas.DataFrame object
>>> df = mdbase.io.read_multiple_databases(
>>>     excel_files=[DBASE1,DBASE2,DBASE3],
>>>     sheet_names=['HIPs','KNEEs'])
>>> 
>>> # Define properties in the database we want to correlate and plot
>>> P1,P2 = ('OI_max_W','CI_max_W')
>>> 
>>> # Correlation plot, all experimental data + fitting with Power law model
>>> CPLOT = mdbase.stats.CorrelationPlot(df)
>>> CPLOT.correlation(P1, P2, marker='rx', label='Experimental data')
>>> CPLOT.regression(P1, P2, rtype='power', label=r'Model: $y = kx^n$')
>>> CPLOT.finalize('OI(max,W)', 'CI(max,W)')
>>> CPLOT.save('corr_oi-ci.py.png')
'''

__version__ = "0.3.3"
