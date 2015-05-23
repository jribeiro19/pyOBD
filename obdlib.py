
#-----------------------  OBD Libraries v1.0  --------------------------#
#																		#
# Author: Júlio Ribeiro	- ISCTE/IUL - Engineering Master Degrees        #
# Date: 23/05/2015, Lisbon												#
# License: GPL															#
# Description: This module intent to implement a bunch of functions to  # 
#              manipulate PIDs requets via "OBD-II ELM327"              #
#             #
#																		#
#-----------------------------------------------------------------------#
 

from bluetooth import *
import os
import sys
import time
import variables
import bluetooth
import ConfigParser
