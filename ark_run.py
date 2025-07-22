#!/usr/bin/env python

# import os
# import platform
# import subprocess
# import sys
# import api.config
# from api.config import PROJECT_DIR

# def _check_help():
#     if len(sys.argv) > 1 and sys.argv[1] in {"help", "--help", "-h"}:
#         return True
#     return False


def cli_entrypoint(model_name="auto"):
    api.config.set_config_by_name("mirai")

    LOGLEVEL_KEY = "LOG_LEVEL"
    loglevel = os.environ.get(LOGLEVEL_KEY, "INFO")
    threads = os.environ.get("ARK_THREADS", "4")
    if platform.system() == "Windows":
        args = ["waitress-serve",
                "--channel-timeout", "3600",
                "--threads", threads,
                "--port", "5000",
                "--call", "main:create_app"]

    else:
        args = ["gunicorn",
                "--bind", "0.0.0.0:8081",
                "--timeout", "0",
                "--threads", threads,
                "--log-level", loglevel,
                "--access-logfile", "-",
                "main:create_app()"]

    proc = subprocess.run(args, stdout=None, stderr=None, text=True, cwd=PROJECT_DIR)




    

if __name__ == '__main__':
    import os
    import platform
    import subprocess
    import sys

    import api.config
    from api.config import PROJECT_DIR, set_config_by_name

    cli_entrypoint("mirai")
