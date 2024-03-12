'''
mdbase.stats
------------
Statistical calculations and plotting in MDBASE.

* In MDBASE, statistical calculations and plotting are connected.
* Current version of MDBASE calculates 4 different plot types + statistics:
    - Correlation plot + statistics: Pearson's r, p-values, R2 coefficients
    - Scatterplot matrix graph + statistics: Pearson's r + p-values
    - Scatterplot matrix tables (two heatmaps with Pearson's r + p-values')
    - Boxplots + statistics: p-values quantifying differences among groups
    
Important technical note - plot settings:

* mdbase.stats set some default reasonable parameters for each plot.
* In fact the program modifies global variable matplotlib.pyplot.rcParams.
* The rcParams are modified in three steps:
    - The default rcParams are auto-pre-set in PlotParameters class.
    - In each plot initialization, the defaults are slightly auto-adjusted.
    - Moreover, in plot initialization, the user can modify my_rcParams arg.
* The exception is ScatterplotMatrixGraph class:
    - The scatterplot matrix graph is somewhat specific plot type in seaborn.
    - The use sns-parameters is more reliable than the use of rcParams.
    - The user can modify selected sns params during the plot initialization.
* DPI of the final image:
    - DPI=100 is auto-pre-set for all plots (for showing in Spyder/Jupyter).
    - DPI=300 is auto-pre-set (and can be changed) during the saving of a plot.
'''


import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats, scipy.optimize
import seaborn as sns
import mdbase.io as mio

class PlotParameters:
    '''
    Global plot parameters.
    
    * PlotParametrs methods modify global variable matplotlib.pyplot.rcParams.
    * For single plots, the methods are auto-called during plot initialization.
    * For multiplots, call the method manually BEFORE creating fig,axes.  
    '''


    @staticmethod
    def set_plot_parameters(my_rcParams={}):
        '''
        Set global plot parameters.

        Parameters
        ----------
        my_rcParams : dict, optional, default is{}
            Dictionary with format of matplotlib.pyplot.rcParams.
            If not given, some suitable defaults are employed.
            Some of the defaults are prepared within sister function
            mdbase.stats.PlotParameters.set_general_plot_parameters.
            The remaining defaults are (auto-)set during plot initializations.

        Returns
        -------
        None
            The result is the change of global settings/dict
            matplotlib.pyplot.rcParams.
        '''
        # (1) Set general plot parameters
        PlotParameters.set_general_plot_parameters()
        # (2) Adjust default parameters
        # (i.e. overwrite them with user-defined rcParams argument
        # (the rcParams argument is optional, default is {} => no update
        if my_rcParams != {}: plt.rcParams.update(my_rcParams)
    
    
    @staticmethod
    def set_general_plot_parameters():
        '''
        Set some basic/general/universal/reasonable global plot parameters.

        Returns
        -------
        None
            The result is the change of global settings/dict
            matplotlib.pyplot.rcParams.
        '''
        # (1) Set general plot style
        plt.style.use('default')
        # (2) Set default parameters
        plt.rcParams.update({
            'figure.figsize'     : (10/2.54,10/2.54),
            'figure.dpi'         : 300,
            'font.size'          : 7,
            'lines.linewidth'    : 0.8,
            'lines.markersize'   : 3,
            'axes.linewidth'     : 0.6,
            'xtick.major.width'  : 0.6,
            'ytick.major.width'  : 0.6,
            'grid.linewidth'     : 0.6,
            'grid.linestyle'     : ':',
            'legend.handlelength': 1})


