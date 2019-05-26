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
  def __init__(self, loc=(720, 380), size=(500, 10), orientation='right',
               label_str="Colorbar", label_color='black',
               cmap='grays', clim=None,
               border_width=1.0, border_color='black',
               visible=True, parent=None):
    # Create a scene.visuals.ColorBar (without parent by default).
    assert clim is not None, "clim must be provided."
    scene.visuals.ColorBar.__init__(self, parent=parent,
      pos=loc, size=size, orientation=orientation,
      label_str=label_str, label_color=label_color,
      cmap=cmap, clim=clim,
      border_width=border_width, border_color=border_color)
    self.interactive = True
    self.unfreeze()
    self.visible = visible
    self.canvas_size = None # will be set when parent is linked

    # TODO: add more than 2 ticks. This requires very in-depth modification.

    # The selection highlight (a Rectangle visual with transparent color).
    # The rectangle is centered on the colorbar.
    if orientation in ["top", "bottom"]:
        (width, height) = size
    elif orientation in ["left", "right"]:
        (height, width) = size
    self.highlight = scene.visuals.Rectangle(parent=parent,
      center=self.pos, height=height+10, width=width+10,
      color=(1, 1, 0, 0.5)) # transparent yellow color
    self.highlight.set_gl_state('opaque', depth_test=True)
    self.highlight.visible = False # only show when selected

    # Set the anchor point (2D screen coordinates). The mouse will
    # drag the axis by anchor point to move around the screen.
    self.anchor = None # None by default
    self.offset = (0, 0)

    self.freeze()

  def on_resize(self, event):
    # When window is resized, move the node accordingly.
    loc = np.array(self.pos).astype(np.single)
    loc *= (np.array(event.size).astype(np.single)
            / np.array(self.canvas_size).astype(np.single))
    self.pos = tuple(loc)
    # Update the canvas size.
    self.canvas_size = event.size

  def set_anchor(self, mouse_press_event):
    """ Set an anchor point (2D screen coordinates) when left click
    in the selection mode (<Ctrl> pressed). After that, the dragging called
    in func 'drag_visual_node' will try to move around the screen and let the
    anchor follows user's mouse position.
    """
    # Get click coordinates on the screen.
    click_pos = mouse_press_event.pos
    # Compute the anchor coordinates by subtracting the click_pos with
    # self.pos in order to get a relative anchor position.
    self.anchor = list(np.array(click_pos[:2]) - np.array(self.pos))

  def drag_visual_node(self, mouse_move_event):
    """ Drag this visual node while holding left click in the selection mode
    (<Ctrl> pressed). The highlighted axis will move with the mouse (the anchor
    point will be 'hooked' to the mouse).
    """
    # Compute the new axis legend center via dragging.
    new_center = mouse_move_event.pos[:2] - self.anchor
    # Get the offset from new_center to current axis center self.loc.
    self.offset = new_center - self.pos

    self.highlight.center = new_center # move highlighte together with axis
    self.pos = new_center
