'''
mdbase.stats
------------
Statistical calculations and plots in MDBASE.

* In MDBASE, statistical calculations are closely connected with plotting.
* MDBASE calculates 4 different plot types + corresponding statistics:
    - Correlation plot + statistics: Pearson's r, p-values, R2 coefficients
    - Scatterplot matrix graph + statistics: Pearson's r + p-values
    - Scatterplot matrix table in the form of heatmap showing Pearson's r
    - Boxplots + statistics: p-values quantifying differences among groups    
'''

import sys
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats, scipy.optimize
import seaborn as sns
import mdbase.io as mio

class CorrelationPlot:
    
    def __init__(self, df, ax=None):
        
        # Each CorrelationPlot object contains
        # * dataset
        # * global plot parameters = rcParams
        # * fig,ax objects:
        #   for standalone plots: both fig,ax are created
        #   for multiplotss: fig is prepared externaly, ax are created
        
        # (1) Define dataset for the plot
        self.df = df
        # (2) Define figure and axes for the plot
        # (new figure and single axes if no specific axes were set
        if ax == None:
            fig,ax = plt.subplots()
            self.fig = fig
            self.ax  = ax
        # (use externally-defined figure and user-defined axes = argument ax
        else:
            self.fig = None
            self.ax = ax
        
    @classmethod
    def set_plot_parameters(self, my_rcParams):
        '''
        A class method defining global plot parameters
        in matplotlib.pyplot.rcParams format.
        
        Parameters
        ----------
        my_rcParams : dict; optional, the default is empty dictionary {}
            The dict must be formatted as mathplotlib.pyplot.rcParams,
            because it is passed to matplotlib.pyplot.rcParams.update.
            This function sets some default rcParams suitable for single plot.
            Nevertheless, the argument my_rcParams can override the defaults.
        
        Returns
        -------
        None
            BUT it redefines global variable plt.rcParams!

        Notes
        -----
        * This is a class method,
          which sets global plot parameters = matplotlib.pyplot.rcParams.
        * IMPORTANT: It must be called before preparing the actual plots,
          in order to achieve reproducible behavior in both Spyder and CLI.
        * GENERAL RULE in matplotlib: set global plot paramers BEFORE plotting.
        '''
        # (1) Set general plot style
        plt.style.use('default')
        # (2) Set default parameters
        plt.rcParams.update({
            'figure.figsize'     : (8/2.54,6/2.54),
            'figure.dpi'         : 500,
            'font.size'          : 7,
            'lines.linewidth'    : 0.8,
            'lines.markersize'   : 3,
            'axes.linewidth'     : 0.6,
            'xtick.major.width'  : 0.6,
            'ytick.major.width'  : 0.6,
            'grid.linewidth'     : 0.6,
            'grid.linestyle'     : ':',
            'legend.handlelength': 1})
        # (3) Adjust default parameters
        # (i.e. overwrite them with user-defined rcParams argument
        # (the rcParams argument is optional, default is {} => no update
        if my_rcParams != {}: plt.rcParams.update(my_rcParams)
        
    def correlation(self, P1, P2, category=None, marker='rx', label=None):
        # Test, if category was given
        # (trick: pandas.Series cannot be compared with scalar => np.any
        if np.any(category) == None:
            ds = self.df
        else:
            ds = self.df[category]
        self.ax.plot(ds[P1], ds[P2], marker, label=label)
    
    def regression(self, P1, P2, category=None, 
            rtype='linear', marker='k-', label=None,
            r_to_plot=None, p_to_plot=None, R2_to_plot=None):
        '''
        Calculate regression and add regression curve to graph/plot.
        
        * Regression = fitting of pre-defined functions to XY-data.
        * Pre-defined function is selected according to rtype argument.
        * XY-data = P1,P2 = X-data, Y-data.
        * Statistical coefficients can be added to the graph as well.

        Parameters
        ----------
        P1 : list or array
            X-values for regression.
        P2 : list or array
            Y-values for regression.
        category : bool, optional, the default is None
            Advanced option.
            The correlationPlot object (self)
            contains this function (self.regression)
            and also reference to data (self.df) = ref to pandas DataFrame.
            If category is given,
            only self.df[category] are employed in regression.
            Example: To plot all data, but fit only TKR data,
            the regression function can be called as
            `CorrelationPlot.regression(P1,P2,category=(df.Itype==THR)`.
        rtype : str, optional, default is 'linear'
            Regression type.
            Pre-defined function for regression.
            It can be one of: 'linear', 'linear_kx', 'quadratic', 'power'.
        marker : matplotlib format string, optional, the default is 'k-'
            Matplotlib format string defines the color and type of line/points.
            More details: GoogleSearch - matplotlib.pyplot.plot.
        label : str, optional, default is None
            Label that can be assigned to regression curve.
            If defined, this label will appear in the legend of the plot.
        r_to_plot : (float,float,int), optional, the default is None
            If r_to_plot contains list with three numbers (x,y,n),
            value of Pearson's r is added to graph/plot
            at position (x,y), rounded to (n) decimals.
        p_to_plot : (float,float,int), optional, the default is None
            If p_to_plot contains list with three numbers (x,y,n),
            p-value is added to graph/plot
            at position (x,y), rounded to (n) decimals.
        R2_to_plot : (float,float,int), optional, the default is None
            If R2_to_plot contains list with three numbers (x,y,n),
            R2 coefficient is added to graph/plot
            at position (x,y), rounded to (n) decimals.
            
        Returns
        -------
        None
            The output is the regression/fitting curve
            added to the self.ax object.
            Additional output are statistical coefficients
            printed to stdout.
            Yet additional (optional) output are statistical
            coefficients added to self.ax object.
        '''
        # Test, if category was given
        # (trick: pandas.Series cannot be compared with scalar => np.any
        if np.any(category) == None:
            ds = self.df
        else:
            ds = self.df[category]
        # Remove NaN values before regression
        # (scipy.optimize.curve_fit does not work with NaN's
        ds = ds[[P1,P2]]
        ds = ds.dropna()
        # Sort values
        ds = ds.sort_values(by=[P1,P2])
        # Get regression type & define regression function
        if rtype == 'linear':
            def linear(X,a,b): return(a*X + b)
            self.regression_func = linear
            self.regression_func_eq = 'y = a*x + b'
        elif rtype == 'linear_kx':
            def linear_kx(X,k): return(k*X)
            self.regression_func = linear_kx
            self.regression_func_eq = 'y = k*x'
        elif rtype == 'quadratic':
            def quadratic(X,a,b,c): return(a*X**2 + b*X + c)
            self.regression_func = quadratic
            self.regression_func_eq = 'y = ax**2 + b*x + c'
        elif rtype == 'power':
            def power(X,n,c): return(c*X**n)
            self.regression_func = power
            self.regression_func_eq = 'y = c * x**n'
        else:
            print('Unknown regression type (rtype) - no action.')    
        # Calculate regression
        X,Y = (ds[P1],ds[P2])
        par,cov = scipy.optimize.curve_fit(self.regression_func,X,Y)
        # Calculate Pearsons's coefficient r and p-value
        r_coeff,p_value = scipy.stats.pearsonr(X,Y)
        # Calculate coefficient of determination
        # R2 values: 1 = perfect, 0 = estimate~average(Y), negative = very bad 
        # https://en.wikipedia.org/wiki/Coefficient_of_determination
        Yave = np.average(Y)
        Yfit = self.regression_func(X,*par)
        SSres = np.sum((Y-Yfit)**2)
        SStot = np.sum((Y-Yave)**2)
        R2 = 1 - SSres/SStot
        # Show regression in graph
        self.ax.plot(X,self.regression_func(X,*par), marker, label=label)
        # Add statistical parameters to graph if required
        if r_to_plot != None: self.add_coeff_to_plot(r_coeff,r'$r$',*r_to_plot)
        if p_to_plot != None: self.add_coeff_to_plot(p_value,r'$p$',*p_to_plot)
        if R2_to_plot != None: self.add_coeff_to_plot(R2,r'$R^2$',*r_to_plot)
        # Print statistics to stdout
        self.print_statistics_to_stdout(par, r_coeff, p_value, R2)
        
    def add_coeff_to_plot(self, coeff, name, x_pos, y_pos, decimals):
        my_format = '.'+str(decimals)+'f'
        my_coeff  = name + ' = ' + format(coeff, my_format)
        self.ax.text(x_pos,y_pos, my_coeff, transform=self.ax.transAxes)
    
    def print_statistics_to_stdout(self, regr_params, r_coeff, p_value, R2):
        regr_params = np.array2string(
            regr_params, precision=2, floatmode='fixed')
        print(f"Regression: {self.regression_func_eq:s}", end='  ')
        print(f"reg.params = {regr_params}", end='  ')
        print(f"r = {r_coeff:.2f}", end='  ')
        print(f"p = {p_value:.3f}", end='  ')
        print(f"R2 = {R2:.2f}")
    
    def finalize(self, xlabel, ylabel,
            grid=True, legend=True, legend_loc='lower right'):
        # Obligatory arguments = XY-labels
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        # Addigional default options
        # (can be modified manually using CorrelationPlot.ax object
        self.ax.grid()
        if legend: self.ax.legend(loc=legend_loc)
        # Applied tight_layout to figure
        # (if the figure is defined = if we create standalone plot
        # (in case of multiple plots, we create just axes, not the whole fig
        if self.fig != None: 
            self.fig.tight_layout()
            
    def label(self, plot_label, xpos=-0.3, ypos=1.00, fontsize=8):
        self.ax.text(xpos, ypos, plot_label,
            fontsize=fontsize, transform=self.ax.transAxes)
        
    def save(self, output_graph='default'):
        if self.fig != None:
            if output_graph == 'default': output_graph = sys.argv[0]+'.png'
            self.fig.savefig(output_graph)
        