class PlotSaver:
    '''
    Save a plot with a supplied name or a suitable default name.
    
    * PLotSaver is used/called in most plotting classes below.
    * It saves all plots in a defined way = with a suitable filename and DPI.
    * The filename is either supplied as argument or
      created accorging to the name of launcher script 
      (considering also Jupyter). 
    '''
    
    @staticmethod
    def save(output_graph='default', dpi=300):
        '''
        Save a plot with a suplied name or a suitable default name.

        Parameters
        ----------
        output_graph : str, optional, default is 'default'
            Name of the output graph, such as 'something.png'.
            If not given, some suitable default filename will be created.
            The output filename depends on the environment - see code below.
        dpi : int, optional, default is 300
            DPI resolution of the saved plot.
            
        Returns
        -------
        None
            The output is the plot saved in a file.
        
        Notes
        -----
        The default output will be
        either [PY-script-name.png] (if the plot was created by PY-scipt)
        or [my_plot_XXX_nb.png] (if the plot was created within Jupyter).
        '''
        
        # Get default output filename if it was not specified.
        if output_graph == 'default':
            calling_script = sys.argv[0]
            if calling_script.endswith('ipykernel_launcher.py'):
                # Calling script is a IPYNB-notebook (Jupyter),
                # whose name is difficult to get.
                # => use a standard filename [my_plot_XXX.nb.png]
                # => this name will be created by an external function
                output_graph = PlotSaver.get_unique_filename()
            else:
                # Calling script is PY-script (CLI, Python, iPython),
                # the output finename will be [calling_script.py.png].
                output_graph = calling_script + '.png'
        
        # Save the plot (with DPI given by *dpi* argument).
        plt.savefig(output_graph, dpi=dpi)


    @staticmethod
    def get_unique_filename(basic_name='my_plot', ext1='.nb', ext2='.png'):
        '''
        Get some suitable default filename for an output graph.
        
        Parameters
        ----------
        basic_name : str, optional, default is 'my_plot'
            The basic name of the output graph.
        ext1 : str, optional, default is '.nb'
            The 1st extention of the output graph.
            The .nb value indicates that the output comes from a notebook.
        ext2 : str, optional, default is '.png'
            The 2nd extension of the output graph.
            The '.png' is used as a standard format.

        Returns
        -------
        filename: str
            The name of the output graph.
            The output graph will be in current working direcrory.
            If the defaults are used, the output will be 'my_plot_XXX_nb.png',
            where XXX is the first number (001,002...)
            for which a file does not exist.
            
        Notes
        -----
        The default name 'my_plot_XXX_nb.png' has a reason.
        We assume that a default name has to be created if the graph was:
        (i) created is Jupyter (that is why '.nb') as the 1st extension and
        (ii) the user did not specify the name - that is my just (my_plot). 
        '''
        
        # Initialize counter
        i = 0
        
        # Test names {basic_name + counter + png}
        # until we find a file which does not exist.
        while True:
            i += 1
            filename = basic_name + f'_{i:03}' + ext1 + ext2
            if not(os.path.exists(filename)): break
        
        # Return the unique filename.
        return(filename)



