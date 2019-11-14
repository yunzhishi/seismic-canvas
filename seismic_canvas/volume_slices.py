# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (C) 2019 Yunzhi Shi @ The University of Texas at Austin.
# All rights reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np
from vispy import scene

from .axis_aligned_image import AxisAlignedImage


def volume_slices(volumes, x_pos=None, y_pos=None, z_pos=None,
                  preproc_funcs=None,
                  seismic_coord_system=True,
                  cmaps='grays', clims=None,
                  interpolation='nearest', method='auto'):
  """ Acquire a list of slices in the form of AxisAlignedImage.
  The list can be attached to a SeismicCanvas to visualize the volume
  in 3D interactively.

  Parameters:

  """
  # Check whether single volume or multiple volumes are provided.
  if isinstance(volumes, (tuple, list)):
    n_vol = len(volumes)
    if preproc_funcs is None:
      preproc_funcs = [None] * n_vol # repeat n times ...
    else:
      assert isinstance(preproc_funcs, (tuple, list)) \
        and len(preproc_funcs) >= n_vol
    assert isinstance(cmaps, (tuple, list)) \
      and len(cmaps) >= n_vol
    assert isinstance(clims, (tuple, list)) \
      and len(clims) >= n_vol \
      and len(clims[0]) == 2 or clims[0] is None
    for vol in volumes:
      assert vol.shape == volumes[0].shape
  else:
    volumes = [volumes]
    preproc_funcs = [preproc_funcs]
    cmaps = [cmaps]
    clims = [clims]
    n_vol = 1

  slices_list = []
  # z-axis down seismic coordinate system, or z-axis up normal system.
  if seismic_coord_system:
    for i_vol in range(n_vol):
      volumes[i_vol] = volumes[i_vol][:, ::-1, ::-1]
  shape = volumes[0].shape

  # Automatically set clim (cmap range) if not specified.
  for i_vol in range(n_vol):
    clim = clims[i_vol]
    vol = volumes[i_vol]
    if clim is None or clim=='auto':
      if type(vol) == np.memmap:
        from warnings import warn
        warn("cmap='auto' with np.memmap can significantly impact launching " +
             "time, cmap=(cmin, cmax) is recommended.",
             UserWarning, stacklevel=2)
      clims[i_vol] = (vol.min(), vol.max())

  # Function that returns the limitation of slice movement.
  def limit(axis):
    if   axis == 'x': return (0, shape[0]-1)
    elif axis == 'y': return (0, shape[1]-1)
    elif axis == 'z': return (0, shape[2]-1)

  # Function that returns a function that provides the slice image at
  # specified slicing position.
  def get_image_func(axis, i_vol):
    def slicing_at_axis(pos, get_shape=False):
      if get_shape: # just return the shape information
        if   axis == 'x': return shape[1], shape[2]
        elif axis == 'y': return shape[0], shape[2]
        elif axis == 'z': return shape[0], shape[1]
      else: # will slice the volume and return an np array image
        pos = int(np.round(pos))
        vol = volumes[i_vol]
        preproc_f = preproc_funcs[i_vol]
        if preproc_f is not None:
          if   axis == 'x': return preproc_f(vol[pos, :, :])
          elif axis == 'y': return preproc_f(vol[:, pos, :])
          elif axis == 'z': return preproc_f(vol[:, :, pos])
        else:
          if   axis == 'x': return vol[pos, :, :]
          elif axis == 'y': return vol[:, pos, :]
          elif axis == 'z': return vol[:, :, pos]
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
        # Generate a list of image funcs for each input volume.
        image_funcs = []
        for i_vol in range(n_vol):
          image_funcs.append(get_image_func(axis, i_vol))
        # Construct the AxisAlignedImage node.
        image_node = AxisAlignedImage(image_funcs,
          axis=axis, pos=pos, limit=limit(axis),
          seismic_coord_system=seismic_coord_system,
          cmaps=cmaps, clims=clims,
          interpolation=interpolation, method=method)
        slices_list.append(image_node)

  return slices_list
