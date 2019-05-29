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

""" A demonstration of the new 3D visualization tool applied to the research
'Optimal Surface Voting': https://github.com/xinwucwp/osv.
"""

import os
import numpy as np
from vispy import app
from vispy.color import get_colormap, Colormap, Color
from vispy.scene.visuals import Mesh

from seismic_canvas import (SeismicCanvas, volume_slices, XYZAxis, Colorbar)
from osv_read_skin import FaultSkin


if __name__ == '__main__':
  # Some common parameters used by all images.
  volume_shape = (420, 400, 100)
  slicing = {'x_pos': 32, 'y_pos': 25, 'z_pos': 93}
  canvas_params = {'size': (1400, 1000),
                   'axis_scales': (1, 1, 1.5), # stretch z-axis
                   'colorbar_region_ratio': 0.1,
                   'fov': 30, 'elevation': 45, 'azimuth': 45,
                   'zoom_factor': 1.6}
  colorbar_size = (800, 20)


  # Image 1: seismic overlaid by planarity attribute.
  seismic_vol = np.memmap('./F3_seismic.dat', dtype='>f4',
                          mode='r', shape=volume_shape)
  planarity_vol = np.memmap('./F3_planarity.dat', dtype='>f4',
                            mode='r', shape=volume_shape)

  seismic_cmap = 'grays'
  seismic_range = (-2.0, 2.0)
  # Get a colormap with alpha decreasing when value decreases.
  planarity_cmap = Colormap([[1,1,1, 0], [1,1,0, 0.5], [1,0,0, 1]])
  planarity_range = (0.25, 1.0)

  visual_nodes = volume_slices([seismic_vol, planarity_vol],
    cmaps=[seismic_cmap, planarity_cmap],
    clims=[seismic_range, planarity_range],
    # The preprocessing functions can perform some simple gaining ops.
    preproc_funcs=[None, lambda x: 1-np.power(x, 8)],
    interpolation='bilinear', **slicing)
  xyz_axis = XYZAxis()
  colorbar = Colorbar(cmap=planarity_cmap, clim=planarity_range,
                      label_str='1 - Planarity', size=colorbar_size)

  canvas1 = SeismicCanvas(title='Planarity',
                          visual_nodes=visual_nodes,
                          xyz_axis=xyz_axis,
                          colorbar=colorbar,
                          **canvas_params)


  # Image 2: seismic overlaid by fault semblance.
  semblance_vol = np.memmap('./F3_semblance.dat', dtype='>f4',
                            mode='r', shape=volume_shape)

  # Get a colormap with alpha decreasing when value decreases.
  original_cmap = get_colormap('RdYeBuCy')
  alpha = np.linspace(0, 1, 128) # 128 color samples
  rgba = np.array([original_cmap.map(x) for x in alpha]).squeeze()
  rgba[:, -1] = alpha
  semblance_cmap = Colormap(rgba)
  semblance_range = (0.25, 1.0)

  visual_nodes = volume_slices([seismic_vol, semblance_vol],
    cmaps=[seismic_cmap, semblance_cmap],
    clims=[seismic_range, semblance_range],
    interpolation='bilinear', **slicing)
  xyz_axis = XYZAxis()
  colorbar = Colorbar(cmap=semblance_cmap, clim=semblance_range,
                      label_str='Fault Semblance', size=colorbar_size)

  canvas2 = SeismicCanvas(title='Fault Semblance',
                          visual_nodes=visual_nodes,
                          xyz_axis=xyz_axis,
                          colorbar=colorbar,
                          **canvas_params)


  # Image 3: fault strike angle.
  strike_vol = np.memmap('./F3_strike.dat', dtype='>f4',
                         mode='r', shape=volume_shape)

  strike_cmap = 'hsl'
  strike_range = (0, 180)

  # Use preprocess function to warp strike angles in range 0 ~ 180 degrees.
  def strike_warp(strike):
    warped = strike.copy()
    warp_index = np.where(strike > 180)
    warped[warp_index] = 180 - warped[warp_index]
    return warped

  visual_nodes = volume_slices(strike_vol,
    cmaps=strike_cmap, clims=strike_range,
    preproc_funcs=strike_warp,
    interpolation='bilinear', **slicing)
  xyz_axis = XYZAxis()
  colorbar = Colorbar(cmap=strike_cmap, clim=strike_range,
                      label_str='Fault Strike Angle', size=colorbar_size)

  canvas3 = SeismicCanvas(title='Fault Strike Angle',
                          visual_nodes=visual_nodes,
                          xyz_axis=xyz_axis,
                          colorbar=colorbar,
                          **canvas_params)


  # Image 4: seismic overlaid by fault surface voting scores.
  voting_vol = np.memmap('./F3_voting.dat', dtype='>f4',
                         mode='r', shape=volume_shape)

  # Get a colormap with alpha decreasing when value decreases.
  original_cmap = get_colormap('viridis')
  alpha = np.linspace(0, 1, 128) # 128 color samples
  rgba = np.array([original_cmap.map(x) for x in alpha]).squeeze()
  rgba[:, -1] = alpha
  voting_cmap = Colormap(rgba)
  voting_range = (0.25, 1.0)

  visual_nodes = volume_slices([seismic_vol, voting_vol],
    cmaps=[seismic_cmap, voting_cmap],
    clims=[seismic_range, voting_range],
    interpolation='bilinear', **slicing)
  xyz_axis = XYZAxis()
  colorbar = Colorbar(cmap=voting_cmap, clim=voting_range,
                      label_str='Voting Scores', size=colorbar_size)

  canvas4 = SeismicCanvas(title='Voting Scores',
                          visual_nodes=visual_nodes,
                          xyz_axis=xyz_axis,
                          colorbar=colorbar,
                          **canvas_params)


  # Image 5: seismic with fault skin surfaces (meshes).
  fault_surfaces = []
  fault_cmap = 'hsl'
  fault_range = (0, 180)

  # Read from skin files using FaultSkin class.
  skin_dir = './F3_fault_skins'
  for filename in os.listdir(skin_dir):
    if filename.startswith('skin') and filename.endswith('.dat'):
      skin = FaultSkin(os.path.join(skin_dir, filename))
      verts, faces = skin.get_vertices_and_faces()
      # Convert to seismic coord system.
      verts[:, 1] = volume_shape[1] - verts[:, 1]
      verts[:, 2] = volume_shape[2] - verts[:, 2]

      strikes = np.zeros(verts.shape[0])
      for i, cell in enumerate(skin.cells):
        strike = cell.strike
        if strike > 180: strike = 360 - strike
        strikes[i] = strike

      fault_surface = Mesh(verts, faces,
        vertex_values=strikes, shading='smooth')
      fault_surface.cmap = fault_cmap
      fault_surface.clim = fault_range
      fault_surface.shininess = 0.01
      fault_surface.ambient_light_color = Color([.2, .2, .2, 1])
      fault_surface.light_dir = (5, -10, 5)
      fault_surfaces.append(fault_surface)

  visual_nodes = volume_slices(seismic_vol,
    cmaps=seismic_cmap,
    clims=seismic_range,
    interpolation='bilinear', **slicing)
  xyz_axis = XYZAxis()
  colorbar = Colorbar(cmap=fault_cmap, clim=fault_range,
                      label_str='Fault Strike Angle', size=colorbar_size)

  visual_nodes += fault_surfaces
  canvas5 = SeismicCanvas(title='Fault Surfaces',
                          visual_nodes=visual_nodes,
                          xyz_axis=xyz_axis,
                          colorbar=colorbar,
                          **canvas_params)


  # Image 6: seismic overlaid by fault likelihood.
  likelihood_vol = np.memmap('./F3_likelihood.dat', dtype='>f4',
                             mode='r', shape=volume_shape)

  # Get a colormap with alpha decreasing when value decreases.
  original_cmap = get_colormap('spring')
  alpha = np.linspace(0, 1, 128) # 128 color samples
  rgba = np.array([original_cmap.map(x) for x in alpha]).squeeze()
  rgba[:, -1] = alpha
  likelihood_cmap = Colormap(rgba)
  likelihood_range = (0.25, 1.0)

  visual_nodes = volume_slices([seismic_vol, likelihood_vol],
    cmaps=[seismic_cmap, likelihood_cmap],
    clims=[seismic_range, likelihood_range],
    interpolation='bilinear', **slicing)
  xyz_axis = XYZAxis(seismic_coord_system=False) # try normal coord system
  colorbar = Colorbar(cmap=likelihood_cmap, clim=likelihood_range,
                      label_str='Fault Likelihood', size=colorbar_size,
                      label_color='white') # dark background

  dark_canvas_params = canvas_params
  dark_canvas_params['bgcolor'] = (.1, .1, .1, 1) # dark background
  canvas6 = SeismicCanvas(title='Fault Likelihood',
                          visual_nodes=visual_nodes,
                          xyz_axis=xyz_axis,
                          colorbar=colorbar,
                          **dark_canvas_params)


  # Show all images.
  app.run()