class CorrelationPlot:
    '''
    Correlation plot + corresponding statistics.
    
    The parameters below are employed during the object initialization.

    Parameters
    ----------
    df : pandas DataFrame
        The dataset, from which we will select properties to compare.
    ax : matplotlib.pyplot.axes object, optional, default is None
        If the argument is given, the plot is drawn in given axes = *ax*.
        Otherwise the plot is drawn as a new, single, separate plot.
    my_rcParams : dict, format of matplotlib.pyplot.rcParams, optional
        If the argument is given, global rcParams variable is updated.
        Example: my_rcParams={'figure.figsize':(8/2.54,5/2.54)}

    Returns
    -------
    None.
    '''
    
    
    def __init__(self, df, ax=None, my_rcParams={}):
        '''
        * Initialization of CorrelationPlot object.
        * For arguments description, see the class description above.
        * Note: some *init* parameters are auto-listed by pdoc (ignored here).
        '''
        
        # Each CorrelationPlot object contains
        # 1. dataset = dataframe
        # 2. fig,ax objects
        #    for standalone plots: both fig,ax are created
        #    for multiplotss: fig is prepared externaly, ax are created
        
        # (1) Define dataset for the plot
        self.df = df
         
        # (2) BEFORE initializing plot, update plot parameters
        # (a) Set some standard/suitable parameters for given plot type
        standard_rcParams = {
            'figure.figsize':(8/2.54,6/2.54),
            'figure.dpi':100}
        # (b) Update predefined parameters with my_rcParams argument
        my_final_rcParams = standard_rcParams|my_rcParams
        # (c) Update plot parameters
        # (we update global rcParams variable using PlotParameters class
        PlotParameters.set_plot_parameters(my_final_rcParams)

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
    
        
    def correlation(self, P1, P2, category=None,
                    marker='rx', alpha=1, label=None):
        '''
        Add a XY-correlation to CorrelationPlot
        (one plot can contain several XY-correlations).

        Parameters
        ----------
        P1 : str
            Name of X-variable to correlate
            = name of column in self.df DataFrame.
        P2 : str 
            Name of Y-variable to correlate
            = name of column in self.df DataFrame.
        category : str, optional, default is None
            If category is given, only a subset of data is used.
            Example:
            To plot only THR data, call the function as:
            `CorrelationPlot.correlation(P1,P2,category=(df.Itype=='THR'))`
        marker : str, optional, default is 'rx'
            Marker of the data, matplotlib string format.
            Examples: 'rx' = red cross, 'bs' = blue square ...
        alpha : float in interval 0--1, optional, default is 1
            Transparency of the markers; 1 = non-transparent.
        label : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None
            The output is saved in *self.ax* object.
        '''
        # Test, if category was given
        # (trick: pandas.Series cannot be compared with scalar => np.any
        if np.any(category) == None:
            ds = self.df
        else:
            ds = self.df[category]
        self.ax.plot(ds[P1], ds[P2], marker, alpha=alpha, label=label)

    
    def regression(self, P1, P2, category=None, 
            rtype='linear', marker='k-', label=None,
            r_to_plot=None, p_to_plot=None, R2_to_plot=None):
        '''
        Add a regression curve to correlation plot
        (one plot can contain several regression curves).

        Parameters
        ----------
        P1 : list or array
            X-values for regression.
        P2 : list or array
            Y-values for regression.
        category : bool, optional, the default is None
            Advanced option.
            The CorrelationPlot object (self)
            contains reference to data (self.df) = ref to pandas DataFrame.
            If category is given,
            only self.df[category] data are employed in regression.
            Example:
            To fit regression function only to TKR data,
            this function can be called as
            `CorrelationPlot.regression(P1,P2,category=(df.Itype=='THR')`.
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
            added to the *self.ax* object.
            Additional output are statistical coefficients
            printed to stdout.
            Yet additional (optional) output are statistical
            coefficients added to the plot (= to *self.ax* object).
        '''
        
        # Regression = fitting of pre-defined functions to XY-data.
        # Pre-defined function is selected according to rtype argument.
        # XY-data = P1,P2 = X-data, Y-data.
        # Statistical coefficients can be added to the graph as well.
        
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
        if r_to_plot != None:
            self._add_coeff_to_plot(r_coeff,r'$r$',*r_to_plot)
        if p_to_plot != None: 
            self._add_coeff_to_plot(p_value,r'$p$',*p_to_plot)
        if R2_to_plot != None: 
            self._add_coeff_to_plot(R2,r'$R^2$',*r_to_plot)
        # Print statistics to stdout
        self._print_statistics_to_stdout(par, r_coeff, p_value, R2)

        
    def _add_coeff_to_plot(self, coeff, name, x_pos, y_pos, decimals):
        '''
        Print selected coefficient to CorrelationPlot.
        (a private method; usually called within regression method above)

        Parameters
        ----------
        coeff : float
            Coefficient value, such as 0.88.
        name : str
            Coefficient name, such as 'r'.
        x_pos : float
            X-coordinate/position, at which the *coeff* is printed.
        y_pos : float
            X-coordinate/position, at which the *coeff* is printed.
        decimals : int
            Number of decimals for given coeff

        Returns
        -------
        None
            Given coefficient is printed in the plot (= *self.ax* object).
        '''
        # Create formatting string (such as '.2f')
        my_format = '.'+str(decimals)+'f'
        # Create the final string to print (such as 'r = 0.88')
        my_coeff  = name + ' = ' + format(coeff, my_format)
        # Print the final string from previous step to self.axes object
        self.ax.text(x_pos,y_pos, my_coeff, transform=self.ax.transAxes)

    
    def _print_statistics_to_stdout(self, regr_params, r_coeff, p_value, R2):
        '''
        Print statistics for given regression curve.
        (a private method; usually called within regression method above)

        Parameters
        ----------
        regr_params : numpy array
            Regression parameters.
        r_coeff : float
            Pearson correlation coefficient
            that quantifies the strenght of given correlation.
        p_value : float
            P-value
            that quantifies the statistical significance of given correlation.
        R2 : float
            that quantifies the strenght of given correlation.

        Returns
        -------
        None
            The result are the above parameters printed to stdout.
            
        Note
        ----
        Arguments of this function are typically obtained from
        the calling Correlationplot.regression method.
        '''
        
        # Convert regression parameter to better/printable format.
        # (the regression parameters come from calling regression function
        # (the calling function returns parameters in the form of an array
        # (the following numpy function returns the array in printable form
        regr_params = np.array2string(
            regr_params, precision=2, floatmode='fixed')
        
        # Print all parameters in some reasonable format.
        print(f"Regression: {self.regression_func_eq:s}", end='  ')
        print(f"reg.params = {regr_params}", end='  ')
        print(f"r = {r_coeff:.2f}", end='  ')
        print(f"p = {p_value:.3f}", end='  ')
        print(f"R2 = {R2:.2f}")

    
    def finalize(self, xlabel, ylabel,
            grid=True, legend=True, legend_loc='lower right'):
        '''
        Finalize the correlation plot before saving.

        Parameters
        ----------
        xlabel : str
            Label of X-axis.
        ylabel : str
            Label of Y-axis.
        grid : bool, optional, default is True
            If True, add a grid to the plot.
        legend : bool, optional, default is True
            If True, add a legend to the plot.
        legend_loc : legend-location, optional, default is 'lower right'.
            If given, the legend is placed at given location
            (otherwise it is placed automatically).
        
        Returns
        -------
        None
            The output is the modified/finalized plot.
        '''
        
        # Obligatory arguments = XY-labels
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        
        # Addigional default options
        # (can be modified manually using CorrelationPlot.ax object
        self.ax.grid()
        if legend: self.ax.legend(loc=legend_loc)
        
        # Apply tight_layout to figure
        # (if the figure is defined = if we create standalone plot
        # (in case of multiple plots, we create just axes, not the whole fig
        if self.fig != None: 
            self.fig.tight_layout()

            
    def label(self, plot_label, xpos=-0.30, ypos=1.00, fontsize=8):
        '''
        Insert a simple label into upper-left corner of the plot.

        Parameters
        ----------
        plot_label : str
            Simple text label, such as 'a' or '(a)'.
        xpos : float, optional, default is -0.30
            X-position of the label, in graph coordinates.
        ypos : float, optional,  default is 1.00
            Y-position of the label, in graph coordinates.
        fontsize : float, optional, default is 8
            Fontsize for the label.
        
        Returns
        -------
        None
            The output is the label inserted in the plot.  
        '''
        
        self.ax.text(xpos, ypos, plot_label,
            fontsize=fontsize, transform=self.ax.transAxes)

        
    def save(self, output_graph='default', dpi=300):
        '''
        Save correlation graph.

        Parameters
        ----------
        output_graph : str, optional, default is 'default'
            Name of the output graph, such as 'something.png'.
            If not given, some suitable default filename will be created.
        dpi : int, optional, default is 300
            DPI resolution of the saved plot.
            
        Returns
        -------
        None
            The output is the plot saved in a file.
        '''
        
        # Correlation plots can be used in multiplots.
        # * If the plot IS NOT a part of a multiplot (= plt object),
        #   it can be saved here,
        #   because in such a case it represents an individual file.
        # * If the plot IS a part of a multiplot  (= ax object of a fig object)
        #   it cannot be saved here, because it does not make sense.
        #   Instead, you typically save the whole fig at the end of the script,
        
        if self.fig != None:
            # Figure is NOT a part of multiplot - Ok to save to file.
            # For saving, we use a universal external function,
            # to avoid code repetition - saving is the same for all plot types.
            PlotSaver.save(output_graph, dpi)
        else:
            # Figure is a part of multiplot => just print warning.
            print('The plot is a part of a multiplot.')
            print('It makes no sense to save individual subplots.')
            print('Function ignored => save the whole figure instead!')
            


