# === set default plotting style ===

__CFPACK_STYLE_CTX = None  # holds the rc_context manager
__CFPACK_STYLE_EXIT = None  # holds the exit function

# load cfpack matplotlib style, saving current rcParams so they can be restored later
def load_style(*extra):
    import os
    from matplotlib import rc_context as mpl_rc_context
    from importlib.resources import files
    from matplotlib.style import use as mpl_style_use
    global __CFPACK_STYLE_CTX, __CFPACK_STYLE_EXIT
    if __CFPACK_STYLE_CTX is not None:
        return  # already loaded
    __CFPACK_STYLE_CTX = mpl_rc_context() # snapshot current rcParams
    __CFPACK_STYLE_EXIT = __CFPACK_STYLE_CTX.__enter__() # enter the context manually
    # apply cfpack style
    style_files = ["cfpack.mplstyle", files("cfpack").joinpath("cfpack.mplstyle")]
    for style_file in style_files:
        if os.path.exists(style_file):
            mpl_style_use([str(style_file), *extra])
            continue

# restore rcParams that were active before load_style()
def unload_style():
    global __CFPACK_STYLE_CTX, __CFPACK_STYLE_EXIT
    if __CFPACK_STYLE_CTX is None:
        return  # nothing to restore
    __CFPACK_STYLE_CTX.__exit__(None, None, None)  # restore snapshot
    __CFPACK_STYLE_CTX, __CFPACK_STYLE_EXIT = None, None

# load_style()

from matplotlib import rcParams

# latex
rcParams['text.usetex'] = True
rcParams['text.latex.preamble'] = r'\usepackage{bm}'
# basics
rcParams['lines.linewidth'] = 1.2
rcParams['lines.markersize'] = 2
rcParams['lines.markeredgewidth'] = 0.5
rcParams['font.family'] = 'Arial'
rcParams['font.size'] = 12
rcParams['axes.linewidth'] = 0.8
# x-ticks
rcParams['xtick.top'] = True
rcParams['xtick.direction'] = 'in'
rcParams['xtick.minor.visible'] = True
rcParams['xtick.major.size'] = 6
rcParams['xtick.minor.size'] = 3
rcParams['xtick.major.width'] = 0.75
rcParams['xtick.minor.width'] = 0.75
rcParams['xtick.major.pad'] = 5
rcParams['xtick.minor.pad'] = 5
# y-ticks
rcParams['ytick.right'] = True
rcParams['ytick.direction'] = 'in'
rcParams['ytick.minor.visible'] = True
rcParams['ytick.major.size'] = 6
rcParams['ytick.minor.size'] = 3
rcParams['ytick.major.width'] = 0.75
rcParams['ytick.minor.width'] = 0.75
rcParams['ytick.major.pad'] = 5
rcParams['ytick.minor.pad'] = 5
# legend
rcParams['legend.fontsize'] = rcParams['font.size']
rcParams['legend.labelspacing'] = 0.2
rcParams['legend.loc'] = 'upper left'
rcParams['legend.frameon'] = False
# figure
rcParams['figure.figsize'] = (5.5, 3.5)
rcParams['figure.dpi'] = 150
rcParams['savefig.dpi'] = 200
rcParams['savefig.bbox'] = 'tight'
# errorbars
rcParams['errorbar.capsize'] = 1.5
