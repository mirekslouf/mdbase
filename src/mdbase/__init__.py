# Python package initialization file.

'''
MDbase package
--------------

Join and proces multiple XLSX files.

Simple and minimalistic, but real and working example:

>>> """ MDbase :: correlation plot """
>>> 
>>> import mdbase.io, mdbase.stats
>>> 
>>> # Define directory with databases + XLSX database files
>>> DDIR  = r'../'
>>> DBASE1 = DDIR + r'DBASE.CZ/database_2022-11-02.xlsx'
>>> DBASE2 = DDIR + r'DBASE.IT/database_it_2022-02.xlsx'
>>> DBASE3 = DDIR + r'DBASE.ES/database_es_2022-02.xlsx'
>>> 
>>> # Join all XLSX databases into one pandas.DataFrame object
>>> df = mdbase.io.read_multiple_databases(
>>>     [DBASE1,DBASE2,DBASE3],['HIPs','KNEEs'])
>>> 
>>> # Initialize plotting
>>> mdbase.stats.CorrelationPlot.set_plot_parameters(
>>>     my_rcParams = {'figure.figsize':(8/2.54,6/2.54)} )
>>> 
>>> # Define properties in the database we want to plot
>>> P1,P2 = ('OI_max_W','CI_max_W')
>>> 
>>> # Correlation plot, all experimental data + fitting with Power law model
>>> CPLOT = mdbase.stats.CorrelationPlot(df)
>>> CPLOT.correlation(P1, P2, marker='rx', label='Experimental data')
>>> CPLOT.regression(P1, P2, rtype='power', label=r'Model: $y = kx^n$')
>>> CPLOT.finalize('OI(max,W)', 'CI(max,W)')
>>> CPLOT.save('corr_oi-ci.py.png')
'''

__version__ = "0.2"
