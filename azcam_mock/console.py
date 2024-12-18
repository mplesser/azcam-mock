"""
Setup method for mock console.
Usage example:
  ipython -i -m azcam_mock.console --profile azcamconsole
"""

import os
import sys
import threading

import azcam
import azcam.utils
import azcam_console.console

from azcam_console.tools.console_tools import create_console_tools
import azcam_console.shortcuts
from azcam.tools.ds9display import Ds9Display

from azcam_console.tools.focus import FocusConsole
from azcam_console.server_comm import ServerCommunication
from azcam_console.observe.observe_cli.observe_cli import ObserveCli


def setup():
    try:
        i = sys.argv.index("-datafolder")
        datafolder = sys.argv[i + 1]
    except ValueError:
        datafolder = None

    # files and folders
    azcam.db.systemname = "mock"

    azcam.db.systemfolder = f"{os.path.dirname(__file__)}"
    # azcam.db.datafolder = azcam.utils.get_datafolder(datafolder)
    azcam.db.datafolder = os.path.join(
        azcam.db.systemfolder, "datafolder"
    )  # special case for mock

    parfile = os.path.join(
        azcam.db.datafolder,
        "parameters",
        f"parameters_console_{azcam.db.systemname}.ini",
    )

    # start logging
    # logfile = os.path.join(azcam.db.datafolder, "logs", "console.log")
    # azcam.db.logger.start_logging(logfile=logfile)
    azcam.db.logger.start_logging()
    azcam.log(f"Configuring console for {azcam.db.systemname}")

    # display
    display = Ds9Display()
    dthread = threading.Thread(target=display.initialize, args=[])
    dthread.start()  # thread just for speed

    # console tools
    create_console_tools()

    # observe
    observe = ObserveCli()

    # focus script
    focus = FocusConsole()
    focus.focus_component = "telescope"
    focus.focus_type = "absolute"

    # try to connect to azcamserver
    connected = azcam.db.server.connect(port=2402)
    if connected:
        azcam.log("Connected to azcamserver")
    else:
        azcam.log("Not connected to azcamserver")

    # par file
    azcam.db.parameters.read_parfile(parfile)
    azcam.db.parameters.update_pars()

    # finish
    azcam.log("Configuration complete")


# start
setup()
from azcam_console.cli import *

del setup