class ScatterplotMatrixGraph:
    
    def __init__(self, df, properties, font_scale=1.1):
        # Set SNS parameters
        sns.set_style('ticks')
        sns.set_theme(
            style='ticks', context='paper',
            palette='RdBu', font_scale=font_scale,
            rc={'figure.dpi':300})
        # Save dataframe as a property
        self.df = df
        self.properties = properties
        
    def draw(self, r_coeffs=False, p_values=False,
             r_pos=(0.1,0.9), p_pos=(0.3,0.1), r_decimals=2, p_decimals=2):
        ds = self.df[list(self.properties.keys())]
        ds = ds.dropna()
        self.grid = sns.pairplot(
            ds, kind='reg', diag_kind='kde',
            plot_kws=({'truncate':False, 'ci':95}))
        if r_coeffs or p_values:
            self._pairplot_statistics(
                r_coeffs, p_values, r_pos, p_pos, r_decimals, p_decimals)
    
    def finalize(self, ylabel_shift=0):
        # NOTE: Setting of figure.dpi and figure.figsize (as of 2022-10-31): 
        # (1) figure.dpi must be set with sns.set_theme (above in __init__)
        # (2) figure.figsize must be set with grid.fig.set_size_inches (below)
        # Other ways (such as plt.rcParams.update) yield strange results ...
        self.grid.fig.set_size_inches(16/2.54,16/2.54)
        self._pairplot_custom_labels()
        self._pairplot_align_ylabels(ylabel_shift)
        self.grid.tight_layout()
        
    def _pairplot_custom_labels(self):
        grid_size = len(self.properties)
        for i in range(grid_size):
            for j in range(grid_size):
                xlabel = self.grid.axes[i][j].get_xlabel()
                ylabel = self.grid.axes[i][j].get_ylabel()
                if xlabel in self.properties.keys():
                    self.grid.axes[i][j].set_xlabel(self.properties[xlabel])
                if ylabel in self.properties.keys():
                    self.grid.axes[i][j].set_ylabel(self.properties[ylabel])
                    
    def _pairplot_align_ylabels(self, ylabel_shift = -0.4):
        for ax in self.grid.axes[:,0]:
            ax.get_yaxis().set_label_coords(ylabel_shift,0.5)
    
    def _pairplot_statistics(self, r_coeffs, p_values,
                             r_pos, p_pos, r_decimals, p_decimals):
        '''
        Draw values of r-coefficients and p-values to the pairplot.

        Parameters
        ----------
        r_coeffs : bool
            If True, Pearson correlation coefficients r are calculated.
            The Pearson r range from +1 (perfect positive correlation)
            through 0 (no correlation) to -1 (perfect negative correlation). 
        p_values : bool
            If True, p-values are calculated.
            In this case, the p-values represent the probability
            that we would get such a strong (or stronger) correlation
            just by coincidence.
        r_pos : (float,float)
            Coordinates for drawing the r coefficient in the graph.
        p_pos : (float,float)
            Coordinates for drawing the p-values in the graph.
        r_decimals : int
            The number of decimals for r coefficients.
        p_decimals : int
            The number of decimals for p-values.

        Returns
        -------
        * None; the output are just the p-coeff and r-values in the pairplot.
        '''
        # Scipy + matplotlib: add Pearson's r to upper-left corners
        # Trick #0: for k in dict: for-cycle with dictionary returns keys
        # Trick #1: for i,k in enumerate(dict): trick0+enumerate => index+key
        # Trick #2: ax.text(x,y,s,transform=ax.transAxes) rel.coords ~ (0;1)
        # Trick #3: ax.text(*pos,...) => x,y coordinates in pos are unpacked
        # (*list and **dict = Python unpacking operators, for function calls
        for index1,column1 in enumerate(self.properties.keys()):
            for index2,column2 in enumerate(self.properties.keys()):
                (corr,pval) = scipy.stats.pearsonr(
                    self.df[column1],self.df[column2])
                if column1 != column2:
                    if r_coeffs == True:
                        self.grid.axes[index1,index2].text(
                            *r_pos, f'$r$ = {corr:.{r_decimals}f}',
                            transform=self.grid.axes[index1,index2].transAxes)
                    if p_values == True:
                        self.grid.axes[index1,index2].text(
                            *p_pos, f'$p$ = {pval:.{p_decimals}f}',
                            transform=self.grid.axes[index1,index2].transAxes)

    def save(self, output_graph='default'):
        if output_graph == 'default': output_graph = sys.argv[0]+'.png'
        # plt.tight_layout()
        plt.savefig(output_graph)
        
