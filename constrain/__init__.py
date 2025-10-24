import logging

# Configure global logging level to INFO
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Set the root logger level to INFO to ensure all loggers inherit this level
logging.getLogger().setLevel(logging.INFO)

from constrain.ashrae import *
from constrain.checklib import *
from constrain.datapoint import *
from constrain.datetimeep import *
from constrain.epinjector import *
from constrain.epreader import *
from constrain.eprunner import *
from constrain.examples import *
from constrain.item import *
from constrain.libcases import *
from constrain.api import *
