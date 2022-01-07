import matplotlib.patheffects as path_effects
import cartopy.crs as ccrs
from cartopy.util import add_cyclic_point

import numpy as np
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import matplotlib.pyplot as plt


class CartopyMapPlotter:
    def __init__(self, cartopymap):
        self._bgmap = cartopymap

    def lines(self, latlons, color, shadow=False, **kwargs):
        if not latlons.any():
            return
        else:
            use_kw = kwargs
            ispoint = latlons.shape[0] == 1

            if ispoint:
                # a line plot will cause a singular point to vanish, so we force it to
                # plot points here
                use_kw = use_kw.copy()
                use_kw.pop('linestyle', None)
                size = use_kw.pop('linewidth', 2)
                use_kw['marker'] = 'o'
                use_kw['markersize'] = size
                use_kw['markeredgewidth'] = 0.0

            if shadow:
                shadow_kw = dict(offset=(0.5, -0.5), alpha=0.6)
                if ispoint:
                    shadow_effect = path_effects.SimplePatchShadow(**shadow_kw)
                else:
                    shadow_effect = path_effects.SimpleLineShadow(**shadow_kw)

                use_kw['path_effects'] = [shadow_effect, path_effects.Normal()]

            self._bgmap.ax.plot(latlons[:, 1], latlons[:, 0],
                                color=color, transform=ccrs.PlateCarree(), **use_kw)

    def points(self, latlons, color='k', marker='o', markersize=2, shadow=False, **kwargs):
        lons = latlons[:, 1]
        lats = latlons[:, 0]

        kw = kwargs.copy()
        if shadow:
            # TODO: fix breaking shadow effects
            shadow_kw = dict(offset=(0.5, -0.5), alpha=0.6)
            shadow_effect = path_effects.SimplePatchShadow(**shadow_kw)
            kw['path_effects'] = [shadow_effect, path_effects.Normal()]

        self._bgmap.ax.scatter(lons, lats, marker=marker, s=markersize,
                               transform=ccrs.PlateCarree(), facecolor=color, **kw)

    def fill(self, da, cmap=None, levels=None, colorbar=False, colorbar_label=None):
        lons = da.lon
        lats = da.lat
        data = da.values
        data, lons = add_cyclic_point(data, coord=lons)

        lons, lats = np.meshgrid(lons, lats)
        data = np.reshape(data, lons.shape)

        CS = self._bgmap.ax.contourf(lons, lats, data,
                                     transform=ccrs.PlateCarree(), cmap=cmap,
                                     levels=levels, extend='both')

        if colorbar:
            cb_inset = inset_axes(self._bgmap.ax, width='50%', height='5%', loc='upper right')
            plt.colorbar(CS, cax=cb_inset, orientation='horizontal', label=colorbar_label)

        return CS


class CartopyMapTextBox:
    def __init__(self, cartopymap):
        self._bgmap = cartopymap

    def bottom_right(self, text, fontsize=16):
        ax = self._bgmap.ax
        plt.text(0.99, 0.01, text, transform=ax.transAxes, fontsize=fontsize,
                 verticalalignment='bottom', horizontalalignment='right',
                 bbox=dict(alpha=0.75, facecolor='white', edgecolor='gray'))

    def top_right(self, text, fontsize=16):
        ax = self._bgmap.ax
        plt.text(0.99, 0.99, text, transform=ax.transAxes, fontsize=fontsize,
                 verticalalignment='top', horizontalalignment='right',
                 bbox=dict(alpha=0.75, facecolor='white', edgecolor='gray'))

    def top_left(self, text, fontsize=16):
        ax = self._bgmap.ax
        plt.text(0.01, 0.99, text, transform=ax.transAxes, fontsize=fontsize,
                 verticalalignment='top', horizontalalignment='left',
                 bbox=dict(alpha=0.75, facecolor='white', edgecolor='gray'))

    def bottom_left(self, text, fontsize=16):
        ax = self._bgmap.ax
        plt.text(0.01, 0.01, text, transform=ax.transAxes, fontsize=fontsize,
                 verticalalignment='bottom', horizontalalignment='left',
                 bbox=dict(alpha=0.75, facecolor='white', edgecolor='gray'))