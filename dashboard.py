import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px
import os
from dash.dependencies import Input, Output

LOG_FILE = "logs.csv"

# Configure Dash to serve assets locally instead of from CDN
app = dash.Dash(__name__, serve_locally=True)
app.title = "Ping Monitor Dashboard"

# Additional configuration to ensure assets load properly
app.config.suppress_callback_exceptions = True

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
    try:
        if not os.path.exists(LOG_FILE):
            return [], []
        df = pd.read_csv(LOG_FILE)
        if df.empty:
            return [], []
        hosts = df['host'].unique()
        options = [{'label': h, 'value': h} for h in hosts]
        return options, hosts.tolist()
    except Exception as e:
        print(f"Error updating dropdown: {e}")
        return [], []

@app.callback(
    Output('latency-graph', 'figure'),
    Input('host-selector', 'value'),
    Input('interval', 'n_intervals')
)
def update_graph(selected_hosts, _):
    try:
        if not selected_hosts or not os.path.exists(LOG_FILE):
            return px.line(title="Waiting for data...")

        df = pd.read_csv(LOG_FILE)
        if df.empty:
            return px.line(title="No data available")
            
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df[df['latency_ms'] != "timeout"]
        
        if df.empty:
            return px.line(title="No valid latency data")
            
        df['latency_ms'] = df['latency_ms'].astype(float)
        df = df[df['host'].isin(selected_hosts)]
        
        if df.empty:
            return px.line(title="No data for selected hosts")
            
        fig = px.line(df, x='timestamp', y='latency_ms', color='host', title="Latency Over Time")
        fig.update_layout(
            transition_duration=500,
            xaxis_title="Time",
            yaxis_title="Latency (ms)"
        )
        return fig
    except Exception as e:
        print(f"Error updating graph: {e}")
        return px.line(title=f"Error loading data: {str(e)}")

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))
