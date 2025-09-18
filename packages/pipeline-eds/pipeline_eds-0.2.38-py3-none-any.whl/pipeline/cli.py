import sqlite3
from rich.table import Table
from rich.console import Console
import typer
import importlib
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError

from pipeline.env import SecretConfig
from pipeline.time_manager import TimeManager
from pipeline.create_sensors_db import get_db_connection, create_packaged_db, reset_user_db # get_user_db_path, ensure_user_db, 
from pipeline.api.eds import demo_eds_webplot_point_live

#from pipeline.helpers import setup_logging
### Versioning
CLI_APP_NAME = "pipeline"
PIP_PACKAGE_NAME = "pipeline-eds"
def print_version(value: bool):
    if value:
        try:
            typer.secho(f"{CLI_APP_NAME} {PIPELINE_VERSION}",fg=typer.colors.GREEN, bold=True)
        except PackageNotFoundError:
            typer.echo("Version info not found")
        raise typer.Exit()
try:
    PIPELINE_VERSION = version(PIP_PACKAGE_NAME)
    __version__ = version(PIP_PACKAGE_NAME)
except PackageNotFoundError:
    PIPELINE_VERSION = "unknown"

try:
    from importlib.metadata import version
    __version__ = version(PIP_PACKAGE_NAME)
except PackageNotFoundError:
    # fallback if running from source
    try:
        with open(Path(__file__).parent / "VERSION") as f:
            __version__ = f.read().strip()
    except FileNotFoundError:
        __version__ = "dev"

### Pipeline CLI

app = typer.Typer(help="CLI for running pipeline workspaces.")
console = Console()

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(None, "--version", callback=lambda v: print_version(v), is_eager=True, help="Show the version and exit.")
    ):
    """
    Pipeline CLI – run workspaces built on the pipeline framework.
    """
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()

@app.command()
def reset_db():
    """Reset the user DB from the packaged default, and from the hardcoded list."""
    """There should be a way to ship plant specific packaged DB, so it is not hardcoded. Probably the same way we can ship secrets. Log in, get JSON via API, write, generate file.""" 
    #user_db = get_user_db_path()
    #if user_db.exists():
    #    user_db.unlink()
    #ensure_user_db()

    packaged_db = create_packaged_db()
    user_db = reset_user_db(packaged_db)

@app.command()
def list_sensors(db_path: str = None):
    """ See a cheatsheet of commonly used sensors from the database."""
    # db_path: str = "sensors.db"
    if db_path is not None:
        conn = sqlite3.connect(db_path)
    else:  
        conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT idcs, iess, zd, units, description FROM sensors")
    rows = cur.fetchall()
    conn.close()

    table = Table(title="Common Sensor Cheat Sheet (hard-coded)")
    table.add_column("IDCS", style="cyan")
    #table.add_column("IESS", style="magenta") # no reason to show this
    table.add_column("ZD", style="green")
    table.add_column("UNITS", style="white")
    table.add_column("DESCRIPTION", style="white")
    

    for idcs, iess, zd, units, description in rows:
        table.add_row(idcs, zd,units, description)
        

    console.print(table)
    console.print("⚠️ The ZD for the Stiles plant is WWTF", style = "magenta")

@app.command()
def live_query(
    idcs: list[str] = typer.Argument(..., help="Provide known idcs values that match the given zd."), # , "--idcs", "-i"
    zd: str = typer.Option('Maxson', "--zd", "-z", help = "Define the EDS ZD from your secrets file. This must correlate with your idcs point selection(s)."),
    webplot: bool = typer.Option(False,"--webplot","-w",help = "Use a web-based plot (plotly) instead of matplotlib. Useful for remote servers without display.")
):
    """live data plotting, based on CSV query files. Coming soon - call any, like the 'trend' command."""
    demo_eds_webplot_point_live()
