import webbrowser
import pystray
from PIL import Image
import logging
logger = logging.getLogger(__name__)

image = Image.open("./images/caret-right-square-fill.png", "r")


def after_click(icon, query):
    if str(query) == "openrecall Search":
        success = webbrowser.open(
            'http://localhost:8082/', new=2, autoraise=True)
        logger.warning("Success:", success)
        if success:
            logger.warning(f"Successfully opened {url} in a new browser tab.")
        else:
            logger.warning(f"Failed to open {url}.")

    elif str(query) == "openrecall homepage":
        webbrowser.open(
            'https://github.com/openrecall/openrecall', new=2, autoraise=True)
        # icon.stop()
    elif str(query) == "Exit":
        icon.stop()


def create_system_tray_icon():
    icon = pystray.Icon("GFG", image, "openrecall is recording....",
                        menu=pystray.Menu(
                            pystray.MenuItem("openrecall Search",
                                             after_click),
                            pystray.MenuItem("openrecall homepage",
                                             after_click), pystray.MenuItem("Exit", after_click)
                        ))

    return icon
