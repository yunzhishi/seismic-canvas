# Copyright (c) Yunzhi Shi. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from vispy import scene
from vispy.util import keys


class SeismicCanvas(scene.SceneCanvas):
  """A canvas that automatically draw all contents in a 3D seismic
  visualization scene, which may include 3D seismic volume slices, axis
  legend, colorbar, etc.

  Parameters:

  """
  def __init__(self, size=(800, 800), bgcolor='white',
               visual_nodes=[],
               fov=45, azimuth=120, elevation=30,
               xyz_axis=None):
    # Create a SceneCanvas obj and unfreeze it so we can add more
    # attributes inside.
    scene.SceneCanvas.__init__(
      self, keys='interactive', size=size, bgcolor=bgcolor)
    self.unfreeze()

    # Attach a ViewBox to this canvas and initiate the camera with the given
    # parameters.
    self.view = self.central_widget.add_view()
    self.camera = scene.cameras.TurntableCamera(
      fov=fov, azimuth=azimuth, elevation=elevation)
    # self.camera = scene.cameras.PanZoomCamera()
    self.view.camera = self.camera

    # Attach all main visual nodes (e.g. slices, meshs, volumes) to the ViewBox.
    for node in visual_nodes:
      self.view.add(node)

    # Connect the XYZAxis visual to the canvas.
    if xyz_axis is not None:
      # Set the parent to view, instead of view.scene, so that this legend will
      # stay at its location on the canvas, and won't rotate away.
      xyz_axis.parent = self.view
      xyz_axis.update_axis()
      self.events.mouse_move.connect(xyz_axis.on_mouse_move)

    # Manage the selected visual node.
    self.selected = None # no selection by default
    self.hover_on = None # visual node that mouse hovers on, None by default

    # Automatically set the range of the canvas, display, and wrap up.
    self.camera.set_range()
    self.show()
    self.freeze()

  def on_mouse_press(self, event):
    # Hold <Ctrl> to enter node-selection mode.
    if keys.CONTROL in event.modifiers:
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
    # Hold <Ctrl> to enter node-selection mode.
    if keys.CONTROL in event.modifiers:
      if self.selected is not None:
        # If the left click is released, complete the dragging operation.
        self.selected.update_location()
        # Erase the anchor point on this node.
        self.selected.anchor = None
        # Reset highlight to default state.
        self.selected.reset_highlight()
        # Then, deselect any previous selection.
        self.selected = None

  def on_mouse_move(self, event):
    # Hold <Ctrl> to enter node-selection mode.
    if keys.CONTROL in event.modifiers:
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
    # Hold <Ctrl> to enter node-selection mode.
    if keys.CONTROL in event.modifiers:
      # TODO: I cannot get the mouse position within the key_press event ...
      # so it is not yet implemented. The purpose of this event handler
      # is simply trying to highlight the visual node when <Ctrl> is pressed
      # but mouse is not moved (just nicer interactivity), so not very
      # high priority now.
      pass

  def on_key_release(self, event):
    # Cancel selection and highlight if release <Ctrl>.
    if keys.CONTROL not in event.modifiers:
      if self.hover_on is not None:
        self.hover_on.highlight.visible = False
        self.hover_on = None
      if self.selected is not None:
        self.selected.highlight.visible = False
        self.selected.reset_highlight()
        self.selected.anchor = None
        self.selected = None
