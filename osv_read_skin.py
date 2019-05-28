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

""" A utility function to read in skin files from the research: 'Optimal
Surface Voting': https://github.com/xinwucwp/osv.
"""

import numpy as np


class FaultCell(object):
  """ A class that contains fault attribute on each fault pixel,
  including pos (x,y,z), likelihood, strike and dip angle,
  slip vector(s1,s2,s3).
  Each object also can include its neighboring cell index, (above,
  below, left, right).
  """
  def __init__(self, pos=(0,0,0), likelihood=0.,
               strike=0., dip=0., slip=(0.,0.,0.)):
    self.pos = pos
    self.likelihood = likelihood
    self.strike = strike
    self.dip = dip
    self.slip = slip

    # The index of neighboring cells.
    self.above = None
    self.below = None
    self.left = None
    self.right = None


class FaultSkin(object):
  """ A class that corresponding to the data structure from each skin
  file. The get_vertices_and_faces() method will try to organize the
  FaultCell points within this FaultSkin object and returns an array
  of vertices and an array of face indexes, which can be used to build
  a triangle mesh.
  """
  def __init__(self, filename):
    self.f = open(filename, 'br')

    num_cells = self._read_int()
    # Build a list of all cells included.
    self.cells = []
    for i in range(num_cells):
      pos = (self._read_float(), self._read_float(), self._read_float())
      likelihood = self._read_float()
      strike = self._read_float()
      dip = self._read_float()
      slip = (self._read_float(), self._read_float(), self._read_float())

      cell = FaultCell(pos=pos, likelihood=likelihood,
                       strike=strike, dip=dip, slip=slip)
      self.cells.append(cell)

    # Get the neighboring cell index for each cell.
    for i in range(num_cells):
      above = self._read_int()
      if above<0: above = None
      below = self._read_int()
      if below<0: below = None
      left = self._read_int()
      if left<0: left = None
      right = self._read_int()
      if right<0: right = None
      self.cells[i].above = above
      self.cells[i].below = below
      self.cells[i].left = left
      self.cells[i].right = right

    self.f.close()

  def get_vertices_and_faces(self):
    """ Get an array of vertices corresponding to an indexed triangle mesh.
    """
    # Directly copy the cell position to vertices.
    vertices = []
    for cell in self.cells:
      vertices.append(cell.pos)
    vertices = np.array(vertices)

    # Walk through the cells, each 4 forms a pair of triangles.
    faces = []
    for i, cell in enumerate(self.cells):
      # Get the FaultCell to the right of current cell.
      if cell.right is not None: R = self.cells[cell.right]
      else: R = None
      # Get the FaultCell below the current cell.
      if cell.below is not None: B = self.cells[cell.below]
      else: B = None

      # First triangle: 0 - 2
      #                   \ |
      #                     1, facing outwards.
      if R is not None and R.below is not None:
        faces.append([i, R.below, cell.right])
      # Second triangle: 0
      #                  | \
      #                  1 - 2, also facing outwards.
      if B is not None and B.right is not None:
        faces.append([i, cell.below, B.right])
    faces = np.array(faces).astype(int)

    return vertices, faces

  def _read_float(self, endian='>'):
    return self._read_type(endian + 'f')

  def _read_int(self, endian='>'):
    return self._read_type(endian + 'i')

  def _read_type(self, format):
    from struct import unpack, calcsize
    return unpack(format, self.f.read(calcsize(format)))[0]
