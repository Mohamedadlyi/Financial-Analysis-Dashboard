import pandas as pd
import numpy as np
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# Read the data
df = pd.read_csv('transactions_2024_categorized.csv', index_col=False)
df['Year'] = pd.to_datetime(df['Date']).dt.year
df['Month'] = pd.to_datetime(df['Date']).dt.month
df['Month Name'] = pd.to_datetime(df['Date']).dt.strftime("%b")

# Define functions to create pie charts
def make_pie_chart(df, year, label):
    sub_df = df[(df['Expense/Income'] == label) & (df['Year'] == year)]
    if label == 'Income':
        fig = px.pie(sub_df, values='Amount (EGP)', names='Name / Description', title=f'{label} Breakdown {year}')
    else:
        fig = px.pie(sub_df, values='Amount (EGP)', names='Category', title=f'{label} Breakdown {year}')
    return fig

# Define function to create bar chart
def make_bar_chart(df, year, label):
    sub_df = df[(df['Expense/Income'] == label) & (df['Year'] == year)]
    monthly_totals = sub_df.groupby('Month Name')['Amount (EGP)'].sum().reset_index()
    fig = px.bar(monthly_totals, x='Month Name', y='Amount (EGP)', title=f'{label} per Month {year}')
    return fig

# Create Dash app
app = dash.Dash(__name__)
server = app.server

# Define app layout using Dash components
app.layout = html.Div([
    html.H1("Financial Analysis Dashboard"),
    
    # Dropdown to select year
    dcc.Dropdown(
        id='year-dropdown',
        options=[
            {'label': '2022', 'value': 2022},
            {'label': '2023', 'value': 2023},
            {'label': '2024', 'value': 2024}
        ],
        value=2024,
        style={'width': '200px'}
    ),
    
    # Tabs for displaying charts
    dcc.Tabs(id='tabs', value='income-tab', children=[
        dcc.Tab(label='Income', value='income-tab'),
        dcc.Tab(label='Expense', value='expense-tab')
    ]),
    
    # Div to display charts
    html.Div(id='charts-div')
])

# Callback to update charts based on dropdown and tab selection
@app.callback(
    Output('charts-div', 'children'),
    [Input('year-dropdown', 'value'),
     Input('tabs', 'value')]
)
def update_charts(year, tab):
    if tab == 'income-tab':
        pie_chart_fig = make_pie_chart(df, year, 'Income')
        bar_chart_fig = make_bar_chart(df, year, 'Income')
    elif tab == 'expense-tab':
        pie_chart_fig = make_pie_chart(df, year, 'Expense')
        bar_chart_fig = make_bar_chart(df, year, 'Expense')
    
    return html.Div([
        dcc.Graph(figure=pie_chart_fig),
        dcc.Graph(figure=bar_chart_fig)
    ])

if __name__ == '__main__':
    app.run_server(debug=True)