@app.command()
def trend(
    idcs: list[str] = typer.Argument(..., help="Provide known idcs values that match the given zd."), # , "--idcs", "-i"
    starttime: str = typer.Option(None, "--start", "-s", help="Identify start time. Use any reasonable format, to be parsed automatically. If you must use spaces, use quotes."),
    endtime: str = typer.Option(None, "--end", "-end", help="Identify end time. Use any reasonable format, to be parsed automatically. If you must use spaces, use quotes."),
    zd: str = typer.Option('Maxson', "--zd", "-z", help = "Define the EDS ZD from your secrets file. This must correlate with your idcs point selection(s)."),
    workspacename: str = typer.Option(None,"--workspace","-w", help = "Provide the name of the workspace you want to use, for the secrets.yaml credentials and for the timezone config. If a start time is not provided, the workspace queries can checked for the most recent successful timestamp. "),
    print_csv: bool = typer.Option(False,"--print-csv","-p",help = "Print the CSV style for pasting into Excel."),
    step_seconds: int = typer.Option(None, "--step-seconds", help="You can explicitly provide the delta between datapoints. If not, ~400 data points will be used, based on the nice_step() function."), 
    webplot: bool = typer.Option(False,"--webplot","-w",help = "Use a browser-based plot instead of local (matplotlib). Useful for remote servers without display.")
    ):
    """
    Show a curve for a sensor over time.
    """
    #from dateutil import parser
    import pendulum
    from pipeline.api.eds import EdsClient, load_historic_data
    from pipeline import helpers
    from pipeline.plotbuffer import PlotBuffer
    from pipeline import environment
    from pipeline.workspace_manager import WorkspaceManager
    #workspaces_dir = WorkspaceManager.ensure_appdata_workspaces_dir()      

    # must set up %appdata for pip/x installation. Use mulch or yeoman for this. And have a secrets filler.
    if workspacename is None:
        workspacename = WorkspaceManager.identify_default_workspace_name()
    wm = WorkspaceManager(workspacename)
    secrets_file_path = wm.get_secrets_file_path()
    secrets_dict = SecretConfig.load_config(secrets_file_path)

    if zd.lower() == "stiles":
        zd = "WWTF"

    if zd == "Maxson":
        idcs_to_iess_suffix = ".UNIT0@NET0"
    elif zd == "WWTF":
        idcs_to_iess_suffix = ".UNIT1@NET1"
    else:
        # assumption for generic system
        idcs_to_iess_suffix = ".UNIT0@NET0"
    iess_list = [x+idcs_to_iess_suffix for x in idcs]
    print(f"iess_list = {iess_list}")

    base_url = secrets_dict.get("eds_apis", {}).get(zd, {}).get("url").rstrip("/")
    session = EdsClient.login_to_session(api_url = base_url,
                                                username = secrets_dict.get("eds_apis", {}).get(zd, {}).get("username"),
                                                password = secrets_dict.get("eds_apis", {}).get(zd, {}).get("password"))
    session.base_url = base_url
    session.zd = secrets_dict.get("eds_apis", {}).get(zd, {}).get("zd")


    # Get units for the iess values
    #decoded_str = EdsClient.get_points_export(session, iess_list=iess_list)
    #print(f"decoded_str = {decoded_str}")
    # # Get the parsed dictionary
    points_data = EdsClient.get_points_metadata(session, iess_list=iess_list)
    #
    # # Now you can easily access the unit for 'M100FI.UNIT0@NET0'
    #unit = points_data.get('M100FI.UNIT0@NET0', {}).get('UN')
    # print(f"The unit for M100FI.UNIT0@NET0 is: {unit}")
    #
    # # You can also iterate through the results
    #for iess, attributes in points_data.items():
    #    print(f"Point: {iess}, Description: {attributes.get('DESC')}, Unit: {attributes.get('UN')}")
    
    
    
    if starttime is None:
        # back_to_last_success = True
        from pipeline.queriesmanager import QueriesManager
        queries_manager = QueriesManager(wm)
        dt_start = queries_manager.get_most_recent_successful_timestamp(api_id=zd)
    else:
        dt_start = pendulum.parse(helpers.sanitize_date_input(starttime), strict=False)
    if endtime is None:
        dt_finish = helpers.get_now_time_rounded(wm)
    else:
        dt_finish = pendulum.parse(helpers.sanitize_date_input(endtime), strict=False)

    # Should automatically choose time step granularity based on time length; map 
    if step_seconds is None:
        step_seconds = helpers.nice_step(TimeManager(dt_finish).as_unix()-TimeManager(dt_start).as_unix()) # TimeManager(starttime).as_unix()
    results = load_historic_data(session, iess_list, dt_start, dt_finish, step_seconds) 
    if not results:
        return 
    # results is a list of lists. Each inner list is a separate curve.
    # The PlotBuffer instance is created once, outside the loop.
    data_buffer = PlotBuffer() 
    # 'results' is a list of lists. Each inner list is a separate curve.
    for idx, rows in enumerate(results):
        # This line is the key.
        # We create a unique label for each of the 'rows' in the outer loop.
        # The plot will use this label to draw a separate line for each 'rows'.
        
        attributes = points_data[iess_list[idx]]
        label = f"{idcs[idx]}, {attributes.get('DESC')}, {attributes.get('UN')}"
        #label = idcs[idx]
        # The raw from EdsClient.get_tabular_trend() is brought in like this: 
        #   sample = [1757763000, 48.93896783431371, 'G'] 
        #   and then is converted to a dictionary with keys: ts, value, quality
        for row in rows:
            ts = helpers.iso(row.get("ts"))
            av = row.get("value")
            
            # All data is appended to the *same* data_buffer,
            # but the unique 'label' tells the buffer which series it belongs to.
            data_buffer.append(label, ts, av)

    # Once the loop is done, you can call your show_static function
    # with the single, populated data_buffer.

    if not environment.matplotlib_enabled() or webplot:
        from pipeline import gui_plotly_static
        #gui_fastapi_plotly_live.run_gui(data_buffer)
        gui_plotly_static.show_static(data_buffer)
    else:
        from pipeline import gui_mpl_live
        #gui_mpl_live.run_gui(data_buffer)
        gui_mpl_live.show_static(data_buffer)
    
    if print_csv:
        print(f"Time,\\{iess_list[0]}\\,")
        for idx, rows in enumerate(results):
            for row in rows:
                print(f"{helpers.iso(row.get('ts'))},{row.get('value')},")
    

