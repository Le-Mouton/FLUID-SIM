"""
Particle class for fluid simulation.
Represents individual fluid particles with physical properties.
"""
import numpy as np


class Particle:
    """Represents a single fluid particle with physical properties."""
    
    def __init__(self, position, velocity, mass=1.0):
        """
        Initialize a particle.
        
        Args:
            position: 2D numpy array [x, y]
            velocity: 2D numpy array [vx, vy]
            mass: particle mass (default 1.0)
        """
        self.position = np.array(position, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)
        self.mass = mass
        self.density = 0.0
        self.pressure = 0.0
        self.force = np.zeros(2, dtype=np.float64)
    
    def update(self, dt):
        """
        Update particle position and velocity based on forces.
        
        Args:
            dt: time step
        """
        # Update velocity from acceleration (F = ma, so a = F/m)
        acceleration = self.force / self.mass
        self.velocity += acceleration * dt
        
        # Update position from velocity
        self.position += self.velocity * dt
        
        # Reset force for next iteration
        self.force = np.zeros(2, dtype=np.float64)
