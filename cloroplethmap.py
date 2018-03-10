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

df = df[['country','borrower_genders','year']]
df.dropna()
df[['borrower_genders']].astype(str)
df.dropna()

mask = (df['borrower_genders'].str.len() <= 6)

df = df.loc[mask]


df['borrower_genders'].replace('female',1, inplace=True)
df['borrower_genders'].replace('male',0, inplace=True)


app = dash.Dash()

app.layout = html.Div(className='container', children=[
        
    # Geographical Map
    html.Div([
        html.Hr(),
        html.H1(
        children='Cloropleth maps including slider percent colormap',
        style={
            'textAlign': 'center', 
            'color': '#7F7F7F'
        }
    ),
        dcc.Graph(id='graph-with-slider'),
        html.Div([  
            dcc.Slider(
                id='year-slider',
                min=df['year'].min(),
                max=df['year'].max(),
                value=df['year'].min(),
                step=None,
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


@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('year-slider', 'value')])
def update_figure(selected_year):
    """Define how the graph is to be updated based on the slider."""

    df1 = df.loc[df['year'] == [selected_year]]

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


    data = [dict(
        type='choropleth',
        locations= percent['country'],
        locationmode='country names',
        z= percent[0].astype(float),
        text=percent['country'],
        hoverinfo='location+z',
        colorscale='Blues',
        reversescale=True,
        marker={'line': {'width': 0.5}},  
        colorbar={'autotick': True,
                  'tickprefix': '%',  
                  'title': 'Percent of loans Female',
                  'tickvals': ticks,
                  'ticktext': label
                  },
    )]
    layout = dict(
        title='Percent loans given tofemales. Year: {}<br>Source:\
                <a href="https://www.kaggle.com/kiva/data-science-for-good-kiva-crowdfunding"">\
                Kaggle</a>'.format(selected_year),
        font=dict(family='Courier New, monospace', size=18, color='#7f7f7f'),
        geo={'showframe': False}  
    )
    cloropleth_map_fig = {'data': data, 'layout': layout}
    return cloropleth_map_fig


if __name__ == '__main__':
    app.run_server(debug=True)
