# src/pipeline/gui_plotly_static.py

import plotly.graph_objs as go
import plotly.offline as pyo
import webbrowser
import tempfile
import threading
from pipeline.environment import is_termux
import http.server
import time
from pathlib import Path
import os
import subprocess

buffer_lock = threading.Lock()  # Optional, if you want thread safety

# A simple HTTP server that serves files from the current directory.
# We suppress logging to keep the Termux console clean.
class PlotServer(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return
    
def show_static(plot_buffer):
    """
    Renders the current contents of plot_buffer as a static HTML plot.
    Does not listen for updates.
    """
    if plot_buffer is None:
        print("plot_buffer is None")
        return

    with buffer_lock:
        data = plot_buffer.get_all()

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    traces = []
    for i, (label, series) in enumerate(data.items()):
        scatter_trace = go.Scatter(
            x=series["x"],
            y=series["y"],
            mode="lines+markers",
            name=label,
        )
        # Explicitly set the line and marker color using update()
        # This is a robust way to ensure the properties are set
        
        scatter_trace.update(
            line=dict(
                color=colors[i],
                width=2
            ),
            marker=dict(
                color=colors[i],
                size=10,
                symbol='circle'
            )
        )   
        traces.append(scatter_trace)

    layout = go.Layout(
        title="EDS Data Plot (Static)",
        margin=dict(t=40),
        #colorway=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    )

    fig = go.Figure(data=traces, layout=layout)

    # Update the layout to position the legend at the top-left corner
    fig.update_layout(legend=dict(
    yanchor="auto",
    y=0.0,
    xanchor="auto",
    x=0.0,
    bgcolor='rgba(255, 255, 255, 0.1)',  # Semi-transparent background
    bordercolor='black',
    
    ))

    # Write to a temporary HTML file
    # Use Path to handle the temporary file path
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode='w', encoding='utf-8') as tmp_file:
        # Write the plot to the file
        pyo.plot(fig, filename=tmp_file.name, auto_open=False)
    #tmp_file.close()

    # Create a Path object from the temporary file's name
    #tmp_path = Path(tmp_file.name)
    # Get the absolute path of the temporary file.
    full_file_path = tmp_file.name
    # Use Path attributes to get the directory and filename
    #tmp_dir = tmp_path.parent
    #tmp_filename = tmp_path.name

    # If running in Windows, open the file directly
    #file_path = f"file://{tmp_file.name}"
    if not is_termux():
        webbrowser.open(Path(full_file_path).as_uri())
        return
    else:
    
        # You can find these for other apps using various tools.
        browser_package = 'com.android.chrome'
        browser_activity = 'com.google.android.apps.chrome.Main'

        # Construct the full command
        # Note: The file path must be in a file URI format.
        file_uri = f'content://com.termux.files{full_file_path}'
        command = [
            'am',
            'start',
            '-a', 'android.intent.action.VIEW',
            '-d', file_uri,
            '-n', f'{browser_package}/{browser_activity}'
        ]
        # Use subprocess.run() to execute the command
        try:
            #subprocess.run(['termux-open', file_path], check=True)
            subprocess.run(command, check=True)
            print(f"Successfully launched Chrome to view {full_file_path}.")
        except subprocess.CalledProcessError as e:
            print(f"Error launching browser: {e}")
        except FileNotFoundError:
            print("Error: The 'am' command was not found. Are you in a Termux environment with root or special permissions?")
        print(f"Successfully opened {full_file_path}")
        return
        
    # Start a temporary local server in a separate, non-blocking thread
    # Change the current working directory to the temporary directory.
    # This is necessary for the SimpleHTTPRequestHandler to find the file.
    # pathlib has no direct chdir equivalent, so we still use os.
    os.chdir(str(tmp_dir))
    PORT = 8000
    server_address = ('', PORT)
    try:
        httpd = http.server.HTTPServer(server_address, PlotServer)
        # Setting daemon=True ensures the server thread will exit when the main program does
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()
    except OSError as e:
        print(f"Error starting server on port {PORT}: {e}")
        print("This is likely because another process is using the port.")
        print("Please try again later or manually navigate to the file.")
        print(f"File path: {tmp_path}")
        return

    # Construct the local server URL
    tmp_url = f'http://localhost:{PORT}/{tmp_filename}'
    print(f"Plot server started. Opening plot at:\n{tmp_url}")
    
    # Open the local URL in the browser
    webbrowser.open(tmp_url)
    
    # Keep the main thread alive for a moment to allow the browser to open.
    # The server will run in the background until the script is manually terminated.
    print("\nPlot displayed. Press Ctrl+C to exit this script and stop the server.")
    try:
        while server_thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting.")
        httpd.shutdown()
        # Clean up the temporary file on exit
        if tmp_path.exists():
            tmp_path.unlink()
