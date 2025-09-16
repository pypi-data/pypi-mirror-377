import lzma
import os
import subprocess
import sys
import lzma
from pathlib import Path

import requests

# GitHub API URL for Frida releases
GITHUB_RELEASES_URL = "https://api.github.com/repos/frida/frida/releases"
DEFAULT_INSTALL_DIR = '/data/local/tmp'


def run_command(cmd, verbose=False, return_error=False):
    """Run a shell command and return the output"""
    if verbose:
        print(f"Running command: {cmd}")

    try:
        result = subprocess.run(cmd, shell=True, check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True)

        if return_error:
            if verbose:
                print(f"Command output: {result.stderr}")
            return result.stderr
        else:
            if verbose:
                print(f"Command output: {result.stdout}")
            return result.stdout
    except subprocess.CalledProcessError as e:
        if verbose:
            print(f"Command failed: {e.stderr}")
        return None


def check_adb_connection(verbose=False):
    """Check if ADB is connected to any device"""
    print("Checking ADB connection...")
    output = run_command('adb devices', verbose)

    if output is None:
        print("Error: ADB is not installed or not in PATH")
        sys.exit(1)

    # Check if there are any devices connected
    devices = [line for line in output.splitlines() if 'device' in line and not line.startswith('List of')]

    if not devices:
        print("Error: No devices connected via ADB")
        sys.exit(1)

    print(f"Success: {len(devices)} device(s) connected")
    if verbose:
        for device in devices:
            print(f"  {device}")


def get_latest_frida_version(repo="frida/frida", verbose=False):
    """Get the latest version of frida from GitHub"""
    if verbose:
        print(f"Fetching latest version from GitHub repository: {repo}")

    try:
        url = f"https://api.github.com/repos/{repo}/releases/latest"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        latest_version = data["tag_name"].strip('v')  # Remove 'v' prefix if present
        if verbose:
            print(f"Latest version: {latest_version}")
        return latest_version
    except Exception as e:
        if verbose:
            print(f"Error fetching latest version: {e}")
        return None


def get_frida_server_arch(verbose=False):
    """Determine the architecture of the Android device for frida-server"""
    if verbose:
        print("Determining Android device architecture...")

    # Get the architecture info from the device
    arch_info = run_command("adb shell getprop ro.product.cpu.abi", verbose)

    if not arch_info:
        print("Error: Could not determine device architecture")
        sys.exit(1)

    arch_info = arch_info.strip()

    # Map Android architecture to frida-server architecture
    if 'arm64' in arch_info:
        frida_arch = "android-arm64"
    elif 'armeabi' in arch_info:
        frida_arch = "android-arm"
    elif 'x86_64' in arch_info:
        frida_arch = "android-x86_64"
    elif 'x86' in arch_info:
        frida_arch = "android-x86"
    else:
        print(f"Error: Unsupported architecture: {arch_info}")
        sys.exit(1)

    if verbose:
        print(f"Device architecture: {arch_info} -> Frida architecture: {frida_arch}")

    return frida_arch


