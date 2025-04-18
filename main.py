import logging
import sys

from dotenv import load_dotenv
from ui.app_manager import AppManager

load_dotenv("secrets.env")


def main():
    try:
        logging.basicConfig(
            filename="debug.log",
            filemode="w",  # Or 'a'
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=logging.DEBUG,
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        logging.getLogger("urwid").setLevel(logging.INFO)
        logging.getLogger("openai").setLevel(logging.INFO)
        logging.getLogger("httpcore").setLevel(logging.NOTSET)
        logging.getLogger("httpx").setLevel(logging.INFO)
        logging.info("Application starting...")

        app = AppManager()
        app.start()

    except Exception as e:
        logging.exception(
            "An unhandled exception occurred, application will terminate."
        )
        print(
            f"\nA critical error occurred. Please check the 'debug.log' file for details.",
            file=sys.stderr,
        )
        sys.exit(1)

    finally:
        logging.info("Application finished.")


if __name__ == "__main__":
    main()