@app.command()
def list_workspaces():
    """
    List all available workspaces detected in the workspaces folder.
    """
    # Determine workspace name
    from pipeline.workspace_manager import WorkspaceManager

    workspaces = WorkspaceManager.get_all_workspaces_names()
    typer.echo("📦 Available workspaces:")
    for name in workspaces:
        typer.echo(f" - {name}")


@app.command()
def build_secrets():
    """
    Use a filler tool to add API URLs, usernames, passwords, etc.
    """
    pass


@app.command()
def ping(
    eds: bool = typer.Option(False,"--eds","-e",help = "Limit the pinged URL's to just the EDS services known to the configured secrets.")
    ):
    """
    Ping all HTTP/S URL's found in the secrets configuration.
    """
    from pipeline.calls import call_ping, find_urls, find_eds_urls
    from pipeline.env import SecretConfig
    from pipeline.workspace_manager import WorkspaceManager
    import logging

    logger = logging.getLogger(__name__)
    workspace_name = WorkspaceManager.identify_default_workspace_name()
    workspace_manager = WorkspaceManager(workspace_name)

    secrets_dict = SecretConfig.load_config(secrets_file_path = workspace_manager.get_secrets_file_path())
    
    if not eds:
        url_set = find_urls(secrets_dict)
    else:
        url_set = find_eds_urls(secrets_dict)

    typer.echo(f"Found {len(url_set)} URLs in secrets configuration.")
    logger.info(f"url_set: {url_set}")
    for url in url_set:
        print(f"ping url: {url}")
        call_ping(url)

@app.command()
def help():
    """
    Show help information.
    """
    typer.echo(app.get_help())

if __name__ == "__main__":
    app()
