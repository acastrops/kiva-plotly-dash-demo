import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import numpy as np

df = pd.read_csv('data/kiva_loans.csv.gz', compression='gzip')

app = dash.Dash()

app.layout = html.Div([
    dcc.Graph(id='graph-with-slider', animate='true'),
    dcc.Slider(
        id='year-slider',
        min=2014,
        max=2017,
        value=2014,
        step=1,
        marks={str(year): str(year) for year in [2014, 2015, 2016, 2017]}
    )
])

app.layout = html.Div([
    html.H1('Heads!'),
    dcc.Graph(id='graph-with-slider'),
    html.H3('Age',
        style={
            'textAlign': 'center'
        }
    ),
    dcc.RadioItems(
        id='year-picker',
        options=[
            {'label': '1', 'value': df['age'].min()},
            {'label': '2', 'value': df['age'].max()}
        ],
        value=1,
        style={'textAlign':'center'}
    )
])

@app.callback(
    dash.dependencies.Output('graph-with-slider', 'figure'),
    [dash.dependencies.Input('year-slider', 'value')])
def update_figure(selected_year):
    filtered_loans_data = loans_data[loans_data['date'].str.match(str(selected_year))]
    traces = []
    for i in filtered_loans_data.sector.unique():
        df_by_sector = filtered_loans_data[filtered_loans_data['sector'] == i]
        traces.append(go.Scatter(
            x=[np.mean(df_by_sector[df_by_sector['country'] == j].loan_amount) for j in df_by_sector.country.unique()],   # graph type. Try changing
            y=[np.mean(df_by_sector[df_by_sector['country'] == j].lender_count) for j in df_by_sector.country.unique()],     # to go.Scatter3d.
            text=df_by_sector['country'],
            mode='markers',
            opacity=0.7,
            marker={
                'size': 15,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=i
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'type': 'linear', 'title': 'Loan Amount', 'autorange': 'True'},
            yaxis={'type': 'linear', 'title': 'Lender Count', 'autorange': 'True'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }


if __name__ == '__main__':
    app.run_server()
