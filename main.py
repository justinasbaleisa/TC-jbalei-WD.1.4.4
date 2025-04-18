import logging
import sys
import traceback

from ui.app_manager import AppManager


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
