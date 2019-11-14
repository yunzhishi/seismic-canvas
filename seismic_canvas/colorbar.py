# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (C) 2019 Yunzhi Shi @ The University of Texas at Austin.
# All rights reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np
from vispy import scene
from vispy.visuals import TextVisual


class Colorbar(scene.visuals.ColorBar):
  """ A colorbar visual fixed to the right side of the canvas. This is
  based on vispy stock ColorBar visual.

  Parameters:

  """
  def __init__(self, size=(500, 10), cmap='grays', clim=None,
               label_str="Colorbar", label_color='black',
               label_size=12, tick_size=10,
               border_width=1.0, border_color='black',
               visible=True, parent=None):

    assert clim is not None, 'clim must be specified explicitly.'

    # Create a scene.visuals.ColorBar (without parent by default).
    scene.visuals.ColorBar.__init__(self, parent=parent,
      pos=(0, 0), size=size, orientation='right',
      label_str=label_str, label_color=label_color,
      cmap=cmap, clim=clim,
      border_width=border_width, border_color=border_color)
    self.unfreeze()
    self.visible = visible
    self.canvas_size = None # will be set when parent is linked

    # This is just for compatibility.
    self.bar_size = self.size

    # Resize the label and ticks.
    self.label.font_size = label_size
    for tick in self.ticks:
      tick.font_size = tick_size

    # TODO: add more than 2 ticks. This requires very in-depth modification.
    # I plan to replace vispy colobar with a matplotlib rendered version.

    self.freeze()

  def on_resize(self, event):
    """ When window is resized, only need to move the position in vertical
    direction, because the coordinate is relative to the secondary ViewBox
    that stays on the right side of the canvas.
    """
    pos = np.array(self.pos).astype(np.single)
    pos[1] *= event.size[1] / self.canvas_size[1]
    self.pos = tuple(pos)
    # Update the canvas size.
    self.canvas_size = event.size
