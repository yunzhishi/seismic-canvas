# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (C) 2019 Yunzhi Shi @ The University of Texas at Austin.
# All rights reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

""" A utility function to read in skin files from the research: 'Optimal
Surface Voting': https://github.com/xinwucwp/osv.
"""

from struct import unpack, calcsize
import numpy as np


class FaultCell(object):
  """ A class that contains fault attribute on each fault pixel,
  including pos (x,y,z), likelihood, strike and dip angle,
  slip vector(sx,sy,sz).
  Each object also can include its neighboring cell, (above, below,
  left, right).
  """
  def __init__(self, index, pos=(0,0,0), likelihood=0.,
               strike=0., dip=0., slip=(0.,0.,0.)):
    self.pos = pos
    self.likelihood = likelihood
    self.strike = strike
    self.dip = dip
    self.slip = slip

    # The index in the cell list of a skin.
    self.index = index

    # The neighboring cells.
    self.above = None
    self.below = None
    self.left = None
    self.right = None

  def smooth_strike(self):
    """ Smooth the strike angle value using neighboring cells.
    """
    L = self.left; R = self.right
    L_strike = 0.; R_strike = 0.
    scs = 0. # not sure what it means ...
    if L is not None:
      dy = self.pos[1] - L.pos[1]
      dx = self.pos[0] - L.pos[0]
      ds = np.sqrt(dy**2 + dx**2)
      L_strike = np.degrees(np.arccos(dx / ds))
      scs += 1
    if R is not None:
      dy = -self.pos[1] + R.pos[1]
      dx = -self.pos[0] + R.pos[0]
      ds = np.sqrt(dy**2 + dx**2)
      R_strike = np.degrees(np.arccos(dx / ds))
      scs += 1
    if scs > 0:
      self.strike = (L_strike + R_strike) / scs


class FaultSkin(object):
  """ A class that corresponding to the data structure from each skin
  file. The get_vertices_and_faces() method will try to organize the
  FaultCell points within this FaultSkin object and returns an array
  of vertices and an array of face indexes, which can be used to build
  a triangle mesh.
  """
  def __init__(self, filename):
    self.f = open(filename, 'br')

    num_cells = unpack('>i', self.f.read(calcsize('>i')))[0]

    # Read all cell parameters in chunk.
    fmt = '>{:d}f'.format(9 * num_cells) # 9 floats per cell
    cell_params = unpack(fmt, self.f.read(calcsize(fmt)))

    # Build a list of all cells included.
    self.cells = []
    for i in range(num_cells):
      param = cell_params[9*i: 9*(i+1)]
      pos = (param[2], param[1], param[0]) # reverse the zyx order to xyz
      likelihood = param[3]
      strike = param[4]
      dip = param[5]
      slip = (param[8], param[7], param[6]) # reverse the zyx order to xyz

      self.cells.append(FaultCell(i, pos=pos, likelihood=likelihood,
                                  strike=strike, dip=dip, slip=slip))

    # Read cell neighbor indexes in chunk.
    fmt = '>{:d}i'.format(4 * num_cells) # 4 neighbor indexes per cell
    cell_neighbors = unpack(fmt, self.f.read(calcsize(fmt)))

    # Get the neighboring cell index for each cell.
    for i in range(num_cells):
      # Neighbor above current cell.
      if cell_neighbors[4*i] >= 0:
        self.cells[i].above = self.cells[cell_neighbors[4*i]]
      # Neighbor below current cell.
      if cell_neighbors[4*i+1] >= 0:
        self.cells[i].below = self.cells[cell_neighbors[4*i+1]]
      # Neighbor to the left of current cell.
      if cell_neighbors[4*i+2] >= 0:
        self.cells[i].left = self.cells[cell_neighbors[4*i+2]]
      # Neighbor to the right of current cell.
      if cell_neighbors[4*i+3] >= 0:
        self.cells[i].right = self.cells[cell_neighbors[4*i+3]]

    self.f.close()

    # Smooth the strike angle on the skin.
    for cell in self.cells:
      cell.smooth_strike()

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
      R = cell.right
      if R is not None: RB = R.below
      # Get the FaultCell below the current cell.
      B = cell.below
      if B is not None: BR = B.right

      # First triangle: 0 - 2
      #                   \ |
      #                     1, facing outwards.
      if R and RB:
        faces.append([i, RB.index, R.index])
      # Second triangle: 0
      #                  | \
      #                  1 - 2, also facing outwards.
      if B and BR:
        faces.append([i, B.index, BR.index])
    faces = np.array(faces).astype(int)

    return vertices, faces

  def _read_float(self, endian='>'):
    return self._read_type(endian + 'f')

  def _read_int(self, endian='>'):
    return self._read_type(endian + 'i')

  def _read_type(self, format):
    from struct import unpack, calcsize
    return unpack(format, self.f.read(calcsize(format)))[0]
