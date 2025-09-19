import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr, pearsonr

def _scientific_round(number, decimals=2, force_decimal=True):
    """
    Round starting from first non-zero digit after decimal
    Parameters:
        decimals: Number of significant digits after first non-zero digit
        force_decimal: If True, always show in decimal format; if False, use scientific notation
    """
    if number == 0:
        return 0
        
    # Convert to scientific notation components
    mantissa, exponent = f'{number:e}'.split('e')
    mantissa = float(mantissa)
    exponent = int(exponent)
    
    # Round the mantissa to desired decimals
    rounded_mantissa = np.round(mantissa, decimals)
    
    # Format the result
    if force_decimal and exponent > -4:  # Only use decimal format for numbers larger than 1e-10
        result = rounded_mantissa * 10**exponent
        # Convert to string and remove trailing zeros after decimal point
        return f'{result:.{abs(exponent) + decimals}f}'.rstrip('0').rstrip('.')
    else:
        return f'{rounded_mantissa}e{exponent:+d}'

def plot_correlation(
    df_toplot, x_value, y_value, 
    groupby=None, group_order=None, group_color=None,
    xlab=None, ylab=None, title = None,
    correlation= None, # 'spearman' or 'pearson'
    height=3.5, aspect=1.2, 
    lab_fontsize = 15, title_fontsize = 15, legend_loc = 'upper center',
    scatter_kws=None
):
    """
    Create a correlation plot with optional grouping and correlation statistics.
    
    Parameters:
    -----------
    df_toplot : pandas DataFrame
        Input dataframe containing the data
    x_value : str
        Column name for x-axis variable
    y_value : str
        Column name for y-axis variable
    groupby : str, optional
        Column name for grouping
    group_order : list, optional
        Order of groups to display
    group_color : dict, optional
        Color mapping for groups
    xlab : str, optional
        X-axis label (defaults to x_value)
    ylab : str, optional
        Y-axis label (defaults to y_value)
    correlation :
        Type of correlation to calculate ('spearman' or 'pearson')
    height : float, default=3.5
        Height of the figure in inches
    aspect : float, default=1.2
        Aspect ratio of the figure
    scatter_kws : dict, optional
        Additional keyword arguments for scatter plot
        
    Returns:
    --------
    matplotlib.axes.Axes
        The plot axes
    """
    # Set default values
    xlab = xlab or x_value
    ylab = ylab or y_value
    scatter_kws = scatter_kws or {
        'edgecolor': 'white',
        'linewidths': 0.8
    }
    
    # Determine groups if not specified
    if groupby:
        if group_order is None:
            group_order = sorted(df_toplot[groupby].unique())
        
        if group_color is None:
            group_color = dict(zip(group_order, sns.color_palette("colorblind", len(group_order))))
    
    # Create title with correlation statistics if requested
    if correlation:
        title = title or ""
        assert correlation in ['spearman','pearson'], "correlation can be only spearman or pearson"
        corr_func = spearmanr if correlation == 'spearman' else pearsonr
        
        if groupby:
            for group in group_order:
                df_sub = df_toplot[df_toplot[groupby] == group][[x_value, y_value]].dropna()
                rho, p_value = corr_func(df_sub[x_value], df_sub[y_value])
                title += f'\n{group}: p = {_scientific_round(p_value, decimals= 3)}, r = {_scientific_round(rho, decimals=2)}'
        else:
            df_sub = df_toplot[[x_value, y_value]].dropna()
            rho, p_value = corr_func(df_sub[x_value], df_sub[y_value])
            title += f'\np = {_scientific_round(p_value, decimals= 3)}, r = {_scientific_round(rho, decimals=2)}'
    
    # Create plot
    g = sns.lmplot(
        data=df_toplot, 
        x=x_value,
        y=y_value, 
        hue=groupby,
        hue_order=group_order,
        palette=group_color,
        height=height,
        aspect=aspect,
        scatter_kws=scatter_kws,
        legend=None
    )
    
    ax = plt.gca()

    # Set labels and title
    ax.set_xlabel(xlab, fontsize=lab_fontsize)
    ax.set_ylabel(ylab, fontsize=lab_fontsize)
    if title:
        ax.set_title(title, fontsize=title_fontsize)
    
    # Add legend if grouping is used
    if groupby:
        ax.legend(title=groupby, loc=legend_loc)
    
    return ax

