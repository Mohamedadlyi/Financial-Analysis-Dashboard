import pandas as pd
import numpy as np
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import base64
import io


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

        # Calculate savings percentage for expenses
        if label == 'Expense':
            total_income = df[(df['Expense/Income'] == 'Income') & (df['Year'] == year)]['Amount (EGP)'].sum()
            total_expense = sub_df['Amount (EGP)'].sum()
            savings = total_income - total_expense
            savings_percentage = (savings / total_income) * 100 if total_income > 0 else 0

            # Add annotation for savings percentage
            fig.update_layout(
                annotations=[dict(
                    text=f'Savings: {savings_percentage:.2f}%',
                    x=0.8, y=0.2, showarrow=False, font_size=16, font_color='white'
                )],
                title=f'Expense Breakdown {year}'
            )

    return fig


# Define function to create bar chart
def make_bar_chart(df, year, label):
    sub_df = df[(df['Expense/Income'] == label) & (df['Year'] == year)]
    monthly_totals = sub_df.groupby('Month Name')['Amount (EGP)'].sum().reset_index()
    fig = px.bar(monthly_totals, x='Month Name', y='Amount (EGP)', title=f'{label} per Month {year}')
    return fig

# Define function to create line chart for expenses per month across all years
def make_line_chart_all_years(df):
    expense_df = df[df['Expense/Income'] == 'Expense']
    monthly_expenses = expense_df.groupby(['Year', 'Month'])['Amount (EGP)'].sum().reset_index()
    fig = px.line(monthly_expenses, x='Month', y='Amount (EGP)', color='Year',
                  labels={'Amount (EGP)': 'Total Expenses (EGP)', 'Month': 'Month'})
    fig.update_layout(title='Expenses per Month Across Years', xaxis=dict(tickmode='linear'))
    return fig

# Create Dash app
app = dash.Dash(__name__)
server = app.server
# Define app layout using Dash components
app.layout = html.Div([
    html.H1("Financial Analysis Dashboard"),
    # dcc.Graph(id='line-chart', figure=make_line_chart_all_years(df)),
    html.Div(
        [
            dcc.Upload(
                id='upload-CSV-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '100%',
                    'display': 'flex',
                    'justify-content': 'center',
                    'align-items': 'center',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'borderColor': '#999',
                    'textAlign': 'center',
                    'background-color': '#444',
                    'color': '#ccc'
                },
                # Allow multiple files to be uploaded
                multiple=False
            ),
        ],
        style={'width': '100px', 'height': '100px'}  # Adjust dimensions of the upload button container
    ),
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


@app.callback(
    Output('charts-div', 'children'),
    [Input('year-dropdown', 'value'),
     Input('tabs', 'value'),
     Input('upload-CSV-data', 'contents'),
     Input('upload-CSV-data', 'filename')]
)
def update_data_and_charts(year, tab, contents, filename):
    # Check if a file was uploaded
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                # Read the uploaded CSV file into a DataFrame
                new_df = pd.read_csv(filename, index_col=False)

                
                # Update the existing DataFrame with the uploaded data
                global df
                df = new_df

                # Regenerate charts with updated data
                if tab == 'income-tab':
                    pie_chart_fig = make_pie_chart(df, year, 'Income')
                    bar_chart_fig = make_bar_chart(df, year, 'Income')
                elif tab == 'expense-tab':
                    pie_chart_fig = make_pie_chart(df, year, 'Expense')
                    bar_chart_fig = make_bar_chart(df, year, 'Expense')

                # Return updated charts
                return html.Div([
                    html.Div([
                        dcc.Graph(figure=pie_chart_fig)
                    ], style={'width': '50%', 'display': 'inline-block'}),
                    html.Div([
                        dcc.Graph(figure=bar_chart_fig)
                    ], style={'width': '50%', 'display': 'inline-block'})
                ])
        except Exception as e:
            print(str(e))
            return html.Div(['There was an error processing this file.'])
    else:
        # No file uploaded, return existing charts
        if tab == 'income-tab':
            pie_chart_fig = make_pie_chart(df, year, 'Income')
            bar_chart_fig = make_bar_chart(df, year, 'Income')
        elif tab == 'expense-tab':
            pie_chart_fig = make_pie_chart(df, year, 'Expense')
            bar_chart_fig = make_bar_chart(df, year, 'Expense')

        return html.Div([
            html.Div([
                dcc.Graph(figure=pie_chart_fig)
            ], style={'width': '50%', 'display': 'inline-block'}),
            html.Div([
                dcc.Graph(figure=bar_chart_fig)
            ], style={'width': '50%', 'display': 'inline-block'})
        ])


if __name__ == '__main__':
    app.run_server(debug=True)
