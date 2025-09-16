import sys
import argparse
from fsm.core import check_adb_connection, install_frida_server, run_frida_server, list_frida_server, get_running_processes, kill_frida_server


def main():
    # 创建一个父解析器来处理全局参数
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    
    # 创建主解析器
    parser = argparse.ArgumentParser(
        description='frida-server manager for Android devices',
        parents=[parent_parser]
    )
    
    # In Python 3.7+, add_subparsers requires setting required=True explicitly
    subparsers = parser.add_subparsers(dest='command', help='Commands', required=True)
    
    # Install command
    install_parser = subparsers.add_parser(
        'install', 
        help='Install frida-server on the device',
        parents=[parent_parser]
    )
    install_parser.add_argument('version', nargs='?', help='Specific version of frida-server to install')
    install_parser.add_argument('-r', '--repo', default='frida/frida', help='Custom GitHub repository (owner/repo format)')
    install_parser.add_argument('-k', '--keep-name', action='store_true', help='Keep the original name when installing, instead of using version-specific name')
    install_parser.add_argument('-n', '--name', help='Custom name for frida-server on the device')
    
    # Run command
    run_parser = subparsers.add_parser(
        'run', 
        help='Run frida-server on the device',
        parents=[parent_parser]
    )
    run_parser.add_argument('-d', '--dir', help='Custom directory to run frida-server from')
    run_parser.add_argument('-p', '--params', help='Additional parameters for frida-server')
    run_parser.add_argument('-V', '--version', help='Specific version of frida-server to run')
    run_parser.add_argument('-n', '--name', help='Custom name of frida-server to run')
    
    # List command
    list_parser = subparsers.add_parser(
        'list',
        help='List frida-server files on the device and show their versions',
        parents=[parent_parser]
    )
    list_parser.add_argument('-d', '--dir', help='Custom directory to list frida-server files from')
    
    # PS command
    ps_parser = subparsers.add_parser(
        'ps',
        help='List running processes on the device (default: frida-server, use -n for custom processes)',
        parents=[parent_parser]
    )
    ps_parser.add_argument('-n', '--name', help='Filter processes by name (e.g., "frida-server", "com.example.app", etc.)')
    
    # Kill command
    kill_parser = subparsers.add_parser(
        'kill',
        help='Kill frida-server process(es) on the device',
        parents=[parent_parser]
    )
    kill_parser.add_argument('-p', '--pid', help='Specific PID of frida-server process to kill')
    kill_parser.add_argument('-n', '--name', help='Process name to kill (e.g., "frida-server", "com.example.app", etc.)')
    
    args = parser.parse_args()
    
    # If no command is provided, check ADB connection
    if not args.command:
        check_adb_connection(args.verbose)
        return
    
    # Handle install command
    if args.command == 'install':
        install_frida_server(args.version, args.verbose, args.repo, args.keep_name, args.name)
        sys.exit(0)
    
    # Handle run command
    elif args.command == 'run':
        run_frida_server(args.dir, args.params, args.verbose, args.version, args.name)
        sys.exit(0)
    
    # Handle list command
    elif args.command == 'list':
        list_frida_server(args.dir, args.verbose)
        sys.exit(0)
    
    # Handle ps command
    elif args.command == 'ps':
        get_running_processes(args.verbose, args.name)
        sys.exit(0)
    
    # Handle kill command
    elif args.command == 'kill':
        kill_frida_server(args.pid, args.verbose, args.name)
        sys.exit(0)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()