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
            print("LOG_FILE does not exist")
            return [], []
        df = pd.read_csv(LOG_FILE)
        if df.empty:
            print("DataFrame is empty")
            return [], []
        hosts = df['host'].unique()
        print(f"Found hosts: {hosts}")
        options = [{'label': h, 'value': h} for h in hosts]
        # Return all hosts as selected by default
        return options, hosts.tolist()
    except Exception as e:
        print(f"Error updating dropdown: {e}")
        import traceback
        traceback.print_exc()
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
        print(f"Raw data shape: {df.shape}")
        print(f"Selected hosts: {selected_hosts}")
        
        if df.empty:
            return px.line(title="No data available")
            
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filter out timeout entries before converting to float
        print(f"Data before timeout filter: {len(df)} rows")
        df = df[df['latency_ms'] != "timeout"]
        print(f"Data after timeout filter: {len(df)} rows")
        
        if df.empty:
            return px.line(title="No valid latency data")
        
        # Convert latency to numeric, handling any potential issues
        df['latency_ms'] = pd.to_numeric(df['latency_ms'], errors='coerce')
        df = df.dropna(subset=['latency_ms'])  # Remove any NaN values
        print(f"Data after numeric conversion: {len(df)} rows")
        
        # Filter by selected hosts
        df = df[df['host'].isin(selected_hosts)]
        print(f"Data after host filter: {len(df)} rows")
        
        if df.empty:
            return px.line(title="No data for selected hosts")
        
        # Get recent data (last 1000 points for better performance)
        df = df.tail(1000)
        print(f"Final data shape for plotting: {df.shape}")
            
        fig = px.line(df, x='timestamp', y='latency_ms', color='host', title="Latency Over Time")
        fig.update_layout(
            transition_duration=500,
            xaxis_title="Time",
            yaxis_title="Latency (ms)"
        )
        return fig
    except Exception as e:
        print(f"Error updating graph: {e}")
        import traceback
        traceback.print_exc()
        return px.line(title=f"Error loading data: {str(e)}")

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))
