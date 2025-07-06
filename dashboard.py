import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px
import os
from dash.dependencies import Input, Output

LOG_FILE = "logs.csv"

app = dash.Dash(__name__)
app.title = "Ping Monitor Dashboard"

app.layout = html.Div([
    html.H1("📡 Real-Time Ping Monitor Dashboard"),
    dcc.Dropdown(id='host-selector', multi=True),
    dcc.Graph(id='latency-graph'),
    dcc.Interval(id='interval', interval=3000, n_intervals=0),  # 3s refresh
])

@app.callback(
    Output('host-selector', 'options'),
    Output('host-selector', 'value'),
    Input('interval', 'n_intervals')
)
def update_host_dropdown(_):
    if not os.path.exists(LOG_FILE):
        return [], []
    df = pd.read_csv(LOG_FILE)
    hosts = df['host'].unique()
    options = [{'label': h, 'value': h} for h in hosts]
    return options, hosts.tolist()

@app.callback(
    Output('latency-graph', 'figure'),
    Input('host-selector', 'value'),
    Input('interval', 'n_intervals')
)
def update_graph(selected_hosts, _):
    if not selected_hosts or not os.path.exists(LOG_FILE):
        return px.line(title="Waiting for data...")

    df = pd.read_csv(LOG_FILE)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df[df['latency_ms'] != "timeout"]
    df['latency_ms'] = df['latency_ms'].astype(float)
    df = df[df['host'].isin(selected_hosts)]
    fig = px.line(df, x='timestamp', y='latency_ms', color='host', title="Latency Over Time")
    fig.update_layout(transition_duration=500)
    return fig

if __name__ == "__main__":
    app.run(debug=False)
