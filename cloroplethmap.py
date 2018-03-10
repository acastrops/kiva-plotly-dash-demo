import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import numpy as np


 
df = pd.read_csv('data/kiva_loans.csv')
df['date'] = pd.to_datetime(df['date'])
df['year'] = df.date.dt.year
df['year'] = df.year.astype(str).astype(int)

#df = df.groupby(['year', 'country','borrower_genders']).size()

df = df[['country','borrower_genders','year']]
df.dropna()
df[['borrower_genders']].astype(str)
df.dropna()

mask = (df['borrower_genders'].str.len() <= 6)

df = df.loc[mask]


df['borrower_genders'].replace('female',1, inplace=True)
df['borrower_genders'].replace('male',0, inplace=True)

#countries_funded_amount = df.loc[df['year'] == 2014]


app = dash.Dash()

app.layout = html.Div(className='container', children=[
        
    # Richard's cloropleth map
    html.Div([
        html.Hr(),
        html.H1(
        children='Cloropleth maps including slider percent colormap',
        style={
            'textAlign': 'center',  # center the header
            'color': '#7F7F7F'
            # https://www.biotechnologyforums.com/thread-7742.html more color code options
        }
    ),
        dcc.Graph(id='graph-with-slider'),
        html.Div([  # div inside div for style
            dcc.Slider(
                id='year-slider',
                min=df['year'].min(),
                max=df['year'].max(),
                value=df['year'].min(),  # The default value of the slider
                step=None,
                # the values have to be the same dtype for filtering to work later
                marks={str(year): year for year in df['year'].unique()},
            )
        ],
            style={'marginLeft': 40, 'marginRight': 40})
    ]),
        html.Div([
        dcc.Graph(id='scatter-with-slider', animate='true'),
        dcc.Slider(
            id='scatter-slider',
            min=2014,
            max=2017,
            value=2014,
            step=1,
            marks={str(year): str(year) for year in [2014, 2015, 2016, 2017]}
    )
])
])
        
        
# Notice the Input and Outputs in this wrapper correspond to
# the ids of the components in app.layout above.
@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('year-slider', 'value')])
def update_figure(selected_year):
    """Define how the graph is to be updated based on the slider."""

    # Depending on the year selected on the slider, filter the db
    # by that year.

    # snag: using .groupby() with more than one feature caused the datatype
    # to be Pandas.Series instead of Pandas.DataFrame. So, we couldn't just do
    # countries_funded_amount[countries_funded_amount['year'] == selected_year]
    
        
    #one_year_data = df.loc[df['year'] == [selected_year]]
    #df = df.loc[df['year'] == [selected_year]]
    df1 = df.loc[df['year'] == [selected_year]]

    
    #df = countries_funded_amount.loc[selected_year]
    #df = countries_funded_amount.loc[2017]
    
    ## Counts number of times a country appears
    a = df1['country'].value_counts()

## gets sum related to country
    b = df1.groupby(['country'])[['borrower_genders']].sum()

    a = pd.DataFrame(a)
    a.columns = ['value']

    b = pd.DataFrame(b)

    a = a.sort_index()
    b = b.sort_index()

## Percentage of loans that females acquired
    percent = b['borrower_genders']/a['value'] *100
    percent = pd.DataFrame(percent)
    percent['country'] =  percent.index
    
    ticksmin = percent[0].min()
    ticksmax = percent[0].max()
    ticks = np.linspace(ticksmin, ticksmax, 8)
    label = ticks.astype(np.int)
    
    #one_year_data = countries_funded_amount.loc[selected_year]


    data = [dict(
        type='choropleth',
        locations= percent['country'],
        # list of country names
        # other option is USA-states
        locationmode='country names',
        # sets the color values. using log scale so that extreme values don't
        # drown out the rest of the data
        z= percent[0].astype(float),# ...and their associated values
        # sets the text element associated w each position
        text=percent['country'],
        hoverinfo='location+z',  # hide the log-transformed data values
        # other colorscales are available here:
        # https://plot.ly/ipython-notebooks/color-scales/
        colorscale='Blues',
        # by default, low numbers are dark and high numbers are white
        reversescale=True,
        # set upper bound of color domain (see also zmin)
        # zmin=200,
        # zmax=30000,
        # if you want to use zmin or zmax don't forget to disable zauto
        # zauto=False,
        marker={'line': {'width': 0.5}},  # width of country boundaries
        colorbar={'autotick': True,
                  'tickprefix': '%',  # could be useful if plotting $ values
                  'title': 'Percent of loans Female',
                  'tickvals': ticks,
                  'ticktext': label# colorbar title
                  # transform log label labels back to standard scale
                  },
    )]
    layout = dict(
        title='Percent loans given tofemales. Year: {}<br>Source:\
                <a href="https://www.kaggle.com/kiva/data-science-for-good-kiva-crowdfunding"">\
                Kaggle</a>'.format(selected_year),
        font=dict(family='Courier New, monospace', size=18, color='#7f7f7f'),
        geo={'showframe': False}  # hide frame around map
    )
    cloropleth_map_fig = {'data': data, 'layout': layout}
    return cloropleth_map_fig


if __name__ == '__main__':
    app.run_server(debug=True)
