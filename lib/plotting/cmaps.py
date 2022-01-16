import functools
from collections import namedtuple

from matplotlib import colors

import config


def load_cmap(name, filename):
    palfile = config.get_cmap(filename)
    rawcolors = colorbar_from_pal(palfile)
    return colorbar_to_cmap_and_norm(name, rawcolors)

#################################################
#    Converting .pal to dictionary of colors    #
#################################################


def colorbar_from_pal(palfile):
    colorbar = {}
    with open(palfile, encoding='utf-8') as paldata:
        for line in paldata:
            if line and line[0] != ';':
                bndy, clrs = _parse_pal_line(line)
                if bndy is not None:
                    colorbar[float(bndy)] = clrs
    return colorbar


def _parse_pal_line(line):
    tokens = line.split()
    header = tokens[0] if tokens else None

    if header is not None and 'color' in header.lower():
        cdata = tokens[1:]
        isrgba = 'color4' in header.lower()
        if not cdata:
            return None, None
        bndy = cdata[0]
        rgba_vals = cdata[1:]
        clrs = [_getcolor(rgba_vals, isrgba)]

        if len(rgba_vals) > 4:
            index = 4 if isrgba else 3
            rgba_vals = rgba_vals[index:]
            clrs.append(_getcolor(rgba_vals, isrgba))

        return bndy, clrs

    return None, None


def _getcolor(rgba_vals, has_alpha):
    if has_alpha:
        alpha = float(rgba_vals[3]) / MAX_RGB_VALUE
        return rgba(r=int(rgba_vals[0]), g=int(rgba_vals[1]), b=int(rgba_vals[2]), a=alpha)
    else:
        return rgb(r=int(rgba_vals[0]), g=int(rgba_vals[1]), b=int(rgba_vals[2]))


###################################################
# Converting dict to cmap and norm for matplotlib #
###################################################


def colorbar_to_cmap_and_norm(name, colors_dict):
    cmap_dict = _rawdict2cmapdict(colors_dict)
    norm = colors.Normalize(min(colors_dict), max(colors_dict), clip=False)
    return colors.LinearSegmentedColormap(name, cmap_dict), norm


def _rawdict2cmapdict(colors_dict):
    cmap_dict = {
        'red': [],
        'green': [],
        'blue': [],
        'alpha': []
    }
    max_bound = max(colors_dict)
    min_bound = min(colors_dict)

    if max_bound == min_bound:
        raise ValueError("Color map requires more than one color")

    bounds_in_order = sorted(colors_dict.keys())

    for i, bound in enumerate(bounds_in_order):
        if i == len(bounds_in_order) - 1:
            # last element, avoid having extra entries in the colortable map
            pass
        else:
            lobound = bounds_in_order[i]
            hibound = bounds_in_order[i+1]
            locolors = colors_dict[lobound]
            hicolors = colors_dict[hibound]
            if not locolors or not hicolors:
                raise ValueError("Invalid colormap file, empty colors.")
            if len(locolors) < 2:
                locolors.append(hicolors[0])

            lobound_frac = relative_percentage(lobound, min_bound, max_bound)
            hibound_frac = relative_percentage(hibound, min_bound, max_bound)
            locolor1 = to_fractional(to_rgba(locolors[0]))
            locolor2 = to_fractional(to_rgba(locolors[1]))
            hicolor1 = to_fractional(to_rgba(hicolors[0]))

            def _append_colors(color):
                attr = color[0]
                # the first element
                if i == 0:
                    cmap_dict[color].append((lobound_frac, getattr(locolor1, attr), getattr(locolor1, attr)))
                    cmap_dict[color].append((hibound_frac, getattr(locolor2, attr), getattr(hicolor1, attr)))
                else:
                    cmap_dict[color].append((hibound_frac, getattr(locolor2, attr), getattr(hicolor1, attr)))

            _append_colors('red')
            _append_colors('green')
            _append_colors('blue')
            _append_colors('alpha')

    for k in cmap_dict:
        cmap_dict[k] = sorted(cmap_dict[k], key=lambda tup: tup[0])
    return cmap_dict


### UTILITIES ###


rgb = namedtuple('rgb', 'r g b')
rgba = namedtuple('rgba', 'r g b a')


MIN_RGB_VALUE = 0
MAX_RGB_VALUE = 255


def to_rgba(rgb_tup):
    if isinstance(rgb_tup, rgba):
        return rgb_tup
    return rgba(rgb_tup.r, rgb_tup.g, rgb_tup.b, 1.0)


def to_fractional(rgb_tup):
    if isinstance(rgb_tup, rgb):
        return rgb(_rgb_frac(rgb_tup.r), _rgb_frac(rgb_tup.g), _rgb_frac(rgb_tup.b))
    else:
        return rgba(_rgb_frac(rgb_tup.r), _rgb_frac(rgb_tup.g), _rgb_frac(rgb_tup.b), rgb_tup.a)

def relative_percentage(val, minval, maxval):
    return (val - minval) / (maxval - minval)


_rgb_frac = functools.partial(relative_percentage, minval=MIN_RGB_VALUE, maxval=MAX_RGB_VALUE)