class CorrelationMatrixTable:
    
    def __init__(self, df, properties, rcParams={}):
        # (1) Initialize basic parameters
        # (data and properties to correlate
        self.df  = df
        self.properties = properties
        # (2) BEFORE initializing plot, update plot parameters
        # (2a) General plot style
        plt.style.use('default')
        # (2b) Default parameters
        plt.rcParams.update({
            'figure.figsize'     : (16/2.54,12/2.54),
            'figure.dpi'         : 500,
            'font.size'          : 7,
            'lines.linewidth'    : 0.8,
            'lines.markersize'   : 3,
            'axes.linewidth'     : 0.6,
            'xtick.major.width'  : 0.6,
            'ytick.major.width'  : 0.6,
            'grid.linewidth'     : 0.6,
            'grid.linestyle'     : ':',
            'legend.handlelength': 1})
        # (2c) Optional modification of default parameters
        if rcParams != {}: plt.rcParams.update(rcParams)
        # (3) AFTER parameters have been updated, initialize the plots 
        # (each CorrelationMatrixTable contains two plots - r-coeff + p-values
        fig1,ax1 = plt.subplots()
        self.fig1 = fig1
        self.ax1  = ax1
        fig2,ax2 = plt.subplots()
        self.fig2 = fig2
        self.ax2  = ax2
        
    def draw(self, 
             cmap_r='Reds', cmap_p='Blues_r', 
             decimals_r=2, decimals_p=2, cbars=True):
        # (1) Prepare data for calculations
        ds = self.df[list(self.properties.keys())]
        ds = ds.dropna()
        # (2) Prepare empty tables to save results
        n = len(self.properties)
        r_values = np.zeros((n,n))
        p_values = np.zeros((n,n))
        # (3) Calculate correlations
        for (i,column1) in enumerate(self.properties.keys()):
            for (j,column2) in enumerate(self.properties.keys()):
                (corr,pval) = scipy.stats.pearsonr(ds[column1],ds[column2])
                r_values[i,j] = round(corr,5)
                p_values[i,j] = round(pval,5)
        # (4) Prepare for plotting... 
        # (Flip rows so that the main diagonal started in upper left corner
        # (default: [0,0] = start of the main diagonal = lower left corner
        r_values = np.flipud(r_values)
        p_values = np.flipud(p_values)
        # (5a) Draw cmatrix for r-values = sns.heatmap
        # ...draw cmatrix = heatmap
        my_format = "."+str(decimals_r)+"f"
        sns.heatmap(data=r_values, ax=self.ax1,
            annot=True, fmt=my_format, cmap=cmap_r, cbar=cbars,
            linecolor='white', linewidth=2)
        # (5b) Draw cmatrix for p-values = sns.heatmap with custom colormap
        # ...draw cmatrix = heatmap
        my_format = "."+str(decimals_p)+"f"
        sns.heatmap(data=p_values, ax=self.ax2,
            annot=True, fmt=my_format, cmap=cmap_p, cbar=cbars,
            linecolor='white', linewidth=2)
        
    def finalize(self):
        # Prepare labels
        # (labels for y-axis must be reversed - like the rows
        my_xticklabels = self.properties.values()
        my_yticklabels = list(reversed(list(self.properties.values())))
        # Set limits, ticklabels...
        n = len(self.properties)
        for ax in (self.ax1, self.ax2):
            ax.set_ylim(0,n)
            ax.set_xticklabels(my_xticklabels, rotation='vertical')
            ax.set_yticklabels(my_yticklabels, rotation='horizontal')
        # Final adjustments
        for fig in (self.fig1,self.fig2):
            fig.tight_layout()

    def save(self, output_table_r='default', output_table_p='default'):
        if output_table_r == 'default': output_table_r = sys.argv[0]+'_1r.png'
        if output_table_p == 'default': output_table_p = sys.argv[0]+'_2p.png'
        self.fig1.savefig(output_table_r)
        self.fig2.savefig(output_table_p)

