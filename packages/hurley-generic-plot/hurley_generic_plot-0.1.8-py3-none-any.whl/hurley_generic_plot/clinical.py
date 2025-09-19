import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D
import pandas as pd
import numpy as np

def _iqr_errorbar(values):
    q1 = np.percentile(values, 25)
    q3 = np.percentile(values, 75)
    return q1, q3

def plot_CFB(
        df_toplot, x_value, y_value, groupby,
        plot_type = 'mean', # median, box
        group_order = None, group_color = None, 
        units = None,
        linewidth_dict = None, linestyle_dict = None, marker_dict = None, markeredgecolor = 'white',
        errorbar = 'se', # 'sd', ('ci', 90)
        figsize = (8,5), ax = None, 
        showfliers = False, box_width = 0.5, general_linewidth = 0.8, 
        markeredgewidth = None, 
        position_adjust = 0.27, 
        x_ticks = None, stripplot = False, title = None, 
        bbox_to_anchor = None, legend_title = None, legend_loc = None,
        legend_fontsize = 12
):
    """
    Plot change from baseline figures

    plot_type: ['mean','median','box']
    errorbar: ['se', 'sd', ('ci', int)]

    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    assert plot_type in ['mean','median','box'], "plot_type can be 'mean' or 'median' or 'box'"
    groupby_term = [x_value, groupby] if groupby is not None else x_value
    group_order = list(df_toplot[groupby].unique()) if group_order is None else group_order    
    palette = sns.color_palette("colorblind") if group_color is None else group_color
    num_hue_levels = len(group_order)
    
    if plot_type == 'mean':
        if units is not None:
            estimator = None
            linewidth_use = general_linewidth
        else:
            estimator = 'mean'
            linewidth_use = 0

        sns.lineplot(
            data = df_toplot, x = x_value, y = y_value, 
            hue = groupby, hue_order = group_order, palette = palette,
            units = units, estimator = estimator,            
            errorbar = errorbar, err_style= 'bars', 
            linewidth= linewidth_use, ax = ax
        )
        connect_dots = df_toplot.groupby(groupby_term, observed = True)[y_value].mean().reset_index()

    elif plot_type == 'median':
        estimator = 'median'
        linewidth_use = 0
        sns.lineplot(
            data = df_toplot, x = x_value, y = y_value, 
            hue = groupby, hue_order = group_order, palette = palette,
            units = units, estimator = estimator,            
            errorbar = _iqr_errorbar, err_style= 'bars', 
            linewidth= linewidth_use, ax = ax
        )
        connect_dots = df_toplot.groupby(groupby_term, observed = True)[y_value].median().reset_index()
    
    else:
        x_order = range(df_toplot[x_value].max() + 1)
        sns.boxplot(
            data = df_toplot, x = x_value, y = y_value, 
            hue = groupby, palette= palette, hue_order = group_order,
            showfliers = showfliers, showmeans = False,
            linewidth= general_linewidth, width = box_width, ax = ax,
            order = x_order
        )
        connect_dots = df_toplot.groupby(groupby_term, observed = True)[y_value].median().reset_index()

        if stripplot:
           sns.stripplot(
               data = df_toplot, x = x_value, y = y_value, 
               hue = groupby, palette= palette, dodge= True, legend = None,
               linewidth = general_linewidth, ax = ax,
               order = x_order
        )
    
    # add lines that connect mean or median
    handles = []
    labels = []
    
    if units is None:
        for i, group in enumerate(group_order):
            subset = connect_dots[connect_dots[groupby] == group]
            if len(subset) > 0:
                # Calculate position for each dot
                dodge_value = (num_hue_levels - 1) / 2
                if plot_type == "mean":
                    positions = subset[x_value]
                else:
                    positions = [x + (i-dodge_value) * position_adjust for x in subset[x_value]]

                color = palette[i] if isinstance(palette, list) else palette[group]
                linestyle = linestyle_dict.get(group, '-') if linestyle_dict is not None else '-'
                marker = marker_dict.get(group, 'o') if marker_dict is not None else 'o'
                linewidth = linewidth_dict.get(group, general_linewidth) if linewidth_dict is not None else general_linewidth

                # Plot the lines - adjust 'x' to match position of boxes
                ax.plot(positions, subset[y_value], 
                    color = color, linestyle = linestyle, marker = marker, linewidth = linewidth,
                    markeredgewidth = markeredgewidth if markeredgewidth else general_linewidth, 
                    markeredgecolor = markeredgecolor
                )

            # costom legend
            line = Line2D([0], [0], 
                color = color, linestyle = linestyle, marker = marker, linewidth = linewidth,
                markeredgewidth=general_linewidth,
                markeredgecolor = markeredgecolor
            )
            handles.append(line)
            labels.append(group)
            
        ax.get_legend().remove()
        ax.legend(handles, labels, 
                title=groupby if legend_title is None else legend_title,
                bbox_to_anchor = bbox_to_anchor, loc = legend_loc, fontsize = legend_fontsize
            )
    ax.set_title(title)

    if x_ticks is not None:
        ax.set_xticks(ticks= x_ticks)

    return ax


def plot_response(
    df, response, 
    groupby, group_order = None, group_color=None,
    hue=None, hue_order=None, hue_color=None, 
    response_value='Y', 
    ylim=(0, 1), legend_loc=None,
    show_count=True, count_color='white', count_height=0.03, percent_f='long',
    text_fontsize=15, figsize=(6, 4),
    ax=None
):
    """
    Create a bar plot showing response rates with optional subgrouping.

    Parameters
    ----------
    df : pandas.DataFrame
        Input data frame
    response : str
        Column name for response variable
    groupby : str or list
        Column name(s) for grouping
    group_order : list
        Order of groups to display
    response_value : str, default 'Y'
        Value in response column that indicates positive response
    hue : str, optional
        Column name for subgrouping
    hue_order : list, optional
        Order of hue categories
    hue_color, x_color : list or dict, optional
        Color palettes for hue groups or main groups
    ylim : tuple, default (0, 1)
        Y-axis limits
    show_count : bool, default True
        Whether to show count numbers on bars
    percent_f : {'long', 'short'}, default 'long'
        Format for percentage labels (long: '75.1%', short: '75%')

    Returns
    -------
    matplotlib.axes.Axes
        The plot axes
    """
    # Convert groupby to list if string
    groupby = [groupby] if isinstance(groupby, str) else groupby
    
    # Set hue if multiple groupby columns
    if hue is None and len(groupby) > 1:
        hue = groupby[-1]
    if hue is not None:
        groupby = groupby + [hue]
    
    # Prepare data
    groups = groupby + [response]
    df_use = df[groups].dropna()
    df_use[response] = pd.Categorical(df_use[response])
    
    # Calculate response rates
    df_toplot_pre = pd.DataFrame(
        df_use.groupby(groups, observed=False).size() / 
        df_use.groupby(groupby).size()
    )
    
    # Add count information
    if len(groupby) > 1:
        df_toplot_pre['count'] = pd.DataFrame(df_use.groupby(groupby).size())
    else:
        count_dict = pd.DataFrame(df_use.groupby(groupby).size())[0].to_dict()
        df_toplot_pre['count'] = [count_dict.get(x[0]) for x in df_toplot_pre.index]
    
    # Filter for response value and prepare final plotting data
    query_name = f"`{response}` == '{response_value}'"
    df_toplot = (df_toplot_pre.query(query_name)
                 .reset_index()
                 .rename({0: 'Rate'}, axis=1))

    # Create or get axes
    if ax is None:
        _, ax = plt.subplots(figsize=figsize)
    
    # Create bar plot
    palette_color = group_color if len(groupby) == 1 else hue_color
    barplot = sns.barplot(
        data=df_toplot, x=groupby[0], y='Rate',
        order=group_order, hue=hue, hue_order=hue_order,
        palette=palette_color, ax=ax
    )

    # Calculate counts for annotations
    if len(groupby) > 1:
        if hue_order is None:
            raise ValueError("hue_order must be specified when using multiple groupby columns")
        counts = [
            df_toplot[
                (df_toplot[groupby[0]] == g) &
                (df_toplot[groupby[1]] == h)
            ]['count'].iloc[0] if not df_toplot[
                (df_toplot[groupby[0]] == g) &
                (df_toplot[groupby[1]] == h)
            ].empty else 0
            for h in hue_order
            for g in group_order
        ]
    else:
        if group_order is None:
            raise ValueError("group_order must be specified")
        counts = [
            df_toplot[df_toplot[groupby[0]] == g]['count'].iloc[0]
            for g in group_order
        ]

    # Add annotations
    for p, count in zip(barplot.patches, counts):
        percentage_value = p.get_height()
        if percent_f == 'long':
            percentage = f"{percentage_value * 100:.1f}%"
        else:
            percentage = f"{percentage_value * 100:.0f}%" if percentage_value > 0 else 0

        if percentage_value == 0:
            percentage = ""
        
        x_pos = p.get_x() + p.get_width() / 2
        
        # Add percentage label
        ax.annotate(
            percentage,
            (x_pos, p.get_height()),
            ha='center', va='center',
            xytext=(0, 9),
            textcoords='offset points',
            fontsize=text_fontsize
        )
        
        # Add count label
        if show_count:
            c_color = '#333333' if percentage_value == 0 or np.isnan(percentage_value) else count_color
            ax.annotate(
                int(count),
                (x_pos, count_height),
                ha='center', va='center',
                color=c_color,
                fontsize=text_fontsize
            )

    # Set title
    title = (f"{response}" if len(groupby) == 1 
            else f"{response}\nsubgroup by: {groupby[-1]}")
    ax.set_title(title)
    
    # Set labels and limits
    ax.set_ylabel('Response Rate')
    ax.set_ylim(ylim)
    
    # Configure legend
    if legend_loc and len(groupby) > 1:
        ax.legend(title=groupby[-1], loc=legend_loc)
    
    return ax


