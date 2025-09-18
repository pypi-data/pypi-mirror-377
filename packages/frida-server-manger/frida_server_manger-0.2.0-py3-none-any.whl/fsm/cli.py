import sys
import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich import print as rich_print
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

from fsm.core import (
    check_adb_connection as core_check_adb,
    install_frida_server as core_install,
    run_frida_server as core_run,
    list_frida_server as core_list,
    get_running_processes as core_ps,
    kill_frida_server as core_kill
)

app = typer.Typer(
    name="fsm",
    help="frida-server manager for Android devices",
    add_completion=False,
    rich_markup_mode="rich"
)

console = Console()


def print_success(message: str):
    """Print success message with green color"""
    rich_print(f"[bold green]✓ {message}[/bold green]")


def print_error(message: str):
    """Print error message with red color"""
    rich_print(f"[bold red]✗ {message}[/bold red]")


def print_warning(message: str):
    """Print warning message with yellow color"""
    rich_print(f"[bold yellow]⚠ {message}[/bold yellow]")


def print_info(message: str):
    """Print info message with blue color"""
    rich_print(f"[bold blue]ℹ {message}[/bold blue]")


@app.command()
def check(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Check ADB connection to devices"""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(description="Checking ADB connection...", total=None)

            # Import and run the core function
            from fsm.core import run_command

            output = run_command('adb devices', verbose)

            if output is None:
                print_error("ADB is not installed or not in PATH")
                raise typer.Exit(1)

            # Check if there are any devices connected
            devices = [line for line in output.splitlines() if 'device' in line and not line.startswith('List of')]

            progress.update(task, completed=True)

            if not devices:
                print_error("No devices connected via ADB")
                raise typer.Exit(1)

            print_success(f"{len(devices)} device(s) connected")

            if verbose:
                for device in devices:
                    print_info(f"  {device}")

    except Exception as e:
        print_error(f"Error checking ADB connection: {e}")
        raise typer.Exit(1)


@app.command()
def install(
    version: Optional[str] = typer.Argument(None, help="Specific version of frida-server to install"),
    repo: str = typer.Option("frida/frida", "--repo", "-r", help="Custom GitHub repository (owner/repo format)"),
    keep_name: bool = typer.Option(False, "--keep-name", "-k", help="Keep the original name when installing"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Custom name for frida-server on the device"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Install frida-server on the device"""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(description="Installing frida-server...", total=None)

            # Run installation
            result = core_install(version, verbose, repo, keep_name, name)

            progress.update(task, completed=True)

            print_success(f"Successfully installed frida-server")
            print_info(f"Location: {result}")

            if version:
                print_info(f"To run this version: fsm run -V {version}")

    except SystemExit as e:
        raise typer.Exit(e.code)
    except Exception as e:
        print_error(f"Error installing frida-server: {e}")
        raise typer.Exit(1)


@app.command()
def run(
    dir: Optional[str] = typer.Option(None, "--dir", "-d", help="Custom directory to run frida-server from"),
    params: Optional[str] = typer.Option(None, "--params", "-p", help="Additional parameters for frida-server"),
    version: Optional[str] = typer.Option(None, "--version", "-V", help="Specific version of frida-server to run"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Custom name of frida-server to run"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Run frida-server on the device"""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(description="Starting frida-server...", total=None)

            # Run frida-server
            core_run(dir, params, verbose, version, name)

            progress.update(task, completed=True)

    except SystemExit as e:
        raise typer.Exit(e.code)
    except Exception as e:
        print_error(f"Error running frida-server: {e}")
        raise typer.Exit(1)


@app.command()
def list(
    dir: Optional[str] = typer.Option(None, "--dir", "-d", help="Custom directory to list frida-server files from"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """List frida-server files on the device and show their versions"""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(description="Listing frida-server files...", total=None)

            # Get the list of files
            from fsm.core import run_command, get_frida_server_version, DEFAULT_INSTALL_DIR

            server_dir = dir if dir else DEFAULT_INSTALL_DIR
            output = run_command(f"adb shell ls {server_dir} | grep frida-server", verbose)

            progress.update(task, completed=True)

            if not output:
                print_warning(f"No frida-server files found in {server_dir}")
                return

            # Process the files and get their versions
            files = output.strip().split('\n')

            # Create a rich table
            table = Table(title=f"Frida-Server Files in {server_dir}")
            table.add_column("Filename", style="cyan", no_wrap=True)
            table.add_column("Version", style="green")

            # Process each file and get its version
            for file in files:
                filename = file.strip()
                remote_path = f"{server_dir}/{filename}"
                version = get_frida_server_version(remote_path, verbose)
                table.add_row(filename, version if version else "Unknown")

            console.print(table)

    except Exception as e:
        print_error(f"Error listing frida-server files: {e}")
        raise typer.Exit(1)


@app.command()
def ps(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Filter processes by name"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """List running processes on the device"""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(description="Checking running processes...", total=None)

            # Get running processes
            from fsm.core import run_command

            search_name = name if name else "frida-server"
            cmd = f"adb shell ps -A | grep {search_name}"
            output = run_command(cmd, verbose)

            progress.update(task, completed=True)

            if not output:
                print_warning(f"No running processes found matching '{search_name}'")
                return

            # Process the output
            lines = output.strip().split('\n')

            # Create a rich table
            table = Table(title=f"Running Processes matching '{search_name}'")
            table.add_column("PID", style="cyan", no_wrap=True)
            table.add_column("User", style="yellow")
            table.add_column("Memory", style="blue")
            table.add_column("Command", style="green")

            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 8:
                    pid = parts[1]
                    user = parts[0]
                    memory = parts[4]
                    command = ' '.join(parts[7:])
                    table.add_row(pid, user, memory, command)

            console.print(table)

    except Exception as e:
        print_error(f"Error checking processes: {e}")
        raise typer.Exit(1)


@app.command()
def kill(
    pid: Optional[str] = typer.Option(None, "--pid", "-p", help="Specific PID of process to kill"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Process name to kill"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Kill frida-server process(es) on the device"""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(description="Killing processes...", total=None)

            # Kill processes
            core_kill(pid, verbose, name)

            progress.update(task, completed=True)

    except SystemExit as e:
        raise typer.Exit(e.code)
    except Exception as e:
        print_error(f"Error killing processes: {e}")
        raise typer.Exit(1)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """
    frida-server manager for Android devices

    When called without a command, checks ADB connection.
    """
    if ctx.invoked_subcommand is None:
        # No command provided, check ADB connection
        check(verbose)


if __name__ == "__main__":
    app()