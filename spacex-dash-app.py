import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Load SpaceX data
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Prepare payload range values
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Get unique launch sites for dropdown options
launch_sites = spacex_df['Launch Site'].unique().tolist()
options = [{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in launch_sites]

# Initialize Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 40}),

    # Dropdown for Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=options,
        value='ALL',
        placeholder="Select a Launch Site",
        searchable=True
    ),
    html.Br(),

    # Pie chart for success counts
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # Payload range slider
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        marks={int(min_payload): str(int(min_payload)), int(max_payload): str(int(max_payload))},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # Scatter plot for payload vs success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for pie chart update based on site dropdown
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(selected_site):
    if selected_site == 'ALL':
        df = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(df, names='Launch Site', title='Total Successful Launches by Site')
    else:
        df = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_fail_counts = df['class'].value_counts().reset_index()
        success_fail_counts.columns = ['class', 'count']
        success_fail_counts['class'] = success_fail_counts['class'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(success_fail_counts, names='class', values='count',
                     title=f"Success vs Failure for site {selected_site}")
    return fig

# Callback for scatter chart update based on site and payload slider
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def get_scatter_plot(selected_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    # If you don't have 'Booster Version Category', remove color param or replace with another column
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                     color='Booster Version Category' if 'Booster Version Category' in spacex_df.columns else 'Launch Site',
                     title='Payload Mass vs Launch Outcome',
                     labels={'class': 'Launch Outcome (1=Success, 0=Failure)'})
    return fig

# Run the Dash app
if __name__ == '__main__':
    app.run(debug=True)
