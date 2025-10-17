"""
Spatial hashing for efficient neighbor particle detection.
"""
import numpy as np
from collections import defaultdict


class SpatialHash:
    """Spatial hash grid for efficient neighbor queries."""
    
    def __init__(self, cell_size):
        """
        Initialize spatial hash grid.
        
        Args:
            cell_size: size of each grid cell
        """
        self.cell_size = cell_size
        self.grid = defaultdict(list)
    
    def clear(self):
        """Clear the grid."""
        self.grid.clear()
    
    def _hash(self, position):
        """
        Compute grid cell coordinates for a position.
        
        Args:
            position: 2D numpy array [x, y]
            
        Returns:
            tuple of grid coordinates (i, j)
        """
        i = int(np.floor(position[0] / self.cell_size))
        j = int(np.floor(position[1] / self.cell_size))
        return (i, j)
    
    def insert(self, particle):
        """
        Insert a particle into the grid.
        
        Args:
            particle: Particle object to insert
        """
        cell = self._hash(particle.position)
        self.grid[cell].append(particle)
    
    def get_neighbors(self, position, radius):
        """
        Get all particles within radius of position.
        
        Args:
            position: 2D numpy array [x, y]
            radius: search radius
            
        Returns:
            list of particles within radius
        """
        neighbors = []
        cell = self._hash(position)
        
        # Check this cell and surrounding cells
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                neighbor_cell = (cell[0] + di, cell[1] + dj)
                if neighbor_cell in self.grid:
                    for particle in self.grid[neighbor_cell]:
                        dist = np.linalg.norm(particle.position - position)
                        if dist < radius:
                            neighbors.append(particle)
        
        return neighbors