class ScatterplotMatrixGraph:        
    '''
    Scatterplot matrix graph + correspondig statistics.
    
    The parameters below are employed during the object initialization.    

    Parameters
    ----------
    df : pandas DataFrame
        The dataset, from which we will select properties to correlate.
    properties : dictionary containing pairs of strings
        The dictionary contains keys and values.
        The keys are names of the properties to correlate
        (= the names of the columns in the dataframe *df*).
        The values are names of the properties that should
        printed in the final graph.
        An example of a key/value pair in the *properties* dictionary:
        key='Hit[MPa]' and value=r'$H_{IT}$ [MPa]'
        => the key is the name of the column in *df*
        and the value will be the corresponding label drawn in the plot.      
    figsize_cm : tuple of two floats, optional, default is (16,16)
        The width and height of output image = output scatterplot matrix graph.
    font_scale : float, optional, default is 1.1
        A multiplicative coefficient that increases font size
        for better readability (the default value can be further increased).
    palette : str, name of plt or sns color(s) or palette, default is 'RdBu'
        The palette or color will be used to draw data points and lines
        in the scatterplot matrix graph.

    Returns
    -------
    None
        The final plot (including optional statistics) is drawn/saved later,
        by means of several methods (draw, finalize, save...). 
    '''


    def __init__(self, df, properties, 
                 figsize_cm = (16,16), font_scale=1.1, palette='RdBu'):
        '''
        * Initialization of ScatterplotMatrixGraph object.
        * For arguments description, see the class description above.
        * Note: some *init* parameters are auto-listed by pdoc (ignored here).
        '''
        
        # (1) Save initialization arguments as properties
        # (Dataframe with data, properties to correlate, figure size...
        
        #: Source dataset; pandas DataFrame.
        self.df = df
        
        #: Properties to correlate; list of strings.
        self.properties = properties
        
        # Figure size is inches; auto-calculated from figsize_cm argument.
        self.figsize_inches = (figsize_cm[0]/2.54,figsize_cm[1]/2.54)  
        
        # (2) Set SNS parameters for future plotting
        # (selected properties can be modified by arguments
        sns.set_style('ticks')
        sns.set_theme(
            style='ticks', context='paper',
            palette=palette, font_scale=font_scale,
            rc={'figure.dpi':100})

        
    def draw(self, r_coeffs=False, p_values=False,
             r_pos=(0.1,0.9), p_pos=(0.3,0.1), r_decimals=2, p_decimals=2):
        '''
        Draw scatterplot matrix graph.

        Parameters
        ----------
        r_coeffs : bool, optional, default is False
            If True, Pearson's r coefficients are calculated
            printed in each of the correlation subplots.
        p_values : bool, optional, default is False
            If True, p-values are calculated
            printed in each of the correlation subplots.
        r_pos : tuple of two floats, optional, default is (0.1,0.9)
            XY-coordinates (in fraction coordinates)
            where to draw Pearson's r coefficients (in correlation subplots).
        p_pos : tuple of two floats, optional, default is (0.3,0.1)
            XY-coordinates (in fraction coordinates)
            where to draw p-values (in correlation subplots).
        r_decimals : int, optional, default is 2
            Number of decimals for the printing of Pearson's r.
        p_decimals : int, optional, default is 2
            Number of decimals for the printing of p-values.

        Returns
        -------
        None
            The output (basic scatterplot matrix graph) is saved in self.grid.
            It can be finalized (self.finalize) and saved (self.save) later.
        '''
        ds = self.df[list(self.properties.keys())]
        ds = ds.dropna()
        self.grid = sns.pairplot(
            ds, kind='reg', diag_kind='kde',
            plot_kws=({'truncate':False, 'ci':95}))
        if r_coeffs or p_values:
            self._pairplot_statistics(
                r_coeffs, p_values, r_pos, p_pos, r_decimals, p_decimals)

    
    def finalize(self, ylabel_shift=0):
        '''
        Finalize scatterplot matrix graph before final showing/saving.

        Parameters
        ----------
        ylabel_shift : float, optional, default is 0
            A shift of Y-labels to well-defined position.
            If all Y-labels are shifted manually, they are aligned precisely.

        Returns
        -------
        None
            The modified plot (scatterplot matrix graph) is saved in self.grid.
            It can be saved (self.save) later.
            
        Notes
        -----
        * Finalizing included just one optional argument.
        * Most of the things is performed automatically
        '''
        # NOTE: Setting of figure.dpi and figure.figsize (as of 2022-10-31): 
        # (1) figure.dpi must be set with sns.set_theme (above in __init__)
        # (2) figure.figsize must be set with grid.fig.set_size_inches (below)
        # Other ways (such as plt.rcParams.update) yield strange results ...
        self.grid.fig.set_size_inches(self.figsize_inches)
        self._pairplot_custom_labels()
        self._pairplot_align_ylabels(ylabel_shift)
        self.grid.tight_layout()

        
    def _pairplot_custom_labels(self):
        '''
        Exchange default XY-labels in smatrix graph for custom labels.

        Returns
        -------
        None
        
        Note
        ----
        * The default and custom labels are saved in *self.properties*.
        * The self.properties contains a user-defined dictionary.
        * The dictionary is assinged to *self.properties*
          during ScatterplotMatrixGraph object initialization.
        * The keys of the dictionary are names of the properties to correlate
          (= the names of the columns in the input dataframe).
        * The values of the dictionary are names of the properties that should
          printed in the final graph.
        * An example of a key/value pair in self.properties dictionary:
          key='Hit[MPa]' and value=r'$H_{IT}$ [MPa]'
          => the key is the name of the column in the input dataframe
          and the value will be the corresponding label drawn in the plot.   
        '''
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
        '''
        Align Y-labels in scatterplot matrix graph.

        Parameters
        ----------
        ylabel_shift : float, optional, default is -0.4
            A shift of Y-labels to well-defined position.
            If all Y-labels are shifted manually, they are aligned precisely.            

        Returns
        -------
        None
            The modified plot (scatterplot matrix graph) is saved in self.grid.
            It can be saved (self.save) later.
        '''
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

    def save(self, output_graph='default', dpi=300):
        '''
        Save scatterplot matrix graph.

        Parameters
        ----------
        output_graph : str, optional, default is 'default'
            Name of the output graph, such as 'my_plot.png'.
            If not given, the 'default' value is employed,
            and the plot will be created in the current dir with a default name
            (the default name depends on the environment => see code below).
        dpi : int, optional, default is 300
            DPI resolution of the saved plot.
            
        Returns
        -------
        None
            The output is the plot saved in a file.
        '''
        # For saving, we use a universal external function.
        # (to avoid code repetition - saving is the same for all plot types
        PlotSaver.save(output_graph, dpi)



