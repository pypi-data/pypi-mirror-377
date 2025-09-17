
import argparse
import logging
from . import app, DOWNLOAD_FOLDER, CONFIG_DIR, load_config

def main():
    """The main entry point for the command line interface."""
    config = load_config()
    default_host = '0.0.0.0' if config.get('ALLOW_LAN_ACCESS') else '127.0.0.1'

    parser = argparse.ArgumentParser(
        description="Run the TubeZ web server, a self-hosted media grabber.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""Examples:
  tubez                             # Start the server with default settings
  tubez --port 5000                 # Start on a different port
  tubez --host 0.0.0.0              # Override config and allow LAN access
  tubez --debug                     # Start in debug mode for development"""
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
    args = parser.parse_args()

    # --- THIS IS THE FIX ---
    # Store BOTH the host and port in the app's runtime config
    app.config['SERVER_PORT'] = args.port
    app.config['SERVER_HOST'] = args.host  # <-- ADD THIS LINE

    print("🚀 TubeZ Server starting...")
    print(f"📂 Downloads will be saved in: {DOWNLOAD_FOLDER}")
    print(f"📂 History & Config is in: {CONFIG_DIR}")
    print(f"🌐 Server is running on: http://{args.host}:{args.port}")
    if args.host == '127.0.0.1':
        print("   (Access is limited to this machine. Use --host 0.0.0.0 to allow network access)")
    print("Press CTRL+C to quit.")

    if args.debug:
        print("⚠️  Running in DEBUG mode. Auto-reloader is active.")
        app.run(host=args.host, port=args.port, threaded=True, debug=True)
    else:
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        try:
            from waitress import serve
            serve(app, host=args.host, port=args.port, threads=8)
        except ImportError:
            print("\n[WARNING] 'waitress' is not installed. Falling back to the Flask development server.")
            print("For a better experience, please run: pip install waitress\n")
            app.run(host=args.host, port=args.port, threaded=True, debug=False)

if __name__ == '__main__':
    main()