def download_frida_server(version=None, repo="frida/frida", verbose=False):
    """Download frida-server for Android"""
    # Get the latest version if not specified
    if not version:
        version = get_latest_frida_version(repo, verbose)
        if not version:
            print("Error: Could not determine the latest version")
            sys.exit(1)

    # Determine the architecture
    frida_arch = get_frida_server_arch(verbose)

    # Construct the download URL with .xz extension
    download_url = f"https://github.com/{repo}/releases/download/{version}/frida-server-{version}-{frida_arch}.xz"

    # Create the download directory if it doesn't exist
    local_path = Path("/tmp")
    local_path.mkdir(parents=True, exist_ok=True)

    # Paths for compressed and extracted files
    compressed_file = local_path / f"frida-server-{version}-{frida_arch}.xz"
    extracted_file = local_path / f"frida-server-{version}"

    if verbose:
        print(f"Downloading frida-server-{version}-{frida_arch}.xz from {download_url}")
        print(f"Saving compressed file to {compressed_file}")

    try:
        # Download the compressed file
        response = requests.get(download_url, stream=True, timeout=30)
        response.raise_for_status()

        with open(compressed_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        if verbose:
            print(f"Download completed: {compressed_file}")
            print(f"Extracting to {extracted_file}")

        # Extract the .xz file
        with lzma.open(compressed_file, 'rb') as f_in:
            with open(extracted_file, 'wb') as f_out:
                f_out.write(f_in.read())

        if verbose:
            print(f"Extraction completed: {extracted_file}")
            # Remove the compressed file
            os.remove(compressed_file)
            print(f"Removed compressed file: {compressed_file}")

        # Make the extracted file executable
        os.chmod(extracted_file, 0o755)
        if verbose:
            print(f"Made the file executable")

        return str(extracted_file)
    except Exception as e:
        if verbose:
            print(f"Error downloading frida-server: {e}")
        print(f"Error: Could not download frida-server from {download_url}")
        sys.exit(1)


def install_frida_server(version=None, verbose=False, repo="frida/frida", keep_name=False, custom_name=None):
    """Install frida-server on the Android device"""
    check_adb_connection(verbose)

    # Download frida-server
    local_path = download_frida_server(version, repo, verbose)

    # Determine the remote path
    if version and not keep_name and not custom_name:
        remote_path = f"{DEFAULT_INSTALL_DIR}/frida-server-{version}"
    elif custom_name:
        remote_path = f"{DEFAULT_INSTALL_DIR}/{custom_name}"
    else:
        remote_path = f"{DEFAULT_INSTALL_DIR}/frida-server"

    if verbose:
        print(f"Installing frida-server to {remote_path}")

    # Push the file to the device
    output = run_command(f"adb push {local_path} {remote_path}", verbose, return_error=True)
    if not output or "1 file pushed" not in output:
        print("Error: Failed to push frida-server to the device")
        sys.exit(1)

    # Make the file executable on the device
    output = run_command(f"adb shell chmod 755 {remote_path}", verbose)

    if verbose:
        print("Successfully installed frida-server")

    return remote_path


def get_frida_server_version(remote_path, verbose=False):
    """Get the version of frida-server from the device"""
    if verbose:
        print(f"Checking version of frida-server at {remote_path}")

    # Try to run the file with --version
    version_output = run_command(f"adb shell {remote_path} --version", verbose)

    if version_output:
        return version_output.strip()

    if verbose:
        print("Could not determine frida-server version")
    return None


def run_frida_server(custom_dir=None, custom_params=None, verbose=False, version=None, name=None):
    """Run frida-server on the Android device"""
    check_adb_connection(verbose)

    # Determine the directory to use
    server_dir = custom_dir if custom_dir else DEFAULT_INSTALL_DIR

    # Determine the server path
    server_path = None

    # If name is specified, use that specific name
    if name:
        server_path = f"{server_dir}/{name}"
        # Check if this specific name exists
        output = run_command(f'adb shell ls {server_path}', verbose)
        if not output or 'No such file or directory' in output:
            print(f"Error: frida-server with name {name} not found at {server_path}")
            print("Please install it first")
            sys.exit(1)
    # If version is specified, try to use that specific version
    elif version:
        server_path = f"{server_dir}/frida-server-{version}"
        # Check if this specific version exists
        output = run_command(f'adb shell ls {server_path}', verbose)
        if not output or 'No such file or directory' in output:
            print(f"Error: frida-server version {version} not found at {server_path}")
            print("Please install this version first")
            sys.exit(1)
    elif custom_params and custom_params.startswith('/'):
        # If custom_params starts with '/', treat it as a full path
        server_path = custom_params
    else:
        # Check if frida-server exists in the directory
        output = run_command(f"adb shell ls {server_dir} | grep frida-server", verbose)
        if not output:
            print(f"Error: No frida-server found in {server_dir}")
            print("Please install it first")
            sys.exit(1)

        # Use the first frida-server file found
        files = output.strip().split('\n')
        server_path = f"{server_dir}/{files[0].split()[-1]}"

    # Construct the command to run frida-server
    cmd = f"adb shell su -c 'nohup {server_path}"
    if custom_params and not custom_params.startswith('/'):
        cmd += f" {custom_params}"
    cmd += " < /dev/null > /dev/null 2>&1 &'"

    if verbose:
        print(f"Running frida-server with command: {cmd}")

    # Run frida-server - don't wait for output since it's backgrounded
    print("Starting frida-server...")
    try:
        subprocess.run(cmd, shell=True, check=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"Error starting frida-server: {e}")
        sys.exit(1)

    # Small delay to allow process to start
    import time
    time.sleep(1)

    # Verify it's running
    verify_cmd = "adb shell ps | grep frida-server"
    verify_output = run_command(verify_cmd, verbose)

    if verify_output:
        print("Success: frida-server is running")
        if verbose:
            print(verify_output)
    else:
        print("Warning: Could not verify that frida-server is running")
        print("You may need to start it manually with:\n  adb shell su -c './frida-server'")


def list_frida_server(custom_dir=None, verbose=False):
    """List frida-server files in the specified directory and show their versions"""
    check_adb_connection(verbose)

    # Determine the directory to use
    server_dir = custom_dir if custom_dir else DEFAULT_INSTALL_DIR

    if verbose:
        print(f"Listing frida-server files in {server_dir}")

    # List all files in the directory containing 'frida-server'
    output = run_command(f"adb shell ls {server_dir} | grep frida-server", verbose)

    if not output:
        print(f"No frida-server files found in {server_dir}")
        sys.exit(0)

    # Process the files and get their versions
    files = output.strip().split('\n')
    print(f"Found {len(files)} frida-server file(s) in {server_dir}:")
    print("=" * 80)
    print(f"{'Filename':<40} {'Version':<40}")
    print("=" * 80)

    # Process each file and get its version
    for file in files:
        filename = file.strip()
        remote_path = f"{server_dir}/{filename}"
        version = get_frida_server_version(remote_path, verbose)
        print(f"{filename:<40} {version if version else 'Unknown':<40}")


def get_running_processes(verbose=False, process_name=None):
    """Check and list running processes on the Android device"""
    check_adb_connection(verbose)
    
    # Use custom process name if provided, default to frida-server
    search_name = process_name if process_name else "frida-server"
    
    # Command to list all running processes with more details
    cmd = f"adb shell ps -A | grep {search_name}"
    
    if verbose:
        print(f"Checking for running processes with command: {cmd}")
    
    output = run_command(cmd, verbose)
    
    if not output:
        print(f"No running processes found matching '{search_name}'")
        return []
    
    # Process the output and extract process information
    processes = []
    lines = output.strip().split('\n')
    
    print(f"Running processes matching '{search_name}':")
    print("=" * 80)
    print(f"{'PID':<10} {'User':<15} {'Memory':<10} {'Command':<40}")
    print("=" * 80)
    
    for line in lines:
        parts = line.strip().split()
        if len(parts) < 5:
            continue
        
        # Extract process information
        pid = parts[1]
        user = parts[0]
        memory = parts[4]
        command = ' '.join(parts[7:])
        
        # Store process info for potential use
        processes.append({
            'pid': pid,
            'user': user,
            'memory': memory,
            'command': command
        })
        
        # Print formatted process info
        print(f"{pid:<10} {user:<15} {memory:<10} {command:<40}")
    
    print("=" * 80)
    return processes


def get_running_frida_servers(verbose=False):
    """Check and list running frida-server processes on the Android device (backward compatibility)"""
    return get_running_processes(verbose, "frida-server")


def kill_frida_server(pid=None, verbose=False, name=None):
    """Kill frida-server process on the Android device"""
    check_adb_connection(verbose)
    
    if name:
        # Kill processes by name
        cmd = f"adb shell su -c 'pkill -f {name} || killall -9 {name}'"
        if verbose:
            print(f"Killing processes with name '{name}'")
        
        output = run_command(cmd, verbose)
        
        # Verify no processes with the name are running
        verify_cmd = f"adb shell ps -A | grep {name}"
        verify_output = run_command(verify_cmd, verbose)
        
        if not verify_output:
            print(f"Success: All processes with name '{name}' have been killed")
        else:
            print(f"Warning: Some processes with name '{name}' might still be running")
            if verbose:
                print(verify_output)
    elif pid:
        # Kill specific process by PID
        cmd = f"adb shell su -c 'kill -9 {pid}'"
        if verbose:
            print(f"Killing frida-server process with PID {pid}")
        
        output = run_command(cmd, verbose)
        
        # Verify the process is killed
        verify_cmd = f"adb shell ps -p {pid}"
        verify_output = run_command(verify_cmd, verbose)
        
        if not verify_output or "No such process" in verify_output:
            print(f"Success: frida-server process with PID {pid} has been killed")
        else:
            print(f"Error: Failed to kill frida-server process with PID {pid}")
    else:
        # Kill all frida-server processes
        cmd = "adb shell su -c 'pkill -f frida-server || killall -9 frida-server'"
        if verbose:
            print("Killing all running frida-server processes")
        
        output = run_command(cmd, verbose)
        
        # Verify no frida-server processes are running
        verify_cmd = "adb shell ps -A | grep frida-server"
        verify_output = run_command(verify_cmd, verbose)
        
        if not verify_output:
            print("Success: All frida-server processes have been killed")
        else:
            print("Warning: Some frida-server processes might still be running")
            if verbose:
                print(verify_output)
