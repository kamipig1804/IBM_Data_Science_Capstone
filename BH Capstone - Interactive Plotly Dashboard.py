# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

#
drop1_options = [{'label': 'All Sites', 'value': 'ALL'},]
distinct_sites = spacex_df["Launch Site"].unique()
                                
for site in distinct_sites:
    drop1_options.append({'label': site, 'value': site})


# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=drop1_options,
                                    value='ALL',
                                    placeholder="Select site",
                                    searchable=True
                                ),

                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0, 
                                    max=10000, 
                                    step=1000,
                                    value=[min_payload, max_payload]
                                    ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))

def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Take all successful launches    
        filtered_df = spacex_df[spacex_df["class"] == 1]
                
        # Count the number per Launch Site
        count_per_site = filtered_df["Launch Site"].value_counts()
                
        # Convert to df, reset_index and rename columns
        count_per_site_df = count_per_site.to_frame('Count').reset_index().sort_values("Launch Site") 

        fig = px.pie(
            count_per_site_df, 
            values='Count', 
            names="Launch Site", 
            title='Total Success Launches Per Site'
            )
        return fig

    else:
        # Take all successful launches    
        filtered_df = spacex_df[spacex_df["Launch Site"] == entered_site]
                
        # Count the number per Launch Site
        outcomes = filtered_df["class"].value_counts()
        
        # Convert to df, reset_index and rename columns
        outcomes_df = outcomes.to_frame('Count').reset_index().sort_values("class") 

        fig = px.pie(
            outcomes_df, 
            values='Count', 
            names="class", 
            title='Launches for site {}'.format(entered_site)
            )

        return fig

    
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), 
              Input(component_id='payload-slider', component_property="value")])

def get_pie_chart(entered_site, payload_range):
    if entered_site == 'ALL':

        filtered_df = spacex_df[spacex_df["Payload Mass (kg)"].between(payload_range[0], payload_range[1])]
        
        # Take all successful launches    
        fig = px.scatter(
            filtered_df, 
            x="Payload Mass (kg)", 
            y="class", 
            color="Booster Version Category",
            title='Correlation Between Payload and Success for All Sites (Booster Version in color)',
            )
        return fig

    else:
        # This launch site    
        filtered_df = spacex_df[spacex_df["Launch Site"] == entered_site]

        # In payload range
        filtered_df2 = filtered_df[filtered_df["Payload Mass (kg)"].between(payload_range[0], payload_range[1])]
        
        # Take all successful launches    
        fig = px.scatter(
            filtered_df2, 
            x="Payload Mass (kg)", 
            y="class", 
            color="Booster Version Category",
            title='Correlation Between Payload and Success for Site {} (Booster Version in color)'.format(entered_site),
            )
        return fig

# Run the app
if __name__ == '__main__':
    app.run(port=8051)
