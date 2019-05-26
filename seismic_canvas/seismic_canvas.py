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

from vispy import scene, io
from vispy.util import keys
from vispy.gloo.util import _screenshot

from .xyz_axis import XYZAxis
from .colorbar import Colorbar


class SeismicCanvas(scene.SceneCanvas):
  """A canvas that automatically draw all contents in a 3D seismic
  visualization scene, which may include 3D seismic volume slices, axis
  legend, colorbar, etc.

  Parameters:

  """
  def __init__(self, size=(800, 720), bgcolor='white',
               visual_nodes=[], xyz_axis=None, colorbar=None,
               fov=45, azimuth=120, elevation=30,
               title='Seismic Canvas'):
    # Create a SceneCanvas obj and unfreeze it so we can add more
    # attributes inside.
    scene.SceneCanvas.__init__(
      self, keys='interactive', size=size, bgcolor=bgcolor,
      title=title)
    self.unfreeze()

    # Attach a ViewBox to this canvas and initiate the camera with the given
    # parameters.
    self.view = self.central_widget.add_view()
    self.camera = scene.cameras.TurntableCamera(
      fov=fov, azimuth=azimuth, elevation=elevation)
    self.fov = fov; self.azimuth = azimuth; self.elevation = elevation
    self.view.camera = self.camera

    # Attach all main visual nodes (e.g. slices, meshs, volumes) to the ViewBox.
    for node in visual_nodes:
      self.view.add(node)

    # Connect the XYZAxis visual to the canvas.
    if xyz_axis is not None:
      # Set the parent to view, instead of view.scene, so that this legend will
      # stay at its location on the canvas, and won't rotate away.
      xyz_axis.parent = self.view
      xyz_axis.canvas_size = self.size
      self.events.resize.connect(xyz_axis.on_resize)
      xyz_axis.highlight.parent = self.view
      xyz_axis._update_axis()
      self.events.mouse_move.connect(xyz_axis.on_mouse_move)

    # Connect the Colorbar visual to the canvas.
    if colorbar is not None:
      # Set the parent to view, instead of view.scene, so that the colorbar
      # will stay at its location on the canvas, and won't rotate away.
      colorbar.parent = self.view
      colorbar.canvas_size = self.size
      self.events.resize.connect(colorbar.on_resize)
      colorbar.highlight.parent = self.view

    # Manage the selected visual node.
    self.drag_mode = False
    self.selected = None # no selection by default
    self.hover_on = None # visual node that mouse hovers on, None by default

    # Automatically set the range of the canvas, display, and wrap up.
    self.camera.set_range()
    self.show()
    self.freeze()

  def on_mouse_press(self, event):
    # Hold <Ctrl> to enter drag mode or press <d> to toggle.
    if keys.CONTROL in event.modifiers or self.drag_mode:
      # Temporarily disable the interactive flag of the ViewBox because it
      # is masking all the visuals. See details at:
      # https://github.com/vispy/vispy/issues/1336
      self.view.interactive = False
      hover_on = self.visual_at(event.pos)

      if event.button == 1 and self.selected is None:
        # If no previous selection, make a new selection if cilck on a valid
        # visual node, and highlight this node.
        if hover_on is not None:
          self.selected = hover_on
          self.selected.highlight.visible = True
          # Set the anchor point on this node.
          self.selected.set_anchor(event)

        # Nothing to do if the cursor is NOT on a valid visual node.

      # Reenable the ViewBox interactive flag.
      self.view.interactive = True

  def on_mouse_release(self, event):
    # Hold <Ctrl> to enter drag mode or press <d> to toggle.
    if keys.CONTROL in event.modifiers or self.drag_mode:
      if self.selected is not None:
        # Erase the anchor point on this node.
        self.selected.anchor = None
        # Then, deselect any previous selection.
        self.selected = None

  def on_mouse_move(self, event):
    # Hold <Ctrl> to enter drag mode or press <d> to toggle.
    if keys.CONTROL in event.modifiers or self.drag_mode:
      # Temporarily disable the interactive flag of the ViewBox because it
      # is masking all the visuals. See details at:
      # https://github.com/vispy/vispy/issues/1336
      self.view.interactive = False
      hover_on = self.visual_at(event.pos)

      if event.button == 1:
        if self.selected is not None:
          self.selected.drag_visual_node(event)
      else:
        # If the left cilck is released, update highlight to the new visual
        # node that mouse hovers on.
        if hover_on != self.hover_on:
          if self.hover_on is not None: # de-highlight previous hover_on
            self.hover_on.highlight.visible = False
            self.hover_on.order = 0 # -> revert the node to default order
            self._draw_order.clear()
          self.hover_on = hover_on
          if self.hover_on is not None: # highlight the new hover_on
            self.hover_on.highlight.visible = True
            self.hover_on.order = -1 # -> move the node to furthest back
            self._draw_order.clear()

      # Reenable the ViewBox interactive flag.
      self.view.interactive = True

  def on_key_press(self, event):
    # Hold <Ctrl> to enter drag mode.
    if keys.CONTROL in event.modifiers:
      # TODO: I cannot get the mouse position within the key_press event ...
      # so it is not yet implemented. The purpose of this event handler
      # is simply trying to highlight the visual node when <Ctrl> is pressed
      # but mouse is not moved (just nicer interactivity), so not very
      # high priority now.
      pass
    # Press <Space> to reset camera.
    if event.text == ' ':
      self.camera.fov = self.fov
      self.camera.azimuth = self.azimuth
      self.camera.elevation = self.elevation
      self.camera.set_range()
      for child in self.view.children:
        if type(child) == XYZAxis:
          child._update_axis()
    # Press <s> to save a screenshot.
    if event.text == 's':
      screenshot = _screenshot()
      io.write_png(self.title + '.png', screenshot)
    # Press <d> to toggle drag mode.
    if event.text == 'd':
      if not self.drag_mode:
        self.drag_mode = True
        self.camera.viewbox.events.mouse_move.disconnect(
          self.camera.viewbox_mouse_event)
      else:
        self.drag_mode = False
        self._exit_drag_mode()
        self.camera.viewbox.events.mouse_move.connect(
          self.camera.viewbox_mouse_event)

  def on_key_release(self, event):
    # Cancel selection and highlight if release <Ctrl>.
    if keys.CONTROL not in event.modifiers:
      self._exit_drag_mode()

  def _exit_drag_mode(self):
    if self.hover_on is not None:
      self.hover_on.highlight.visible = False
      self.hover_on = None
    if self.selected is not None:
      self.selected.highlight.visible = False
      self.selected.anchor = None
      self.selected = None
