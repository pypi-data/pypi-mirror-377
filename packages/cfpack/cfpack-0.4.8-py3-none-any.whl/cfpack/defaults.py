from . import print # overload print function to activate colours and function signatures
from . import stop # simple 'stop()' in any script to drop into python debugger mode
# forward physical constants for quick access to enable interactive calculations (speed_of_light, pc, m_sol, etc.)
from .constants import *
# load default matplotlib styles
from . import load_plot_style
load_plot_style()
