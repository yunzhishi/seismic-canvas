# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (C) 2019 Yunzhi Shi @ The University of Texas at Austin.
# All rights reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import io
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
plt.style.use('seaborn-notebook')
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
from vispy import scene
from vispy.color import get_colormap
from vispy.util.dpi import get_dpi
from vispy.visuals.transforms import MatrixTransform


class Colorbar(scene.visuals.Image):
  """ A colorbar visual fixed to the right side of the canvas. This is
  based on the rendering from Matplotlib, then display this rendered
  image as a scene.visuals.Image visual node on the canvas.

  Parameters:

  """
  def __init__(self, size=(500, 10), cmap='grays', clim=None,
               label_str="Colorbar", label_color='black',
               label_size=12, tick_size=10,
               border_width=1.0, border_color='black',
               visible=True, parent=None):

    assert clim is not None, 'clim must be specified explicitly.'

    # Create a scene.visuals.Image (without parent by default).
    scene.visuals.Image.__init__(self, parent=None,
      interpolation='nearest', method='auto')
    self.unfreeze()
    self.visible = visible
    self.canvas_size = None # will be set when parent is linked

    # Record the important drawing parameters.
    self.pos = (0, 0)
    self.bar_size = size # tuple
    self.cmap = get_colormap(cmap) # vispy Colormap
    self.clim = clim # tuple

    # Record the styling parameters.
    self.label_str = label_str
    self.label_color = label_color
    self.label_size = label_size
    self.tick_size = tick_size
    self.border_width = border_width
    self.border_color = border_color

    # Draw colorbar using Matplotlib.
    self.set_data(self._draw_colorbar())

    # Give a Matrix transform to self in order to move around canvas.
    self.transform = MatrixTransform()

    self.freeze()

  def on_resize(self, event):
    """ When window is resized, only need to move the position in vertical
    direction, because the coordinate is relative to the secondary ViewBox
    that stays on the right side of the canvas.
    """
    pos = np.array(self.pos).astype(np.single)
    pos[1] *= event.size[1] / self.canvas_size[1]
    self.pos = tuple(pos)

    # Move the colorbar to specified position (with half-size padding, because
    # Image visual uses a different anchor (top-left corner) rather than the
    # center-left corner used by ColorBar visual.).
    self.transform.reset()
    self.transform.translate((self.pos[0]/2.618, # make the gap smaller :)
                              self.pos[1] - self.size[1]/2.))

    # Update the canvas size.
    self.canvas_size = event.size

  def _draw_colorbar(self):
    """ Draw a Matplotlib colorbar, save this figure without any boundary to a
    rendering buffer, and return this buffer as a numpy array.
    """
    dpi = get_dpi()
    # Compute the Matplotlib figsize: note the order of width, height.
    # The width is doubled because we will only keep the colorbar portion
    # before we export this image to buffer!
    figsize = (self.bar_size[1]/dpi * 2, self.bar_size[0]/dpi)

    # Convert cmap and clim to Matplotlib format.
    rgba = self.cmap.colors.rgba
    # Blend to white to avoid this Matplotlib rendering issue:
    # https://github.com/matplotlib/matplotlib/issues/1188
    for i in range(3):
      rgba[:, i] = (1 - rgba[:, -1]) + rgba[:, -1]*rgba[:, i]
    rgba[:, -1] = 1.
    if len(rgba) < 2: # in special case of 'grays' cmap!
      rgba = np.array([[0,0,0, 1.], [1,1,1, 1.]])
    cmap = LinearSegmentedColormap.from_list('vispy_cmap', rgba)
    norm = mpl.colors.Normalize(vmin=self.clim[0], vmax=self.clim[1])
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)

    # Put the colorbar at proper location on the Matplotlib fig.
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = plt.Axes(fig, [0, 0, 1, 1])
    ax.set_axis_off()
    fig.add_axes(ax)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='100%', pad=0.)
    cb = fig.colorbar(sm, cax=cax)
    ax.remove()

    # Apply styling to the colorbar.
    cb.set_label(self.label_str,
      color=self.label_color, fontsize=self.label_size)
    plt.setp(plt.getp(cb.ax.axes, 'yticklabels'),
      color=self.label_color, fontsize=self.tick_size)
    cb.ax.yaxis.set_tick_params(color=self.label_color)
    cb.outline.set_linewidth(self.border_width)
    cb.outline.set_edgecolor(self.border_color)

    # Export the rendering to a numpy array in the buffer.
    buf = io.BytesIO()
    fig.savefig(buf, format='png',
      bbox_inches='tight', pad_inches=0, dpi=dpi, transparent=True)
    buf.seek(0)

    return plt.imread(buf)
