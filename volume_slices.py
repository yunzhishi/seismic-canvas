# Copyright (c) Yunzhi Shi. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import numpy as np
from vispy import scene

from axis_aligned_image import AxisAlignedImage


def volume_slices(volume, x_pos=None, y_pos=None, z_pos=None,
                  seismic_coord_system=True,
                  cmap='grays', clim=None,
                  interpolation='nearest', method='auto'):
  """ Acquire a list of slices in the form of AxisAlignedImage.
  The list can be attached to a SeismicCanvas to visualize the volume
  in 3D interactively.

  Parameters:

  """
  slices_list = []
  # z-axis down seismic coordinate system, or z-axis up normal system.
  if seismic_coord_system: volume = volume[:, ::-1, ::-1]
  shape = volume.shape

  # Automatically set clim (cmap range) if not specified.
  if clim is None: clim = (volume.min(), volume.max())

  # Function that returns the limitation of slice movement.
  def limit(axis):
    if   axis == 'x': return (0, shape[0]-1)
    elif axis == 'y': return (0, shape[1]-1)
    elif axis == 'z': return (0, shape[2]-1)

  # Function that returns a function that provides the slice image at
  # specified slicing position.
  def get_image_func(axis):
    def slicing_at_axis(pos, get_shape=False):
      if get_shape: # just return the shape information
        if   axis == 'x': return shape[1], shape[2]
        elif axis == 'y': return shape[0], shape[2]
        elif axis == 'z': return shape[0], shape[1]
      else: # will slice the volume and return an np array image
        pos = int(np.round(pos))
        if   axis == 'x': return volume[pos, :, :]
        elif axis == 'y': return volume[:, pos, :]
        elif axis == 'z': return volume[:, :, pos]
    return slicing_at_axis

  # Organize the slice positions.
  for xyz_pos in (x_pos, y_pos, z_pos):
    if not (isinstance(xyz_pos, (list, tuple, int, float))
            or xyz_pos is None):
      raise ValueError('Wrong type of x_pos/y_pos/z_pos={}'.format(xyz_pos))
  axis_slices = {'x': x_pos, 'y': y_pos, 'z': z_pos}

  # Create AxisAlignedImage nodes and append to the slices_list.
  for axis, pos_list in axis_slices.items():
    if pos_list is not None:
      if isinstance(pos_list, (int, float)):
        pos_list = [pos_list] # make it iterable, even only one element
      for pos in pos_list:
        pos = int(np.round(pos))
        if seismic_coord_system and axis in ('y', 'z'):
          # Revert y and z axis in seismic coordinate system.
          pos = limit(axis)[1] - pos
        image_node = AxisAlignedImage(get_image_func(axis),
          axis=axis, pos=pos, limit=limit(axis),
          cmap=cmap, clim=clim, interpolation=interpolation, method=method)
        slices_list.append(image_node)

  return slices_list
