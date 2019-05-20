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
      # self.events.mouse_move.connect(node.on_mouse_move)
      # self.events.mouse_press.connect(node.on_mouse_press)

    # Connect the XYZAxis visual to the canvas.
    if xyz_axis is not None:
      # Set the parent to view, instead of view.scene, so that this legend will
      # stay at its location on the canvas, and won't rotate away.
      xyz_axis.parent = self.view
      xyz_axis.update_axis()
      self.events.mouse_move.connect(xyz_axis.on_mouse_move)

    # Manage the selected visual node.
    self.selected = None # no selection by default
    self.cursor_on = None # the visual node that cursor hovers on

    # Automatically set the range of the canvas, display, and wrap up.
    self.camera.set_range()
    self.show()
    self.freeze()

  def on_mouse_move(self, event):
    # Hold <Ctrl> to enter node-selection mode.
    if keys.CONTROL in event.modifiers:
      # Temporarily disable the interactive flag of the ViewBox because it
      # is masking all the visuals. See details at:
      # https://github.com/vispy/vispy/issues/1336
      self.view.interactive = False

      if event.button == 1:
        cursor_on = self.visual_at(event.pos)
        if self.cursor_on is not None and cursor_on == self.cursor_on:
          self.cursor_on.highlight.visible = True
      else:

        # Update the cursor_on when mouse moves.
        cursor_on = self.visual_at(event.pos)
        if cursor_on != self.cursor_on: # when moving to a new visual node
          if self.cursor_on is not None: # de-highlight the previous cursor_on
            self.cursor_on.highlight.visible = False
          self.cursor_on = cursor_on # update the cursor_on

        # Only interactive visual nodes will be detected, otherwise None.
        if self.cursor_on is not None:
          self.cursor_on.highlight.visible = True

          # import numpy as np
          # tr = self.scene.node_transform(selected)

          # click_pos = tr.map([*event.pos, 0, 1])
          # click_pos /= click_pos[3]

          # view_vector = tr.map([*event.pos, 1])[:3]
          # view_vector /= np.linalg.norm(view_vector)

          # # axis_to_index = {'x':0, 'y':1, 'z':2}
          # # i = axis_to_index[selected.axis]
          # distance = (selected.pos - click_pos[2]) / view_vector[2]
          # project_point = click_pos[:3] + distance * view_vector
          # print(project_point)

      # Reenable the ViewBox interactive flag.
      self.view.interactive = True

    # Cancel selection and highlight if release <Ctrl>.
    else:
      if self.cursor_on is not None:
        self.cursor_on.highlight.visible = False
        self.cursor_on = None
      if self.selected is not None:
        self.selected.highlight.visible = False
        self.selected = None