def plot_bar_from_baseline(df, x, y, 
                    baseline=1,
                    x_order=None,
                    colors=None, 
                    figsize=(4, 3),
                    cap_width=0.1,
                    line_width=1,
                    baseline_color='grey',
                    baseline_style='-',
                    baseline_width=0.8,
                    error_color='black',
                    error_type = 'sem',
                    ylabel='ratio to baseline'):
    """
    Create a bar plot showing changes from a baseline value with directional error bars.
    
    Parameters:
    -----------
    df : pandas DataFrame
        Input data
    x : str
        Column name for x-axis categories
    y : str
        Column name for y-axis values
    baseline : float, default=1
        The baseline value to measure changes from
    x_order : list, optional
        Specific order for x-axis categories
    colors : dict, optional
        Dictionary mapping x categories to colors
    figsize : tuple, default=(4, 3)
        Figure size in inches
    cap_width : float, default=0.1
        Width of error bar caps
    line_width : float, default=1
        Width of error bar lines
    baseline_color : str, default='grey'
        Color of baseline horizontal line
    baseline_style : str, default='-'
        Style of baseline line
    baseline_width : float, default=0.8
        Width of baseline line
    error_color : str, default='black'
        Color of error bars
    error_type = 'sem'
        Type of error bar, either 'sem' or 'std'
    ylabel : str, default='ratio to baseline'
        Label for y-axis
    
    Returns:
    --------
    matplotlib.axes.Axes
        The plot axes
    """
    plt.figure(figsize=figsize)
    
    # Calculate statistics
    if x_order is None:
        x_order = df[x].unique()
    
    stats = df.groupby(x)[y].agg(['mean', error_type])
    stats = stats.reindex(x_order)  # Reorder based on x_order
    
    heights = stats['mean'] - baseline
    errors = stats[error_type]
    
    # Create bars
    bars = plt.bar(x=range(len(heights)), 
                  height=heights,
                  bottom=baseline,
                  color=[colors.get(cat) for cat in stats.index] if colors else None)
    
    # Add directional error bars
    for idx, (mean, error) in enumerate(zip(stats['mean'], errors)):
        if mean < baseline:  # Below baseline
            # Vertical line
            plt.plot([idx, idx], [mean, mean - error], 
                    color=error_color, linewidth=line_width)
            # Horizontal cap
            plt.plot([idx - cap_width, idx + cap_width], [mean - error, mean - error], 
                    color=error_color, linewidth=line_width)
        else:  # Above baseline
            # Vertical line
            plt.plot([idx, idx], [mean, mean + error], 
                    color=error_color, linewidth=line_width)
            # Horizontal cap
            plt.plot([idx - cap_width, idx + cap_width], [mean + error, mean + error], 
                    color=error_color, linewidth=line_width)
    
    plt.axhline(y=baseline, color=baseline_color, 
                linestyle=baseline_style, linewidth=baseline_width)
    plt.xticks(range(len(heights)), stats.index)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.ylabel(ylabel)
    
    return plt.gca()

def plot_box_strip(df,x,y,
             order = None, hue = None, hue_order = None,
             palette = None, showfliers = False,
             dot_color = 'white', dot_size = 6, dot_line = 0.8,
             ax = None, figsize = (6,5),
             kwargs_box = {}, kwargs_strip = {}
             ):
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    sns.boxplot(df, x = x, y = y, 
                order = order, 
                palette = palette, 
                showfliers = showfliers, 
                ax = ax,
                hue = hue, hue_order= hue_order,
                **kwargs_box
               )
    sns.stripplot(df, x = x, y = y,
                  order = order, 
                  dodge=True if hue else False,
                  hue = hue, hue_order= hue_order,
                  ax = ax,
                  palette=[dot_color],
                  linewidth= dot_line, size = dot_size,
                  legend= None,
                  **kwargs_strip
                 )
    return ax