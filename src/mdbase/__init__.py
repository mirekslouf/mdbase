'''
mdbase package
--------------
Join and proces multiple XLSX files.

Simple and minimalistic, but real and working example:

>>> """ MDbase :: correlation plot """
>>> 
>>> import mdbase.io, mdbase.stats
>>> 
>>> # Define directory with databases + XLSX database files
>>> DDIR  = r'../'
>>> DBASE1 = DDIR + r'DBASE/CZ/database_cz_2023-09-20.xlsx'
>>> DBASE2 = DDIR + r'DBASE/IT/database_it_2023-02-15.xlsx'
>>> DBASE3 = DDIR + r'DBASE/ES/database_es_2023-02-15.xlsx'
>>> 
>>> # Join all XLSX databases into one pandas.DataFrame object
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

__version__ = "0.3.2"
