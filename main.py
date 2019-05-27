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

""" Simple demonstration of the new 3D visualization tool for Madagascar.
The program displays x-, y-, z- slices of a numpy array in 3D, allows user
to interactively drag the slices, includes useful features such as colorbar
and axis legend, and can output the figure to .png file with various resolution.
"""

from seismic_canvas import (SeismicCanvas, volume_slices, XYZAxis, Colorbar)

import vispy
vispy.use(app='glfw')


if __name__ == '__main__':

  # Test 1: seismic image data.
  import numpy as np
  # 1. F3 seismic
  # vol1 = np.fromfile('./F3_seismic.dat', '>f4').reshape(420, 400, 100)
  vol1 = np.memmap('./F3_seismic.dat', dtype='>f4',
                   mode='r', shape=(420, 400, 100))
  # 2. F3 planarity
  # vol2 = np.fromfile('./F3_planarity.dat', '>f4').reshape(420, 400, 100)
  vol2 = np.memmap('./F3_planarity.dat', dtype='>f4',
                   mode='r', shape=(420, 400, 100))
  # 3. Costa Rica seismic
  # volume = np.fromfile('./CostaRica_seismic.dat', '>f4').reshape(825, 920, 210)
  # volume = np.memmap('./CostaRica_seismic.dat', dtype='>f4',
  #                    mode='r', shape=(825, 920, 210))
  # 4. SEAM velocity
  # volume = np.fromfile('./SEAM_seismic.dat', np.single).reshape(1169, 1002, 751)
  # volume = np.memmap('./SEAM_seismic.dat', dtype=np.single,
  #                    mode='r', shape=(1169, 1002, 751))

  # Colormaps.
  from vispy.color import get_colormap, Colormap
  # cmap='grays'; clim=(-2, 2)
  cmap=get_colormap('fire')
  n_colors=128; alphas = np.linspace(0, 1, n_colors);
  rgba = np.array([cmap.map(x) for x in alphas]); rgba[:,-1] = alphas;
  cmap = Colormap(rgba)
  clim=(0.25, 1.0)
  # cmap = 'viridis'; clim=(1, 5)
  # Preprocessing function.
  def preproc_func(array): # preprocessing for planarity
    import numpy as np
    return 1 - np.power(array, 8)
  # Get visual nodes ready.
  visual_nodes = volume_slices([vol1, vol2],
    cmaps=['grays', cmap], clims=[(-2,2), clim],
    preproc_funcs=[None, preproc_func],
    x_pos=32, y_pos=25, z_pos=93)
    # x_pos=[370, 170, 570, 770], y_pos=810, z_pos=120)
    # x_pos=[300, 600, 900], y_pos=500, z_pos=700)
  xyz_axis = XYZAxis()
  colorbar = Colorbar(cmap=cmap, clim=clim)


  # # Test 2: brain CT data.
  # import numpy as np
  # from vispy import io
  # volume = np.load(io.load_data_file('brain/mri.npz'))['data']
  # volume = volume.transpose(2, 0, 1)[:, :, ::-1]

  # visual_nodes = volume_slices(volume,
  #   x_pos=100, y_pos=128, z_pos=30,
  #   seismic_coord_system=False)
  # xyz_axis = XYZAxis(seismic_coord_system=False)
  # colorbar = Colorbar(cmap='grays', clim=(volume.min(), volume.max()))


  # Run the canvas.
  canvas = SeismicCanvas(visual_nodes=visual_nodes,
                         xyz_axis=xyz_axis,
                         colorbar=colorbar,
                         axis_scales=(1, 1,
                           0.3*max(vol1.shape[:2])/vol1.shape[2]),
                         # Manual camera setting below.
                         # auto_range=False,
                         # scale_factor=972.794,
                         # center=(434.46, 545.63, 10.26),
                         fov=30,
                         elevation=36,
                         azimuth=45,
                         )
  # canvas.measure_fps()
  canvas.app.run()