class BoxPlot:
    
    def __init__(self, df, rcParams={}, ax=None):
        # (1) Define dataset for the plot
        self.df = df
        # (2) Optional modification of default parameters
        if rcParams != {}: plt.rcParams.update({rcParams})
        # (3) Define figure and axes for the plot
        # (new figure and single axes if no specific axes were set
        if ax == None:
            fig,ax = plt.subplots()
            self.fig = fig
            self.ax  = ax
        # (use externally-defined figure and user-defined axes = argument ax
        else:
            self.fig = None
            self.ax = ax
    
    @classmethod
    def set_plot_parameters(cls, my_rcParams={}):
        '''
        A class method defining global plot parameters
        in matplotlib.pyplot.rcParams format.
        
        Parameters
        ----------
        my_rcParams : dict; optional, the default is empty dictionary {}
            The dict must be formatted as mathplotlib.pyplot.rcParams,
            because it is passed to matplotlib.pyplot.rcParams.update.
            This function sets some default rcParams suitable for single plot.
            Nevertheless, the argument my_rcParams can override the defaults.
        
        Returns
        -------
        None
            BUT it redefines global variable plt.rcParams!

        Notes
        -----
        * This is a class method,
          which sets global plot parameters = matplotlib.pyplot.rcParams.
        * IMPORTANT: It must be called before preparing the actual plots,
          in order to achieve reproducible behavior in both Spyder and CLI.
        * GENERAL RULE in matplotlib: set global plot paramers BEFORE plotting.
        '''
        # (1) Set general plot style
        sns.set_style('whitegrid')
        # (2) Set default parameters
        plt.rcParams.update({
            'figure.figsize'     : (6/2.54,6/2.54),
            'figure.dpi'         : 300,
            'font.size'          : 8,
            'lines.linewidth'    : 0.6,
            'lines.markersize'   : 4,
            'axes.linewidth'     : 0.6,
            'xtick.major.width'  : 0.6,
            'ytick.major.width'  : 0.6,
            'grid.linewidth'     : 0.6,
            'grid.linestyle'     : ':'})
        # (3) Adjust default parameters
        # (i.e. overwrite them with user-defined rcParams argument
        # (the rcParams argument is optional, default is {} => no update
        if my_rcParams != {}: plt.rcParams.update(my_rcParams) 
    
    def add_boxes(self, x, y, categories, colors, width=0.5):
        sns.boxplot(
            data=self.df, x=x, y=y,
            order=categories, palette=colors, width=0.5, ax=self.ax)
    
    def label(self, plot_label, xpos=-0.3, ypos=1.00, fontsize=10):
        self.ax.text(xpos, ypos, plot_label,
            fontsize=fontsize, transform=self.ax.transAxes)
    
    def finalize(self, xlabel, ylabel, xlabelpad=None, ylabelpad=None):
        self.ax.set_xlabel(xlabel, labelpad=xlabelpad)
        self.ax.set_ylabel(ylabel, labelpad=ylabelpad)        
        if xlabelpad != 0: self.ax
        if self.fig != None: self.fig.tight_layout()
    
    def save(self, output_graph='default'):
        if output_graph == 'default': output_graph = sys.argv[0]+'.png'
        self.fig.savefig(output_graph)

    def statistics(self, X, Y, CATS, output_stats='default'):
        # Name of TXT file with output statistics that corresponds to BoxPlot
        if output_stats == 'default': output_stats = sys.argv[0]+'.txt'
        # Start writing to both standard output and output_stats file
        logfile = mio.Logger(output_stats)
        # Calulate and print statistics
        print('Correlation matrix table (p-values)')
        print('-----------------------------------')
        for category1 in CATS:
            print(f'{category1:8s}', end='')
            for category2 in CATS:
                xdata = self.df[Y][self.df[X] == category1]
                ydata = self.df[Y][self.df[X] == category2]
                t,p = scipy.stats.ttest_ind(xdata, ydata, equal_var = True)
                print(f'{p:8.4f}', end=' ')
            print()
        # Close dual output
        logfile.close()
    