import re
import pandas as pd 
from sklearn import linear_model
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
from matplotlib.dates import DateFormatter
from matplotlib.dates import DayLocator
from matplotlib.backends.backend_pdf import PdfPages
from cycler import cycler
import seaborn as sns
from gdrive import getLatest


def no_units(s):
    value, units= s.split()
    return float(value)
    
def convert_dates(s):
    return pd.to_datetime(s, format='%b %d, %Y %I:%M:%S %p')
    
def add_space(value):
    '''convert "CamelCase" to "Camel Case"
    '''
    return re.sub('([a-z0-9])([A-Z])', r'\1 \2', value)
    
def make_plot(data):
    converters = {'Concentration': no_units,
                  'Weight': no_units,
                  'Date/Time': convert_dates,
                 }
    weight = pd.read_html(data, match='Weight', 
                                header=0, 
                                converters=converters)[0]
    glucose = pd.read_html(data, match='Concentration', 
                                 header=0,
                                 converters=converters)[0]
    glucose.Event = glucose.Event.apply(add_space)
    glucose.set_index('Date/Time', inplace=True)


    # set up plots
    plt.rc('axes', prop_cycle=(cycler('color', [ 'b','#ee7600', 'magenta','g']))+
                               (cycler('marker', ['o', 'o', 'o', 'o'])))
    fig = plt.figure()
    fig.set_size_inches(11, 8.5)
    ax1 = plt.subplot(211)
    plt.suptitle('Blood Glucose and Weight')
    plt.ylabel('Concentration (mg/dL)')
    ax1.xaxis.set_major_formatter(DateFormatter('%#m/%d'))
    ax1.xaxis.set_major_locator(DayLocator())

    events = glucose.groupby('Event')
    for name, event in events:
        ax1.plot(event.index, event.Concentration, linestyle='-', ms=5, label=name, linewidth=0.5)
    ax1.legend(numpoints=1, loc='upper left', ncol=3)
    #~ plt.axhline(y=120, color='red', linestyle=':', linewidth=1)
    #~ plt.axhspan(0.5, 1, color='red', transform=ax1.transAxes)
    plt.margins(x=0.1, y=0.1)
    trans = transforms.blended_transform_factory( ax1.transAxes, ax1.transData)
    ax1.add_patch(patches.Rectangle((0, 120), width=1, height=100, transform=trans, color='r', alpha=0.1))
    ax1.add_patch(patches.Rectangle((0, 80), width=1, height=40, transform=trans, color='g', alpha=0.1))

    ax2 = plt.subplot(212, sharex=ax1)
    plt.ylabel('Weight (lbs)')
    ax2.plot(weight['Date/Time'], weight['Weight'], marker='o', color='black', ms=5, linewidth=0.5)

    # add trendline
    dates = weight['Date/Time'].values.astype(float).reshape(-1, 1)
    weights = weight['Weight'].values.reshape(-1, 1)
    regression = linear_model.LinearRegression()
    regression.fit(dates, weights)
    trend = regression.predict(dates)
    ax2.plot(weight['Date/Time'], trend, ':', color='#808080')

    plt.margins(x=0.1, y=0.1)
    plt.savefig('output/readings.png', orientation='landscape')
    plt.savefig('output/readings.pdf', orientation='landscape')
    plt.show()

if __name__ == '__main__':
    from argparse import ArgumentParser
    
    parser = ArgumentParser()
    parser.add_argument('filename', nargs='?')
    options = parser.parse_args()
    if options.filename is None:
        print('Reading data from google drive')
        data = getLatest('Blood sugar')  # read from Google Drive account
    else:
        data = options.filename
    make_plot(data)

    