
import os
import sys

import api
import api.app
import api.config
from api.config import DEFAULT_CONFIG_PATH, common_setup

def main():
    app = create_app()
    port = int(os.getenv('ARK_FLASK_PORT', 5000))
    debug = os.getenv('ARK_FLASK_DEBUG', "false").lower() == "true"
    app.run(host='0.0.0.0', port=port, debug=debug)


def create_app():
    common_setup()
    config = api.config.get_config()
    app = api.app.build_app(config)
    return app


if __name__ == '__main__':
    main()
