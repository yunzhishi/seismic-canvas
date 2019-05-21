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

    # Set the anchor point (2D local world coordinates). The mouse will
    # drag this image by the anchor point moving in the normal direction.
    self.anchor = (0, 0) # set at origin point by default

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

  def drag_visual_node(self, drag_event):
    """ Drag this visual node according to the drag_event.
    The visual node's position should be updated following the mouse position.
    """
    # Get the screen-to-local transform to get camera coordinates.
    tr = self.canvas.scene.node_transform(self)

    # Get click (camera) coordinate in the local world.
    click_pos = tr.map([*drag_event.pos, 0, 1])
    click_pos /= click_pos[3] # rescale to cancel out the pos.w factor
    # Get the view direction (camera-to-target) vector in the local world.
    # TODO: this vector is actually slightly distorted in perspective
    # (non-orthogonal) projection, so very subtle inaccuracy can occur!
    view_vector = tr.map([*drag_event.pos, 1, 1])[:3]
    view_vector /= np.linalg.norm(view_vector) # normalize to unit vector

    # Get distance from camera to the drag anchor point on the image plane.
    # Eq 1: click_pos + distance * view_vector = anchor
    # Eq 2: anchor[2] = self.pos  <- direction normal to the plane
    # The following equation can be derived by Eq 1 and Eq 2.
    distance = (self.pos - click_pos[2]) / view_vector[2]
    anchor = click_pos[:3] + distance * view_vector # we only need vec3

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
