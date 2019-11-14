# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (C) 2019 Yunzhi Shi @ The University of Texas at Austin.
# All rights reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np
from vispy import scene
from vispy.visuals.transforms import MatrixTransform, STTransform


class AxisAlignedImage(scene.visuals.Image):
  """ Visual subclass displaying an image that aligns to an axis.
  This image should be able to move along the perpendicular direction when
  user gives corresponding inputs.

  Parameters:

  """
  def __init__(self, image_funcs, axis='z', pos=0, limit=None,
               seismic_coord_system=True,
               cmaps=['grays'], clims=None,
               interpolation='nearest', method='auto'):

    assert clims is not None, 'clim must be specified explicitly.'

    # Create an Image obj and unfreeze it so we can add more
    # attributes inside.
    # First image (from image_funcs[0])
    scene.visuals.Image.__init__(self, parent=None, # no image func yet
      cmap=cmaps[0], clim=clims[0],
      interpolation=interpolation, method=method)
    self.unfreeze()
    self.interactive = True

    # Other images ...
    self.overlaid_images = [self]
    for i_img in range(1, len(image_funcs)):
      overlaid_image = scene.visuals.Image(parent=self,
        cmap=cmaps[i_img], clim=clims[i_img],
        interpolation=interpolation, method=method)
      self.overlaid_images.append(overlaid_image)

    # Set GL state. Must check depth test, otherwise weird in 3D.
    self.set_gl_state(depth_test=True, depth_func='lequal',
      blend_func=('src_alpha', 'one_minus_src_alpha'))

    # Determine the axis and position of this plane.
    self.axis = axis
    # Check if pos is within the range.
    if limit is not None:
      assert (pos>=limit[0]) and (pos<=limit[1]), \
        'pos={} is outside limit={} range.'.format(pos, limit)
    self.pos = pos
    self.limit = limit
    self.seismic_coord_system = seismic_coord_system

    # Get the image_func that returns either image or image shape.
    self.image_funcs = image_funcs # a list of functions!
    shape = self.image_funcs[0](self.pos, get_shape=True)

    # The selection highlight (a Plane visual with transparent color).
    # The plane is initialized before any rotation, on '+z' direction.
    self.highlight = scene.visuals.Plane(parent=self,
      width=shape[0], height=shape[1], direction='+z',
      color=(1, 1, 0, 0.1)) # transparent yellow color
    # Move the plane to align with the image.
    self.highlight.transform = STTransform(
      translate=(shape[0]/2, shape[1]/2, 0))
    # This is to make sure we can see highlight plane through the images.
    self.highlight.set_gl_state('additive', depth_test=True)
    self.highlight.visible = False # only show when selected

    # Set the anchor point (2D local world coordinates). The mouse will
    # drag this image by anchor point moving in the normal direction.
    self.anchor = None # None by default
    self.offset = 0

    # Apply SRT transform according to the axis attribute.
    self.transform = MatrixTransform()
    # Move the image plane to the corresponding location.
    self._update_location()

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

  def set_anchor(self, mouse_press_event):
    """ Set an anchor point (2D coordinate on the image plane) when left click
    in the selection mode (<Ctrl> pressed). After that, the dragging called
    in func 'drag_visual_node' will try to move along the normal direction
    and let the anchor follows user's mouse position as close as possible.
    """
    # Get the screen-to-local transform to get camera coordinates.
    tr = self.canvas.scene.node_transform(self)

    # Get click (camera) coordinate in the local world.
    click_pos = tr.map([*mouse_press_event.pos, 0, 1])
    click_pos /= click_pos[3] # rescale to cancel out the pos.w factor
    # Get the view direction (camera-to-target) vector in the local world.
    view_vector = tr.map([*mouse_press_event.pos, 1, 1])[:3]
    view_vector /= np.linalg.norm(view_vector) # normalize to unit vector

    # Get distance from camera to the drag anchor point on the image plane.
    # Eq 1: click_pos + distance * view_vector = anchor
    # Eq 2: anchor[2] = 0 <- intersects with the plane
    # The following equation can be derived by Eq 1 and Eq 2.
    distance = (0. - click_pos[2]) / view_vector[2]
    self.anchor = click_pos[:2] + distance * view_vector[:2] # only need vec2

  def drag_visual_node(self, mouse_move_event):
    """ Drag this visual node while holding left click in the selection mode
    (<Ctrl> pressed). The plane will move in the normal direction
    perpendicular to this image, and the anchor point (set with func
    'set_anchor') will move along the normal direction to stay as close to
    the mouse as possible, so that user feels like 'dragging' the plane.
    """
    # Get the screen-to-local transform to get camera coordinates.
    tr = self.canvas.scene.node_transform(self)

    # Unlike in 'set_anchor', we now convert most coordinates to the screen
    # coordinate system, because it's more intuitive for user to do operations
    # in 2D and get 2D feedbacks, e.g. mouse leading the anchor point.
    anchor = [*self.anchor, self.pos, 1] # 2D -> 3D
    anchor_screen = tr.imap(anchor) # screen coordinates of the anchor point
    anchor_screen /= anchor_screen[3] # rescale to cancel out 'w' term
    anchor_screen = anchor_screen[:2] # only need vec2

    # Compute the normal vector, starting from the anchor point and
    # perpendicular to the image plane.
    normal = [*self.anchor, self.pos+1, 1] # +[0,0,1,0] from anchor
    normal_screen = tr.imap(normal) # screen coordinates of anchor + [0,0,1,0]
    normal_screen /= normal_screen[3] # rescale to cancel out 'w' term
    normal_screen = normal_screen[:2] # only need vec2
    normal_screen -= anchor_screen # end - start = vector
    normal_screen /= np.linalg.norm(normal_screen) # normalize to unit vector

    # Use the vector {anchor_screen -> mouse.pos} and project to the
    # normal_screen direction using dot product, we can get how far the plane
    # should be moved (on the screen!).
    drag_vector = mouse_move_event.pos[:2] - anchor_screen
    drag = np.dot(drag_vector, normal_screen) # normal_screen must be length 1

    # We now need to convert the move distance from screen coordinates to
    # local world coordinates. First, find where the anchor is on the screen
    # after dragging; then, convert that screen point to a local line shooting
    # across the normal vector; finally, find where the line comes directly
    # above/below the anchor point (before dragging) and get that distance as
    # the true dragging distance in local coordinates.
    new_anchor_screen = anchor_screen + normal_screen * drag
    new_anchor = tr.map([*new_anchor_screen, 0, 1])
    new_anchor /= new_anchor[3] # rescale to cancel out the pos.w factor
    view_vector = tr.map([*new_anchor_screen, 1, 1])[:3]
    view_vector /= np.linalg.norm(view_vector) # normalize to unit vector
    # Solve this equation:
    # new_anchor := new_anchor + view_vector * ?,
    # ^^^ describe a 3D line of possible new anchor positions
    # arg min (?) |new_anchor[:2] - anchor[:2]|
    # ^^^ find a point on that 3D line that minimize the 2D distance between
    #     new_anchor and anchor.
    numerator = anchor[:2] - new_anchor[:2]
    numerator *= view_vector[:2] # element-wise multiplication
    numerator = np.sum(numerator)
    denominator = view_vector[0]**2 + view_vector[1]**2
    shoot_distance = numerator / denominator
    # Shoot from new_anchor to get the new intersect point. The z- coordinate
    # of this point will be our dragging offset.
    offset = new_anchor[2] + view_vector[2] * shoot_distance

    # Note: must reverse normal direction from -y direction to +y!
    if self.axis == 'y': offset = -offset
    # Limit the dragging within range.
    if self.limit is not None:
      if self.pos + offset < self.limit[0]: offset = self.limit[0] - self.pos
      if self.pos + offset > self.limit[1]: offset = self.limit[1] - self.pos
    self.offset = offset
    # Note: must reverse normal direction from +y direction to -y!
    if self.axis == 'y': offset = -offset

    self._update_location()

  def _update_location(self):
    """ Update the image plane to the dragged location and redraw this image.
    """
    self.pos += self.offset
    self.pos = int(np.round(self.pos)) # must round to nearest integer location

    # Update the transformation in order to move to new location.
    self.transform.reset()
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

    # Update image on the slice based on current position. The numpy array
    # is transposed due to a conversion from i-j to x-y axis system.
    # First image, the primary one:
    self.set_data(self.image_funcs[0](self.pos).T)
    # Other images, overlaid on the primary image:
    for i_img in range(1, len(self.image_funcs)):
      self.overlaid_images[i_img].set_data(
        self.image_funcs[i_img](self.pos).T)

    # Reset attributes after dragging completes.
    self.offset = 0
    self._bounds_changed() # update the bounds with new self.pos

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
