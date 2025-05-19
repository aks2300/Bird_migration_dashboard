import dash_bootstrap_components as dbc
import pandas as pd 
import plotly.express as pex 
import plotly.graph_objects as go
from dash import Dash, html, dcc, callback, Output, Input 



df = pd.read_csv("bird_migration_data.csv")

app = Dash(__name__, external_stylesheets= [dbc.themes.BOOTSTRAP], title= "Bird Migration")


def create_Df(plot):
    if plot.lower() == "bar":
        barDf = pd.DataFrame({
        'region' : df.Region.unique().tolist(),
        'Successful' : df.Migration_Success[df.Migration_Success == "Successful"].groupby(pd.Categorical(df.Region[df.Migration_Success == "Successful"]), observed= True).count(),
        'Failed' : df.Migration_Success[df.Migration_Success == "Failed"].groupby(pd.Categorical(df.Region[df.Migration_Success == "Failed"]), observed= True).count()
        }, index=df.Region.unique().tolist())
        return barDf

def create_Arr(arr):
    resultArr = []
    for i in range(arr[0], arr[1]+1):
        resultArr.append(i)
    return resultArr

figBar = pex.bar(create_Df("bAr"), x = 'region', y = ['Successful', 'Failed'], barmode='group', labels= {'x': 'Region', 'y' : 'Count', 'color' : 'Migration Status'}
              ).update_layout(xaxis_title = 'Region', yaxis_title = 'Count', legend_title= 'Migration Status', clickmode= "event+select", template= "plotly_dark", title= "Bird Count")
barGraph = dbc.Col(dcc.Graph(id= "barGraph", figure= figBar, style={'width' : '50vw', 'height' : '50vh'}, config = {'responsive': True}), width = 'auto')

figPie = pex.pie(values= df.Species.value_counts(), names= df.Species.unique().tolist()).update_layout(template= "plotly_dark", title= "Species Population per Region")
pieGraph = dbc.Col(dcc.Graph(id = "pieGraph", figure = figPie, className="w-auto", config = {'responsive': True}))

title = [dbc.Col(html.H1('Bird Migration')), dbc.Col(html.P("Bird migration is one of the nature's fascinating processes. " \
    "Dig through this web app to gain insights on how different bird species migrate in this dashboard."), style= {"text-align": "right"})]

cardOne = dbc.Col(dbc.Card(dbc.CardBody([
    html.H4(id="cardOne", style={'textAlign': 'center', 'font-size' : '24px'}),
    html.Span(children="Main Reason of Migration", style = {'font-size' : '14px'}), 
]), class_name="w-100 d-inline-block text-white bg-dark"))

cardTwo = dbc.Col(dbc.Card(dbc.CardBody([
    html.Span("Longest Flight Distance", style= {"font-size" : "14px"}),
    html.H4(style= {"textAlign" : "center", "font-size" : "24x"}, id= "cardTwoF"),
    html.Br(),
    html.Span("Mean Flock Size", style= {"font-size" : "14px"}),
    html.H4(style= {"textAlign" : "center", "font-size" : "24px"}, id= "cardTwoS"), 
    html.Br(),
    html.Span("Minimum Altitude", style= {"font-size" : "14px"}),
    html.H4(style= {"textAlign" : "center", "font-size" : "24x"}, id= "cardTwoT")
]), class_name="d-inline-block text-white bg-dark w-100")) #, class_name="rounded border border-dark border-2"

form = dbc.Col(dbc.Card(dbc.CardBody([
    html.H4("Select region", style= {"font-size" : "14px"}, className="text-white"),
    dcc.Dropdown(df['Region'].unique().tolist(), "Asia", className= "text-dark", clearable= False, searchable= False, id= "region-dropdown"),
    html.Br(),
    html.H4("Select species", style= {"font-size" : "14px"}, className="text-white"),
    dcc.Dropdown(df['Species'].unique().tolist(), "Eagle", className= "text-dark", clearable= False, searchable= False, id= "species-dropdown"),
    html.Br(),
    html.H4("Number of rest stops", style= {"font-size" : "14px"}, className="text-white"),
    dcc.RangeSlider(1, 14, 1, count= 1, value= [3, 6], id= "reststops-slider")
]), class_name="d-inline-block text-white bg-dark w-100"), width = "auto", style = {'width' : '25rem'})

mapGraph = dbc.Col(dcc.Graph(id = "mapGraph", config= {'responsive': True}), width= "auto")

app.layout = dbc.Container([
    dbc.Row(title, class_name= "text-white"),
    dbc.Row([barGraph, dbc.Col([
        cardOne,
        html.Br(),
        cardTwo
    ], width = 'auto', style= {'width' : '15rem'}), pieGraph]),
    dbc.Row([form, mapGraph]),
    dbc.Row(html.A(html.Button("Refresh Data", className="w-100"), href="/")),
], fluid= True, class_name= "px-8", style = {"background-color" : "#101112"}) 

@callback(
    [Output('cardOne', 'children'), Output('cardTwoF', 'children'), Output('cardTwoS', 'children'), Output('cardTwoT', 'children'), Output('pieGraph', 'figure')],
    Input('barGraph', 'clickData')
)

def out(clickData):
    if not(clickData):
        migration_reason = df["Migration_Reason"].mode()[0]
        longest_distance = f"{df['Flight_Distance_km'].max()} km"
        mean_flock = round(df['Flock_Size'].mean(), 2)
        min_altitude = f"{df['Min_Altitude_m'].min()} m"
        fig = pex.pie(values= df.Species.value_counts(), names= df.Species.unique().tolist()).update_layout(template= "plotly_dark", title= "Species Population")
    else:
        migration_state = ""
        region = clickData['points'][0]['x']
        if clickData['points'][0]['curveNumber'] == 0:
            migration_state = "Successful"
        elif clickData['points'][0]['curveNumber'] == 1:
            migration_state = "Failed"

        migration_reason = df.Migration_Reason[(df.Region == region) & (df.Migration_Success == migration_state)].mode()[0]
        longest_distance = f"{df.Flight_Distance_km[(df.Region == region) & (df.Migration_Success == migration_state)].max()} km"
        mean_flock = round(df.Flock_Size[(df.Region == region) & (df.Migration_Success == migration_state)].mean(), 2)
        min_altitude = f"{df.Min_Altitude_m[(df.Region == region) & (df.Migration_Success == migration_state)].min()} m"
        fig = pex.pie(values= df.Species[df.Region == region].value_counts(), names= df.Species.unique().tolist()).update_layout(template= "plotly_dark", title= "Species Population per Region")
    return migration_reason, longest_distance, mean_flock, min_altitude, fig

@callback(
    Output('mapGraph', 'figure'),
    [Input('region-dropdown', 'value'), Input('species-dropdown', 'value'), Input('reststops-slider', 'value')]
)

def geo_map(region, species, restStop):
    filtered_df = df[(df['Region'] == region) & (df['Species'] == species) & (df['Rest_Stops'].isin(create_Arr(restStop)))]  
    modified_df = pd.DataFrame({
        'lat' : pd.concat([filtered_df['Start_Latitude'], filtered_df['End_Latitude']]),
        'lon' : pd.concat([filtered_df['Start_Longitude'], filtered_df['End_Longitude']]),
        'line_id' : sum([[i] *2 for i in filtered_df.index], [])
    })
    return pex.line_geo(modified_df, lat = 'lat', lon = 'lon', color = 'line_id', line_group= 'line_id', projection='natural earth', height= 450).update_layout(template= "plotly_dark", title= "Migration paths of the birds")


if __name__ == "__main__":
    app.run(debug= True)
