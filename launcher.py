#!/usr/bin/env python
import os
import sys
import time
import webbrowser

from pathlib import Path
import api.config
from main import create_app

"""
Simple Ark Launcher - No complex process management

This launcher simply starts the Flask server directly without trying to
manage it as a subprocess. This avoids all the circular detection issues.
"""


# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


def main():  # noqa: C901
    """Simple launcher that starts the server directly"""
    print("=" * 60)
    print("ARK PORTABLE")
    print("=" * 60)
    print()

    model_name = "mirai"

    if len(sys.argv) > 1:
        model_arg = sys.argv[1].lower()
        if model_arg in ["empty", "mirai", "sybil"]:
            model_name = model_arg

    print(f"🔧 Initializing with model: {model_name}")

    try:
        api.config.set_config_by_name(model_name)
        print("✅ Configuration loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return

    port = 5000
    os.environ["ARK_FLASK_PORT"] = str(port)
    os.environ["ARK_FLASK_DEBUG"] = "false"

    print("📡 Starting web server...")
    print()

    try:
        app = create_app()

        print("=" * 60)
        print("✅ ARK SERVER IS STARTING")
        print("=" * 60)
        print(f"🌐 Web Interface: http://localhost:{port}")
        print(
            "🛑 To stop: Press Ctrl+C or use the shutdown button in the web interface"
        )
        print("=" * 60)
        print()

        def open_browser():
            time.sleep(2)
            try:
                webbrowser.open(f"http://localhost:{port}")
                print("🌐 Browser opened automatically")
            except Exception as e:
                print(f"⚠️ Could not open browser automatically: {e}")
                print(f"Please manually navigate to http://localhost:{port}")

        import threading

        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()

        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

    except KeyboardInterrupt:
        print("\n⚠️ Server stopped by user (Ctrl+C)")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use!")
            print("Please stop any other applications using this port and try again.")
        else:
            print(f"❌ Server error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