class CorrelationMatrixTable:
    '''
   Correlation matrix tables in the form of heatmaps.
    
    The parameters below are employed during the object initialization.    

    Parameters
    ----------
    df : pandas DataFrame
        The dataset, from which we will select properties to correlate.
    properties : dictionary containing pairs of strings
        The dictionary contains keys and values.
        The keys are names of the properties to correlate
        (= the names of the columns in the dataframe *df*).
        The values are names of the properties that should
        printed in the final graph.
        An example of a key/value pair in the *properties* dictionary:
        key='Hit[MPa]' and value=r'$H_{IT}$ [MPa]'
        => the key is the name of the column in *df*
        and the value will be the corresponding label drawn in the plot. 
    my_rcParams : dict, format of matplotlib.pyplot.rcParams, optional
        If the argument is given, global rcParams variable is updated.
        Example: my_rcParams={'figure.figsize':(18/2.54,14/2.54)}

    Returns
    -------
    None
        The final plots are drawn/saved later,
        by means of several methods (draw, finalize, save...). 
    '''

    
    def __init__(self, df, properties, my_rcParams={}):
        '''
        * Initialization of CorrelationMatrixTable object.
        * For arguments description, see the class description above.
        * Note: some *init* parameters are auto-listed by pdoc (ignored here).
        '''

        # Each CorrelationMatrixTable object contains
        # * dataset = dataframe
        # * properties = names of the properties to correlate
        # * two pairs of fig,ax objects
        #   1st fig/ax pair for r-coeffs
        #   2nd fig/ax pair for p-values

        # (1) Initialize basic parameters
        # (data and properties to correlate
        self.df  = df
        self.properties = properties
                
        # (2) BEFORE initializing plot, update plot parameters
        # (a) Set some standard/suitable parameters for given plot type
        standard_rcParams = {
            'figure.figsize':(16/2.54,12/2.54),
            'figure.dpi':100}
        # (b) Update predefined parameters with my_rcParams argument
        my_final_rcParams = standard_rcParams|my_rcParams
        # (c) Update plot parameters
        # (we update global rcParams variable using PlotParameters class
        PlotParameters.set_plot_parameters(my_final_rcParams)
        
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
        '''
        Draw correlation matrix tables for r-values and p-values.

        Parameters
        ----------
        cmap_r : str, optional, default is 'Reds'
            Name of matplotlib.pyplot colormap.
            The colormap will be used for Pearson's r coefficients.
            List of available colormaps: `matplotlib.pyplot.colormaps()`.
        cmap_p : str, optional, default is 'Blues_r'
            Name of matplotlib.pyplot colormap.
            The colormap will be used for p-values.
            List of available colormaps: `matplotlib.pyplot.colormaps()`.
        decimals_r : int, optional, default is 2
            Number of decimals in correlation matrix table showing r coeffs. 
        decimals_p : int, optional, default is 2
            Number of decimals in correlation matrix table showing p-values.
        cbars : bool, optional, default is True
            If True, the colormaps will contain side colorbars.

        Returns
        -------
        None
            The output (two basic correlation matrix tables)
            are saved in self.ax1 (r coefficients) and self.ax2 (p-values).
            They can be finalized (self.finalize) and saved (self.save) later.
        '''
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


    def save(self, 
             output_r='cmatrix_1r.py.png', 
             output_p='cmatrix_2p.py.png',
             dpi=300):
        self.fig1.savefig(output_r, dpi=dpi)
        self.fig2.savefig(output_p, dpi=dpi)



