"""
Setup method for mock azcamserver.
Usage example:
  python -i -m azcam_mock.server
"""

import os
import sys

import azcam
import azcam.utils
import azcam.server
import azcam.shortcuts
from azcam.cmdserver import CommandServer
from azcam.header import System
from azcam.tools.instrument import Instrument
from azcam.tools.ds9display import Ds9Display
from azcam.tools.telescope import Telescope
from azcam.tools.controller import Controller
from azcam.tools.exposure import Exposure
from azcam.tools.tempcon import TempCon
from azcam.web.fastapi_server import WebServer


def setup():

    # parse command line arguments
    try:
        i = sys.argv.index("-datafolder")
        datafolder = sys.argv[i + 1]
    except ValueError:
        datafolder = None

    # define folders for system
    azcam.db.systemname = "mock"
    azcam.db.servermode = azcam.db.systemname

    azcam.db.systemfolder = os.path.dirname(__file__)
    azcam.db.systemfolder = azcam.utils.fix_path(azcam.db.systemfolder)
    # azcam.db.datafolder = azcam.utils.get_datafolder(datafolder)
    azcam.db.datafolder = os.path.join(
        azcam.db.systemfolder, "datafolder"
    )  # special case for mock

    parfile = os.path.join(
        azcam.db.datafolder,
        "parameters",
        f"parameters_server_{azcam.db.systemname}.ini",
    )

    # enable logging
    # logfile = os.path.join(azcam.db.datafolder, "logs", "server.log")
    # azcam.db.logger.start_logging(logfile=logfile)
    azcam.db.logger.start_logging()
    azcam.log(f"Configuring console for {azcam.db.systemname}")

    # controller
    controller = Controller()

    # temperature controller
    tempcon = TempCon()
    tempcon.control_temperature = -100.0

    # exposure
    exposure = Exposure()
    filetype = "MEF"
    exposure.filetype = exposure.filetypes[filetype]
    exposure.image.filetype = exposure.filetypes[filetype]
    exposure.display_image = 0

    # detector
    detector_mock = {
        "name": "mock4k",
        "description": "STA0500 4064x4064 CCD",
        "ref_pixel": [2032, 2032],
        "format": [4064, 7, 0, 20, 4064, 0, 0, 0, 0],
        "focalplane": [1, 1, 1, 2, [2, 0]],
        "roi": [1, 4064, 1, 4064, 2, 2],
        "ext_position": [[1, 2], [1, 1]],
        "jpg_order": [1, 2],
    }
    exposure.set_detpars(detector_mock)
    exposure.image.focalplane.gains = 2 * [1.0]
    exposure.image.focalplane.rdnoises = 2 * [4.0]

    # instrument
    instrument = Instrument()

    # telescope
    telescope = Telescope()

    # system header template
    template = os.path.join(azcam.db.datafolder, "templates", "fits_template_mock.txt")
    system = System("Mock", template)
    system.set_keyword("DEWAR", "mock_dewar", "Dewar name")

    # display
    display = Ds9Display()
    display.initialize()

    # par file
    azcam.db.parameters.read_parfile(parfile)
    azcam.db.parameters.update_pars()

    # define and start command server
    cmdserver = CommandServer()
    cmdserver.port = 2402
    azcam.log(f"Starting cmdserver - listening on port {cmdserver.port}")
    azcam.db.tools["api"].initialize_api()
    cmdserver.start()

    # web server
    webserver = WebServer()
    webserver.port = 2403
    webserver.logcommands = 1
    webserver.logstatus = 0
    webserver.start()

    # azcammonitor
    azcam.db.monitor.register()

    # GUIs
    if 1:
        import azcam_mock.start_azcamtool

    # finish
    azcam.log("Configuration complete")


# start
setup()
from azcam.cli import *
