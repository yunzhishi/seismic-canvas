# Copyright (C) 2019 Yunzhi Shi @ The University of Texas at Austin.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np
from vispy import scene
from vispy.visuals import TextVisual


class Colorbar(scene.visuals.ColorBar):
  """ A colorbar visual that add some interactivity fixes to be used
  in 3D. It rotates correctly, and can be dragged around.

  Parameters:

  """
  def __init__(self, size=(500, 10), cmap='grays', clim=None,
               label_str="Colorbar", label_color='black',
               label_size=12, tick_size=10,
               border_width=1.0, border_color='black',
               visible=True, parent=None):
    # Create a scene.visuals.ColorBar (without parent by default).
    assert clim is not None, "clim must be provided."
    scene.visuals.ColorBar.__init__(self, parent=parent,
      pos=(0, 0), size=size, orientation='right',
      label_str=label_str, label_color=label_color,
      cmap=cmap, clim=clim,
      border_width=border_width, border_color=border_color)
    self.unfreeze()
    self.visible = visible
    self.canvas_size = None # will be set when parent is linked

    # Resize the label and ticks.
    self.label.font_size = label_size
    for tick in self.ticks:
      tick.font_size = tick_size

    # TODO: add more than 2 ticks. This requires very in-depth modification.
    # I plan to replace vispy colobar with a matplotlib rendered version.

    self.freeze()

  def on_resize(self, event):
    # When window is resized, only need to move the position in vertical
    # direction, because the coordinate is relative to the secondary ViewBox
    # that stays on the right side of the canvas.
    pos = np.array(self.pos).astype(np.single)
    pos[1] *= event.size[1] / self.canvas_size[1]
    self.pos = tuple(pos)
    # Update the canvas size.
    self.canvas_size = event.size