class BoxPlot:

    '''
    Boxplot + correspondig statistics.
    
    The parameters below are employed during the object initialization.    

    Parameters
    ----------
    df : pandas DataFrame
        The dataset, from which we will select properties to compare.
    ax : matplotlib.pyplot.axes object, optional, default is None
        If the argument is given, the plot is drawn in given axes = *ax*.
        Otherwise the plot is drawn as a new, single, separate plot.
    my_rcParams : dict, format of matplotlib.pyplot.rcParams, optional
        If the argument is given, global rcParams variable is updated.
        Example: my_rcParams={'figure.figsize':(8/2.54,5/2.54)}

    Returns
    -------
    None
        The final plot (including optional statistics) is drawn/saved later,
        by means of several methods (draw, finalize, save...). 
    '''

    def __init__(self, df, ax=None, my_rcParams={}):
        '''
        * Initialization of ScatterplotMatrixGraph object.
        * For arguments description, see the class description above.
        * Note: some *init* parameters are auto-listed by pdoc (ignored here).
        '''
        
        # Each BoxPlot object contains
        # 1. dataset = dataframe
        # 2. fig,ax objects
        #   - for standalone plots: both fig,ax are created
        #   - for multiplotss: fig is prepared externaly, ax are created
        
        # (1) Define dataset for the plot
        self.df = df
        
        # (2) BEFORE initializing plot, update plot parameters
        # (a) Set some standard/suitable parameters for given plot type
        standard_rcParams = {
            'figure.figsize':(6/2.54,6/2.54),
            'figure.dpi':100,
            'font.size':9}
        # (b) Update predefined parameters with my_rcParams argument
        my_final_rcParams = standard_rcParams|my_rcParams
        # (c) Update plot parameters
        # (we update global rcParams variable using PlotParameters class
        PlotParameters.set_plot_parameters(my_final_rcParams)
        
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

      
    def add_boxes(self, x, y, categories, colors, width=0.5):
        '''
        Add data = boxes to the BoxPlot graph.

        Parameters
        ----------
        x : str
            Name of X-variable = column in a Dataframe (such as Sterilization),
            which contains categorical data.
        y : str
            Name of Y-variable = column in a DataFrame (such as OI_max),
            which contains numerical data.
        categories : list of strings
            Names of categories = values in a Dataframe (such as ['IRR,'EtO']),
            which should be compared.
        colors : list of colors
            Colors of the categories = boxes in the plot. 
            The list can contain any valid matplotlib color names.
            The number of colors should correspond to number of categories.
        width : float, optional, default is 0.5
            The width of boxes in the plot.

        Returns
        -------
        None.

        '''
        sns.boxplot(
            data=self.df, x=x, y=y,
            order=categories, palette=colors, width=0.5, ax=self.ax)

    
    def label(self, plot_label, xpos=-0.30, ypos=1.00, fontsize=10):
        '''
        Add a short one-letter label to upper left corner of the graph.
        
        Parameters
        ----------
        plot_label : str
            A one letter label, such as 'a','b', ...
        xpos : float, optional, default is -0.30
            X-position of the label.
            The default value should work, but can be adjusted.
        ypos : float, optional, default is 1.00
            X-position of the label.
            The default value should work, but can be adjusted.
        fontsize : int, optional, default is 10
            Font size of the label.
            The default value should work, but can be adjusted.
        
        Returns
        -------
        None
            The output is the plot-with-label saved in self/BoxPlot object.
        '''
        
        self.ax.text(xpos, ypos, plot_label,
            fontsize=fontsize, transform=self.ax.transAxes)

    
    def finalize(self, xlabel, ylabel, xlabelpad=None, ylabelpad=None):
        '''
        Finalize boxplot (add XY-labels, apply labelpads ...).

        Parameters
        ----------
        xlabel : str
            X-axis main label (in addition to X category labels).
        ylabel : str
            Y-axis main label (in addition to Y numerical values)
        xlabelpad : float, optional, the default is None
            Distance between xlabel and the plot edge.
            If not given, the default matplotlib-estimated distance is used.
        ylabelpad : float, optional, the default is None
            Distance between ylabel and the plot edge.
            If not given, the default matplotlib-estimated distance is used.

        Returns
        -------
        None
            The output is the finalized plot saved in self/BoxPlot object.
        '''
        
        # Add X,Y labels (and take xlabelpad,ylabelpad into account)
        self.ax.set_xlabel(xlabel, labelpad=xlabelpad)
        self.ax.set_ylabel(ylabel, labelpad=ylabelpad) 
        
        # Add grid (and ensure that it is BELOW boxes in the boxplot
        self.ax.set_axisbelow(True)
        self.ax.grid()
        
        # Apply tight_layout to figure
        # (if the figure is defined = if we create standalone plot
        # (in case of multiple plots, we create just axes, not the whole fig
        if self.fig != None: 
            self.fig.tight_layout()

    
    def save(self, output_graph='default', dpi=300):
        '''
        Save boxplot to image file.

        Parameters
        ----------
        output_graph : str, optional, default is 'default'
            Name of the output graph, such as 'my_plot.png'.
            If not given, some suitable default filename will be created.
        dpi : int, optional, default is 300
            DPI resolution of the saved plot.
            
        Returns
        -------
        None
            The output is the plot saved in a file.
        '''
        
        # Boxplots can be used in multiplots (although it is not typical).
        # * If the plot IS NOT a part of a multiplot (= plt object),
        #   it can be saved here,
        #   because in such a case it represents an individual file.
        # * If the plot IS a part of a multiplot  (= ax object of a fig object)
        #   it cannot be saved here, because it does not make sense.
        #   Instead, you typically save the whole fig at the end of the script,
        
        if self.fig != None:
            # Figure is NOT a part of multiplot - Ok to save to file.
            # For saving, we use a universal external function,
            # to avoid code repetition - saving is the same for all plot types.
            PlotSaver.save(output_graph, dpi)
        else:
            # Figure is a part of multiplot => just print warning.
            print('The plot is a part of a multiplot.')
            print('It makes no sense to save individual subplots.')
            print('Function ignored => save the whole figure instead!')


    def statistics(self, X, Y, CATS, output_stats='default'):
        '''
        Calculate and save boxplot statistics to text file.

        Parameters
        ----------
        X : str
            Name of X-variable = column in a Dataframe (such as Sterilization),
            which contains categorical data.
        Y : str
            Name of Y-variable = column in a DataFrame (such as OI_max),
            which contains numerical data.
        CATS : list
            Names of categories = values in a Dataframe (such as ['IRR,'EtO']),
            which should be compared.
        output_stats : str, optional, default is 'default'
            Name of the output text file with statistics.
            If 'default' the name will be (input_script_name + .txt).
            
        Returns
        -------
        None
            The output is the calculated statistics
            on the screen and in the text file (with name = output_stats).
        '''
        # Name of TXT file with output statistics that corresponds to BoxPlot
        if output_stats == 'default': output_stats = sys.argv[0]+'.txt'
        # Start writing to both standard output and output_stats file
        logfile = mio.Logger(output_stats)
        # Calulate and print statistics
        print('Correlation matrix table (p-values)')
        print('-----------------------------------')
        for category1 in CATS:
            print(f'{category1:12s}', end='')
            for category2 in CATS:
                xdata = self.df[Y][self.df[X] == category1]
                ydata = self.df[Y][self.df[X] == category2]
                t,p = scipy.stats.ttest_ind(xdata, ydata, equal_var = True)
                print(f'{p:8.4f}', end=' ')
            print()
        # Close dual output
        logfile.close()
    