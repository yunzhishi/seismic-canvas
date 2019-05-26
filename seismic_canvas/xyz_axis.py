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
from vispy.visuals.transforms import MatrixTransform


class XYZAxis(scene.visuals.XYZAxis):
  """ An XYZAxis legend visual that add some interactivity fixes to be used
  in 3D. It rotates correctly, and can be dragged around.

  Parameters:

  """
  def __init__(self, loc=(60, 60), size=50, visible=True,
               seismic_coord_system=True,
               width=2, antialias=True, parent=None):
    # Create a scene.visuals.XYZAxis (without parent by default).
    scene.visuals.XYZAxis.__init__(self, parent=parent,
                                   width=width, antialias=antialias)
    self.interactive = True
    self.unfreeze()
    self.visible = visible

    # Determine the size and position.
    self.loc = loc
    self.size = size
    # z-axis down seismic coordinate system, or z-axis up normal system.
    self.seismic_coord_system = seismic_coord_system

    # The selection highlight (a Ellipse visual with transparent color).
    # The circle is centered on the axis legend.
    self.highlight = scene.visuals.Ellipse(parent=parent,
      center=self.loc, radius=self.size,
      color=(1, 1, 0, 0.5)) # transparent yellow color
    self.highlight.visible = False # only show when selected

    # Set the anchor point (2D screen coordinates). The mouse will
    # drag the axis by anchor point to move around the screen.
    self.anchor = None # None by default
    self.offset = 0

    # The axis legend is rotated to align with the parent camera. Then put
    # the legend to specified location and scale up to desired size.
    # The location is computed from the top-left corner.
    self.transform = MatrixTransform()
    self._update_axis()

    self.freeze()

  def on_mouse_move(self, event):
    if event.button == 1 and event.is_dragging:
      self._update_axis()

  def set_anchor(self, mouse_press_event):
    """ Set an anchor point (2D screen coordinates) when left click
    in the selection mode (<Ctrl> pressed). After that, the dragging called
    in func 'drag_visual_node' will try to move around the screen and let the
    anchor follows user's mouse position.
    """
    # Get click coordinates on the screen.
    click_pos = mouse_press_event.pos
    # Compute the anchor coordinates by subtracting the click_pos with
    # self.loc in order to get a relative anchor position.
    self.anchor = list(np.array(click_pos[:2]) - np.array(self.loc))

  def drag_visual_node(self, mouse_move_event):
    """ Drag this visual node while holding left click in the selection mode
    (<Ctrl> pressed). The highlighted axis will move with the mouse (the anchor
    point will be 'hooked' to the mouse).
    """
    # Compute the new axis legend center via dragging.
    new_center = mouse_move_event.pos[:2] - self.anchor
    # Get the offset from new_center to current axis center self.loc.
    self.offset = new_center - self.loc

    self.highlight.center = new_center # move highlighte together with axis
    self._update_location()

  def _update_location(self):
    """ Update the axis plane to the dragged location and redraw.
    """
    self.loc += self.offset
    self._update_axis()

    # Reset attributes after dragging completes.
    self.offset = 0

  def _update_axis(self):
    """ Align the axis legend with the current camera rotation, scale up to
    desired size, then put the axis legend at pos (measuring from the
    top-left corner).
    """
    if self.parent is None:
      return # if not connected to any parent, no need to update

    tr = self.transform
    tr.reset() # remove all transforms (put back to origin)

    # Revert y and z axis in seismic coordinate system.
    if self.seismic_coord_system:
      tr.scale((1, -1, -1))

    # Align camera rotation. This only works for turntable camera!!
    tr.rotate(90, (1, 0, 0)) # for some reason I have to do this at first ...
    tr.rotate(self.parent.camera.azimuth, (0, 1, 0))
    tr.rotate(self.parent.camera.elevation, (1, 0, 0))
    # Scale up to desired size and put to desired location.
    tr.scale((*(self.size,)*2, 0.001)) # only scale in screen plane!
    tr.translate(self.loc)

    self.update()
