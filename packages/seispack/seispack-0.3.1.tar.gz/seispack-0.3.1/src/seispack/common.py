"""! This module contains common specifications
"""

# blue-ish colors to plot observations
color_obs=[ 'xkcd:blue', 'xkcd:lightblue', 'xkcd:lightgreen', 'xkcd:turquoise', 'xkcd:teal']

# red-ish colors to plot models
color_mod=[ 'xkcd:red', 'xkcd:magenta', 'xkcd:orange', 'xkcd:salmon', 'xkcd:purple']


def color_tables(c_obs=None, c_mod=None):
    """!This routine provide two lists of colors
    @param c_obs None|list|str: list of valid colors to replace the default one
    @param c_mod None|list|str: list of valid colors to replace the default one
    @return tuple(list,list): return two lists of colors
    """
    if c_obs is not None:
        c_obs = list(c_obs)
    else:
        c_obs=color_obs

    if c_mod is not None:
        c_mod = list(c_mod)
    else:
        c_mod=color_mod

    return c_obs, c_mod