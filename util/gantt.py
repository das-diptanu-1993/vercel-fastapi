import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import sys

FIG_LOCATION = '/tmp/gantt.png'

def clear_all():
    sys.modules[__name__].__dict__.clear()
    return

def save_plot(plt=plt):
    plt.savefig(FIG_LOCATION, dpi=300, bbox_inches='tight')

# Function to modify data format ...
# Input data-format : 
# [ {"task":"task-name", "assignee":"team-member", 
#   "start":"2021-01-10", "due":"2021-01-20", 
#   "end": "2021-01-25" } ]
# Output data-format :
# {'task': {0: 'task-name'}, 'assignee': {0: 'team-member'}, 
#   'start': {0: Timestamp('2021-01-10 00:00:00')}, 
#   'due': {0: Timestamp('2021-01-20 00:00:00')}, 
#   'end': {0: Timestamp('2021-01-25 00:00:00')}}
def row2col(row_data = {}):
    if row_data is None or row_data == {}:
         return {}
    col_data = {'task': {}, 'assignee': {}, \
                     'start': {}, 'due':{}, 'end': {}}
    for i in range(len(row_data)):
        col_data['task'][i] = row_data[i]['task']
        col_data['assignee'][i] = row_data[i]['assignee']
        col_data['start'][i] = pd.Timestamp(row_data[i]['start'])
        col_data['due'][i] = pd.Timestamp(row_data[i]['due'])
        col_data['end'][i] = pd.Timestamp(row_data[i]['end'])
    return col_data

# Function to create random color ...
def random_color():
    r = lambda: random.randint(0,127)
    return ('#%02X%02X%02X' % (128+r(),128+r(),128+r()))

# Creating color dictionary ...
c_dict = {}

# create a column with the color for each Resource
def color(row):
    if row['assignee'] in c_dict:
        return c_dict[row['assignee']]
    else:
        c_dict[row['assignee']] = random_color()
        return c_dict[row['assignee']]

def empty_c_dict():
    c_dict = {}

color_theme = {
    # configuration colors
    "bg": "#23272A",
    "text": "#FFFDE0",
    # additional colors
    "black": "#000000",
    "white": "#FFFFFF",
    "red": "#FFB8B8",
    "green": "#B8FFB8",
    "blue": "#B8B8FF",
    "yellow": "#FFFFB8",
}

# Input data-format : 
# [ {"task":"task-name", "assignee":"team-member", 
#   "start":"2021-01-10", "due":"2021-01-20", 
#   "end": "2021-01-25" } ]
def plot_gantt(title, row_data, color_theme=color_theme):
    if row_data is None or row_data == []:
         return False
    # Building pandas data-frame ...
    col_data = row2col(row_data)
    df = pd.DataFrame(col_data)
    start = df.start.min()
    df['start_x'] = (df.start-start).dt.days
    df['due_x'] = (df.due-start).dt.days
    df['start2due'] = df.due_x - df.start_x
    df['end_x'] = (df.end-start).dt.days
    df['due2end'] = df.end_x - df.due_x
    df['color'] = df.apply(color, axis=1)
    df = df.iloc[::-1] # reverse rows for waterfall view
    # Creating Plot ...
    fig, (ax, ax1) = plt.subplots(2, figsize=(16,9),
                                  gridspec_kw={'height_ratios':[6, 1]},
                                  facecolor=color_theme['bg'])
    fig.canvas.manager.set_window_title(title)
    ax.set_facecolor(color_theme['bg'])
    ax1.set_facecolor(color_theme['bg'])
    ax.barh(df.task, df.start2due, left=df.start_x, color=df.color)
    ax.barh(df.task, df.due2end, left=df.due_x, color=df.color, alpha=0.5)
    df_row_count = df.shape[0]
    for idx, row in df.iterrows():
        callout_color = color_theme['text']
        if int(row.due2end) < 7:
            callout_color = color_theme['green']
        elif int(row.due2end) < 14:
            callout_color = color_theme['yellow']
        else: 
            callout_color = color_theme['red']
        ax.text(row.due_x + 0.1, (df_row_count - idx - 1), f"(delay: {int(row.due2end)}days)",
                va='top', color=callout_color, weight='bold', alpha=0.8)
        ax.text(row.due_x + 0.1, (df_row_count - idx - 1), row.task, va='bottom', ha='left',
                alpha=0.8, color=color_theme['text'], weight='bold')
    ax.set_axisbelow(True)
    ax.xaxis.grid(color='w', linestyle='dashed', alpha=0.4, which='both')
    xticks = np.arange(0, df.end_x.max()+1, 5)
    xticks_labels = pd.date_range(start, end=df.end.max()).strftime("%m/%d")
    xticks_minor = np.arange(0, df.end_x.max()+1, 30)
    ax.set_xticks(xticks)
    ax.set_xticks(xticks_minor, minor=True)
    ax.set_xticklabels(xticks_labels[::5], color='w')
    ax.set_yticks([])
    plt.setp([ax.get_xticklines()], color='w')
    ax.set_xlim(0, df.end_x.max())
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['left'].set_position(('outward', 10))
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_color('w')
    plt.suptitle(title, color=color_theme['text'], weight='bold', fontsize=15)
    legend_elements = []
    for key, value in c_dict.items():
        if key in col_data['assignee'].values():
            legend_elements.append(Patch(facecolor=value, label=key))
    legend = ax1.legend(handles=legend_elements, loc='upper center', ncol=5, frameon=False)
    empty_c_dict()
    plt.setp(legend.get_texts(), color=color_theme['text'], weight='bold')
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.set_xticks([])
    ax1.set_yticks([])
    fig_manager = plt.get_current_fig_manager()
    fig_manager.window.state('zoomed')
    return True

def file2row(file_name):
    try:
        f = open(file_name)
    except FileNotFoundError:
        print("Invalid File Address: {}".format(file_name))
        return None
    except Exception as e:
        print(e)
        return None
    file_data = f.read()
    file_row_list = file_data.split("\n")
    file_header = file_row_list[0].split(",")
    row_data = []
    for file_row in file_row_list[1:]:
        file_cell_list = file_row.split(",")
        row = {}
        for i in range(len(file_header)):
            if i < len(file_cell_list):
                cell = file_cell_list[i]
                if cell.isnumeric():
                    cell = int(cell)
                if cell == "":
                    cell = None
                row[file_header[i]] = cell
        if row != {}:
            row_data.append(row)
    return row_data
