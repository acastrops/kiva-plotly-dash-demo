import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import numpy as np

# Import your dataframe from a csv with pandas
df = pd.read_csv('data/kiva_loans.csv.gz', compression='gzip')

'''
Create two new gender columns indicating if male or
female was found in the list of borrower genders.
'''
df['male'] = df['borrower_genders'].str.contains('male', case=False)

df['female'] = df['borrower_genders'].str.contains('female', case=False)

################### BAR CHART CODE #####################

# Select variables of interest
repayment_df = df[['repayment_interval', 'sector', 'male', 'female']]

# drop any rows with any null values
repayment_df = repayment_df.dropna()

# select rows with irregular payments
repayment_df = repayment_df[repayment_df.repayment_interval == "irregular"]

#print(repayment_df.male)
#print(repayment_df.female)

# Split dataframe based on gender
top_sectors_male = repayment_df[repayment_df.male]
top_sectors_female = repayment_df[repayment_df.female]

# For each gender, find the top 5 sectors by count
top_sectors_male = top_sectors_male.groupby('sector').size().sort_values(ascending=False)[0:5]
top_sectors_female = top_sectors_female.groupby('sector').size().sort_values(ascending=False)[0:5]

############### END BAR CHART CODE #####################




# Modify time columns
df['date'] = pd.to_datetime(df['date'])
df['year'] = df.date.dt.year
df['year'] = df.year.astype(str).astype(int)
df['day'] = df.date.dt.dayofyear
df['day'] = df.day.astype(str).astype(int)

#df = df[['country','borrower_genders','year']]
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
        children='Choropleth maps including slider percent colormap',
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
    html.Br(),
    html.Br(),
        html.Div([
        dcc.Graph(id='scatter-with-slider', animate='true'),
        dcc.Slider(
            id='scatter-slider',
            min=df['year'].min(),
            max=df['year'].max(),
            value=df['year'].min(),
            step=None,
            marks={str(year): year for year in df['year'].unique()},
    ),
    html.Br(),
    html.Br(),
    dcc.Dropdown(
        id='scatter_country',
        options=[{'label': country, 'value': country} for country in df['country'].unique()],
        value='United States'
    ),
    html.Br(),
    html.Br(),
    html.H1(
        children='Top 5 sectors for irregular payments',
        style={
            'textAlign': 'center',  # center the header
            'color': '#7F7F7F'
            # https://www.biotechnologyforums.com/thread-7742.html more color code options
        }
    ),
    # Bar Graph
    html.Div(dcc.Graph(
        id='basic-interactions',
        figure={
            'data': [
                {
                    'x': top_sectors_male.index,
                    'y': top_sectors_male,
                    'type': 'bar',
                    'opacity': .6,  # changes the bar chart's opacity
                    'name': 'At Least 1 Male Borrower'
                },
                {
                    'x': top_sectors_female.index,
                    'y': top_sectors_female,
                    'type': 'bar',
                    'opacity': .6,  # changes the bar chart's opacity
                    'name': 'At Least 1 Female Borrower'
                }

            ],
            'layout': go.Layout(
                xaxis={'title': 'Sector'},
                yaxis={'title': 'Irregular Payments'},
                barmode='group'
            )
        }

    ))
], style={'marginLeft': 40, 'marginRight': 40})
])

@app.callback(
    Output('scatter-with-slider', 'figure'),
    [Input('scatter-slider', 'value'), Input('scatter_country', 'value')])
def update_scatter(selected_year, selected_country):
    """Define how the graph is to be updated based on the slider."""

    df_scatter = df.loc[df['year'] == selected_year]
    df_scatter = df_scatter.loc[df_scatter['country'] == selected_country]
    df_scatter = df_scatter[['day', 'borrower_genders', 'funded_amount']]
    df_scatter = df_scatter.groupby(['day','borrower_genders']).mean().reset_index()
    # each point is
    # y = funded_amount
    # x = day
    # color is gender

## gets sum related to country
    traces = []
    male_x = []
    male_y = []
    female_x = []
    female_y = []
    for _, row in df_scatter.iterrows():
        if row['borrower_genders']:
            female_x.append(row['day'])
            female_y.append(row['funded_amount'])
        else:
            male_x.append(row['day'])
            male_y.append(row['funded_amount'])
    #x = list(df_scatter.day)
    #y = list(df_scatter.funded_amount)
    #color = ['red' if gender else 'blue' for gender in list(df_scatter.borrower_genders)]
    # red for female
    #female
    traces.append(go.Scatter(
        x=female_x,
        y=female_y,
        mode='markers',
        opacity=0.7,
        marker={'size':15,'line':{'width':0.5,'color':'red'}},
        name='Female'
    ))
    #male
    traces.append(go.Scatter(
        x=male_x,
        y=male_y,
        mode='markers',
        opacity=0.7,
        marker={'size':15,'line':{'width':0.5,'color':'blue'}},
        name='Male'
    ))
    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'type': 'linear', 'title': 'Day of Year', 'autorange': 'True'},
            yaxis={'type': 'linear', 'title': 'Funded Amount', 'autorange': 'True'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }


'''
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
        title='Percent loans given to females. Year: {}<br>Source:\
                <a href="https://www.kaggle.com/kiva/data-science-for-good-kiva-crowdfunding"">\
                Kaggle</a>'.format(selected_year),
        font=dict(family='Courier New, monospace', size=18, color='#7f7f7f'),
        geo={'showframe': False}
    )
    scatter_fig = {'data': data, 'layout': layout}
    return scatter_fig
'''

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
        title='Percent loans given to females. Year: {}<br>Source:\
                <a href="https://www.kaggle.com/kiva/data-science-for-good-kiva-crowdfunding"">\
                Kaggle</a>'.format(selected_year),
        font=dict(family='Courier New, monospace', size=18, color='#7f7f7f'),
        geo={'showframe': False}
    )
    choropleth_map_fig = {'data': data, 'layout': layout}
    return choropleth_map_fig


if __name__ == '__main__':
    app.run_server(debug=True)
