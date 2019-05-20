# Copyright (c) Yunzhi Shi. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np
from vispy import scene
from vispy.visuals.transforms import MatrixTransform, STTransform


class AxisAlignedImage(scene.visuals.Image):
  """ Visual subclass displaying an image that aligns to an axis.
  This image should be able to move along the perpendicular direction when
  user gives corresponding inputs.

  Parameters:

  """
  def __init__(self, data, axis='z', pos=0):
    # Create an Image obj and unfreeze it so we can add more
    # attributes inside.
    scene.visuals.Image.__init__(self, data, parent=None)
    self.interactive = True
    self.unfreeze()

    # Determine the axis and position of this plane.
    self.axis = axis
    self.pos = pos

    # The selection highlight (a Plane visual with transparent color).
    # The plane is initialized before any rotation, on '+z' direction.
    self.highlight = scene.visuals.Plane(parent=self,
      width=data.shape[1], height=data.shape[0], direction='+z',
      color=(1, 1, 0, 0.2)) # transparent yellow color
    # Move the plane to align with the image.
    self.highlight.transform = STTransform(
      translate=(data.shape[1]/2, data.shape[0]/2, 0))
    # This is to make sure we can see highlight plane through the images.
    self.highlight.set_gl_state('additive')
    self.highlight.visible = False # only show when selected

    # Apply SRT transform according to the axis attribute.
    self.transform = MatrixTransform()
    if self.axis == 'z':
      # 1. No rotation to do for z axis (y-x) slice. Only translate.
      self.transform.translate((0, 0, self.pos))
    elif self.axis == 'y':
      # 2. Rotation(s) for the y axis (z-x) slice, then translate:
      self.transform.rotate(90, (1, 0, 0))
      self.transform.translate((0, self.pos, 0))
    elif self.axis == 'x':
      # 3. Rotation(s) for the x axis (z-y) slice, then translate:
      self.transform.rotate(90, (1, 0, 0))
      self.transform.rotate(90, (0, 0, 1))
      self.transform.translate((self.pos, 0, 0))

    self.freeze()

  @property
  def axis(self):
    """The dimension that this image is perpendicular aligned to."""
    return self._axis

  @axis.setter
  def axis(self, value):
    value = value.lower()
    if value not in ('z', 'y', 'x'):
      raise ValueError('Invalid value for axis.')
    self._axis = value

  # def on_mouse_move(self, event):
  #   # Hold <Ctrl> to enter node-selection mode.
  #   if keys.CONTROL in event.modifiers:
  #     # Temporarily disable the interactive flag of the ViewBox because it
  #     # is masking all the visuals. See details at:
  #     # https://github.com/vispy/vispy/issues/1336
  #     self.canvas.view.interactive = False

  #     if self.canvas.visual_at(event.pos) == self:
  #       # Highlight when mouse moves over self:
  #       self.highlight.visible = True
  #       if event.button == 1:
  #         self.selected = True # select self when left click
  #         # TODO: perform translation
  #         pass
  #       else:
  #         self.selected = False # otherwise, deselect
  #     elif not self.selected:
  #       # Cancel highlight if mouse moves away and not selected.
  #       self.highlight.visible = False

  #     # Reenable the ViewBox interactive flag.
  #     self.canvas.view.interactive = True

  #   # Cancel selection and highlight if release <Ctrl>.
  #   else:
  #     self.selected = False
  #     self.highlight.visible = False

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

  # def on_mouse_drag(self, event):
  #   # Hold <Ctrl> and drag with left button will move the highlight plane
  #   # first, then the image will also follow after mouse button release.
  #   if keys.CONTROL in event.modifiers and event.button==1:
  #     # Temporarily disable the interactive flag of the ViewBox because it
  #     # is masking all the visuals. See details at:
  #     # https://github.com/vispy/vispy/issues/1336
  #     self.canvas.view.interactive = False

  #     if self.canvas.visual_at(event.pos) == self:
  #       self.selected = True
  #       self.highlight.visible = True

  # def on_mouse_press(self, event):
  #   # Hold <Ctrl> and press with left button will select the corresponding
  #   # AxisAlignedImage, and highlight it.
  #   if keys.CONTROL in event.modifiers and event.button==1:
  #     # Temporarily disable the interactive flag of the ViewBox because it
  #     # is masking all the visuals. See details at:
  #     # https://github.com/vispy/vispy/issues/1336
  #     self.canvas.view.interactive = False

  #     if self.canvas.visual_at(event.pos) == self:
  #       self.selected = True
  #       self.highlight.visible = True
  #     else:
  #       self.selected = False
  #       self.highlight.visible = False

  #     # Reenable the ViewBox interactive flag.
  #     self.canvas.view.interactive = True

    # if event.button == 1:
    #   if self.axis == 'z':
    #     # tr = self.canvas.view.scene.node_transform(self)
    #     tr = self.parent.transforms.get_transform('render', 'visual')
    #     pos = tr.map(event.pos)
    #     print('AXIS {} - x={:6.1f}, y={:6.1f}, z={:6.1f}'.format(
    #       self.axis.upper(), pos[0], pos[1], pos[2]))

  def _compute_bounds(self, axis_3d, view):
    """ Overwrite the original 2D bounds of the Image class. This will correct 
    the automatic range setting for the camera in the scene canvas. In the
    original Image class, the code assumes that the image always lies in x-y
    plane; here we generalize that to x-z and y-z plane.
    
    Parameters:
    axis_3d: int in {0, 1, 2}, represents the axis in 3D view box.
    view: the ViewBox object that connects to the parent.

    The function returns a tuple (low_bounds, high_bounds) that represents
    the spatial limits of self obj in the 3D scene.
    """
    # Note: self.size[0] is slow dim size, self.size[1] is fast dim size.
    if self.axis == 'z':
      if   axis_3d==0: return (0, self.size[0])
      elif axis_3d==1: return (0, self.size[1])
      elif axis_3d==2: return (self.pos, self.pos)
    elif self.axis == 'y':
      if   axis_3d==0: return (0, self.size[0])
      elif axis_3d==1: return (self.pos, self.pos)
      elif axis_3d==2: return (0, self.size[1])
    elif self.axis == 'x':
      if   axis_3d==0: return (self.pos, self.pos)
      elif axis_3d==1: return (0, self.size[0])
      elif axis_3d==2: return (0, self.size[1])
