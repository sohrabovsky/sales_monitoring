# Use Flight International Ticket 2 Table with 
# Issue State is Successful filter


import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

intflight = pd.read_csv("intflight.csv", dtype={"Phone Number": str, "Booking Date": str, "Departure Date": str})
intflight["Booking Date"] = intflight["Booking Date"].str[:10]
intflight["Departure Date"] = intflight["Departure Date"].str[:10]
intflight = intflight.dropna(subset=["Book ID"])

routes = intflight.groupby('Route')['Book ID'].count().sort_values(ascending=False)

top_routes = (
    intflight.groupby(["Route"])["Book ID"]
    .count()
    .sort_values(ascending=False)[:5]
    .index
)

df = intflight.groupby("Booking Date")["Book ID"].count()
fig_total_sale = px.line(x=df.index, y=df.values)
moving_average = df.rolling(window=7).mean()
fig_total_sale.add_trace(
    go.Scatter(x=moving_average.index, y=moving_average.values, name="Moving Average")
)
fig_total_sale.update_layout(
    title= 'Sales per Day',
    template="plotly_white",
    xaxis= dict(title='Date'),
    yaxis= dict(title= 'Sales'))

### Pie Chart for route contribution
df = intflight.groupby("Route")["Book ID"].count().sort_values(ascending=False)
dff = df[:5].to_frame()
dff.loc["other", "Book ID"] = df[5:].sum()
fig_route_perc = px.pie(
    dff,
    values=dff["Book ID"],
    names=dff.index,
)
fig_route_perc.update_layout(
    title= 'Sales Contribution in Top Routes',
    template="plotly_white")

# Top Routes trend in one chart

fig_top_route_trend= go.Figure()
for route in top_routes:
    df = intflight[intflight["Route"] == route]
    dff = df.groupby(["Booking Date"])["Book ID"].count()
    x = dff.index
    y = dff.values
    fig_top_route_trend.add_trace(go.Scatter(x=x, y=y, name=route, mode="lines"))
fig_top_route_trend.update_layout(title="Top Routes Sales Trend",
                                  template="plotly_white",
                                  xaxis= dict(title='Date'),
                                  yaxis= dict(title='Sales'))

# Long Haul Vs Short Haul

long_short = pd.read_excel("long_short.xlsx", sheet_name="Short")
long_short.rename(columns={"Unnamed: 0": "Route"}, inplace=True)
long_short.dropna(subset="Route", inplace=True)
long_short = long_short[["Route"]]

long_short_nassim = pd.read_excel("long_short_nassim.xlsx", usecols=["Route"])

index = intflight[intflight["Route"].isin(long_short["Route"])].index
intflight.loc[index, "route_type"] = "short"
index = intflight[intflight["route_type"].isna()].index
intflight.loc[index, "route_type"] = "long"

route_types = intflight["route_type"].unique()

df = intflight.groupby("route_type")["Book ID"].count().sort_values(ascending=False)
df = df.to_frame()
fig_route_type_perc = px.pie(
    df,
    values=df["Book ID"],
    names=df.index,
)
fig_route_type_perc.update_layout(
    title="Short Hauls Vs Long Hauls contribution in sales",
    template="plotly_white")



app = Dash(__name__)

# Set up the app layout
app.layout = html.Div([
    html.H1('Total Sales'),
    dcc.Graph(figure= fig_total_sale),
    
    html.H1("Sales by Route"),
    dcc.Graph(figure= fig_top_route_trend),
    html.P("Select Routs"),
    dcc.Dropdown(
        id='route-name',
        options= [{'label': route, 'value': route} for route in routes.index],
        value= routes.index[0],
        style= {'width' : '1000px'}
    ),
    dcc.Graph(id="sales_by_route_name",style={'width': '50%', 'display': 'inline-block'}),
    dcc.Graph(figure= fig_route_perc, style={'width': '50%', 'display': 'inline-block'}),
    
    html.H1("Long Haul Vs Short Haul"),
    html.P("Select Route Type"),
    dcc.Dropdown(
        id='route-type',
        options= [{'label': route_type, 'value': route_type} for route_type in route_types],
        value= route_types[0],
        style= {'width' : '1000px'}
    ),
    dcc.Graph(id= 'sales_by_route_type',style={'width': '50%', 'display': 'inline-block'}),
    dcc.Graph(figure= fig_route_type_perc, style={'width': '50%', 'display': 'inline-block'}),
    
    
])

@app.callback(
    Output("sales_by_route_name", "figure"), 
    Input("route-name", "value"))    
def chart_route(route):
    # trend by top routes
    df = intflight[intflight["Route"] == route]
    dff = df.groupby(["Booking Date"])["Book ID"].count()
    x = dff.index
    y = dff.values
    fig = px.line(x=x, y=y,title=route)
    moving_average = dff.rolling(window=7).mean()
    fig.add_trace(
        go.Scatter(
            x=moving_average.index, y=moving_average.values, name="moving_average"
        )
    )
    fig.update_layout(
        template="plotly_white",
        xaxis= dict(title='Date'),
        yaxis= dict(title= 'Sales')
        )
    return fig
@app.callback(
    Output("sales_by_route_type", "figure"), 
    Input("route-type", "value"))  
def chart_route_type(route_type):
    # trend by route type
    df = intflight[intflight["route_type"] == route_type]
    dff = df.groupby(["Booking Date"])["Book ID"].count()
    x = dff.index
    y = dff.values
    fig = px.line(x=x, y=y,title=route_type)
    moving_average = dff.rolling(window=7).mean()
    fig.add_trace(
        go.Scatter(
            x=moving_average.index, y=moving_average.values, name="moving_average"
        )
    )
    fig.update_layout(
        template="plotly_white",
        xaxis= dict(title= 'Date'),
        yaxis= dict(title='Sales'))
    return fig
if __name__ == "__main__":
    app.run_server(debug=True)
