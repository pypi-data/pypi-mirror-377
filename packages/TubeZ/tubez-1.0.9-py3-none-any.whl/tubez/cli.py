# src/tubez/cli.py

import argparse
import logging
import os
import time
import webbrowser
import subprocess
from colorama import Fore, Style, init

from . import app, __version__, DOWNLOAD_FOLDER, CONFIG_DIR, load_config

def main():
    """The main entry point for the command line interface."""
    init(autoreset=True)

    config = load_config()
    default_host = '0.0.0.0' if config.get('ALLOW_LAN_ACCESS') else '127.0.0.1'

    parser = argparse.ArgumentParser(
        description="Run the TubeZ web server, a self-hosted media grabber.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""Examples:
  tubez                             # Start the server with default settings
  tubez --open                      # Start the server and open the browser
  tubez --port 5000                 # Start on a different port
  tubez --host 0.0.0.0              # Override config and allow LAN access
  tubez --debug                     # Start in debug mode for development
  tubez --version                   # Show the current version and exit"""
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s v{__version__}'
    )
    parser.add_argument(
        '--host',
        type=str,
        default=default_host,
        help=f"The host to bind the server to. Defaults to '{default_host}' based on your config."
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8089,
        help="The port to run the server on. Defaults to 8089."
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help="""Enable debug mode."""
    )
    parser.add_argument(
        '--open',
        action='store_true',
        help="Automatically open the web dashboard in your browser on startup."
    )
    args = parser.parse_args()

    app.config['SERVER_PORT'] = args.port
    app.config['SERVER_HOST'] = args.host
    
    is_main_process = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
    if not args.debug or is_main_process:
        print(f"{Style.BRIGHT}{Fore.MAGENTA}🚀 TubeZ Server starting...{Style.RESET_ALL}")
        print(f"{Fore.WHITE}📂 Downloads will be saved in: {Fore.LIGHTYELLOW_EX}{DOWNLOAD_FOLDER}")
        print(f"{Fore.WHITE}📂 History & Config is in: {Fore.LIGHTYELLOW_EX}{CONFIG_DIR}")
        
        # --- THIS IS THE REFINEMENT ---
        # Determine the correct URL for browser access and display it.
        # If listening on all interfaces, the browser should connect to localhost.
        display_host = '127.0.0.1' if args.host == '0.0.0.0' else args.host
        browser_url = f"http://{display_host}:{args.port}"
        
        print(f"{Fore.WHITE}🌐 Server is running on: {Fore.CYAN}{browser_url}")
        
        if args.host == '127.0.0.1':
            print(f"{Fore.YELLOW}   (Access is limited to this machine. Use --host 0.0.0.0 to allow network access)")
        
        print(f"{Fore.LIGHTBLACK_EX}Press CTRL+C to quit.")
        
        if args.open:
            for i in range(3, 0, -1):
                print(f"{Fore.GREEN}Opening browser in {i} seconds... \r", end="")
                time.sleep(1)
            print(" " * 40, end="\r")

            try:
                if 'TERMUX_VERSION' in os.environ:
                    print(f"{Fore.CYAN}Termux detected. Using 'termux-open-url'...")
                    # Use the corrected browser_url
                    subprocess.run(['termux-open-url', browser_url], check=True)
                else:
                    # Use the corrected browser_url
                    webbrowser.open(browser_url)
            except FileNotFoundError:
                print(f"{Fore.RED}Error: 'termux-open-url' command not found. Please run 'pkg install termux-api'.")
            except Exception as e:
                print(f"{Fore.RED}Could not open browser: {e}")

    if args.debug:
        print(f"{Style.BRIGHT}{Fore.YELLOW}⚠️  Running in DEBUG mode. Auto-reloader is active.")
        app.run(host=args.host, port=args.port, threaded=True, debug=True)
    else:
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        try:
            from waitress import serve
            serve(app, host=args.host, port=args.port, threads=8)
        except ImportError:
            print(f"\n{Fore.RED}[WARNING] 'waitress' is not installed. Falling back to the Flask development server.")
            print(f"{Fore.YELLOW}For a better experience, please run: pip install waitress\n")
            app.run(host=args.host, port=args.port, threaded=True, debug=False)

if __name__ == '__main__':
    main()
