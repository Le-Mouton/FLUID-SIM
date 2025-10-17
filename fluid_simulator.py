"""
Fluid simulator using Smoothed Particle Hydrodynamics (SPH).
"""
import numpy as np
from particle import Particle
from spatial_hash import SpatialHash


class FluidSimulator:
    """Simulates fluid dynamics using particle-based methods."""
    
    def __init__(self, width=10.0, height=10.0):
        """
        Initialize fluid simulator.
        
        Args:
            width: simulation domain width
            height: simulation domain height
        """
        self.width = width
        self.height = height
        self.particles = []
        
        # SPH parameters
        self.smoothing_radius = 0.5
        self.rest_density = 1000.0
        self.gas_constant = 2000.0
        self.viscosity = 0.018
        self.gravity = np.array([0.0, -9.81])
        
        # Spatial hashing for efficiency
        self.spatial_hash = SpatialHash(self.smoothing_radius)
        
        # Time step
        self.dt = 0.001
    
    def add_particle(self, position, velocity, mass=1.0):
        """
        Add a particle to the simulation.
        
        Args:
            position: 2D array [x, y]
            velocity: 2D array [vx, vy]
            mass: particle mass
        """
        particle = Particle(position, velocity, mass)
        self.particles.append(particle)
    
    def _kernel(self, r, h):
        """
        Poly6 smoothing kernel for SPH.
        
        Args:
            r: distance between particles
            h: smoothing radius
            
        Returns:
            kernel value
        """
        if r >= h:
            return 0.0
        
        coeff = 315.0 / (64.0 * np.pi * h**9)
        return coeff * (h**2 - r**2)**3
    
    def _kernel_gradient(self, r_vec, r, h):
        """
        Gradient of Spiky kernel for pressure forces.
        
        Args:
            r_vec: vector between particles
            r: distance between particles
            h: smoothing radius
            
        Returns:
            gradient vector
        """
        if r >= h or r < 1e-6:
            return np.zeros(2)
        
        coeff = -45.0 / (np.pi * h**6)
        return coeff * (h - r)**2 * r_vec / r
    
    def _kernel_laplacian(self, r, h):
        """
        Laplacian of viscosity kernel for viscosity forces.
        
        Args:
            r: distance between particles
            h: smoothing radius
            
        Returns:
            laplacian value
        """
        if r >= h:
            return 0.0
        
        coeff = 45.0 / (np.pi * h**6)
        return coeff * (h - r)
    
    def _compute_density_pressure(self):
        """Compute density and pressure for all particles."""
        for particle in self.particles:
            density = 0.0
            neighbors = self.spatial_hash.get_neighbors(
                particle.position, self.smoothing_radius
            )
            
            for neighbor in neighbors:
                r = np.linalg.norm(particle.position - neighbor.position)
                density += neighbor.mass * self._kernel(r, self.smoothing_radius)
            
            particle.density = max(density, self.rest_density)
            particle.pressure = self.gas_constant * (particle.density - self.rest_density)
    
    def _compute_forces(self):
        """Compute forces for all particles."""
        for particle in self.particles:
            pressure_force = np.zeros(2)
            viscosity_force = np.zeros(2)
            
            neighbors = self.spatial_hash.get_neighbors(
                particle.position, self.smoothing_radius
            )
            
            for neighbor in neighbors:
                if neighbor is particle:
                    continue
                
                r_vec = particle.position - neighbor.position
                r = np.linalg.norm(r_vec)
                
                if r < 1e-6:
                    continue
                
                # Pressure force
                pressure_grad = self._kernel_gradient(r_vec, r, self.smoothing_radius)
                pressure_force -= neighbor.mass * (
                    (particle.pressure + neighbor.pressure) / (2.0 * neighbor.density)
                ) * pressure_grad
                
                # Viscosity force
                velocity_diff = neighbor.velocity - particle.velocity
                viscosity_force += neighbor.mass * (
                    velocity_diff / neighbor.density
                ) * self._kernel_laplacian(r, self.smoothing_radius)
            
            viscosity_force *= self.viscosity
            
            # Total force = pressure + viscosity + gravity
            particle.force = (
                pressure_force + 
                viscosity_force + 
                particle.mass * self.gravity
            )
    
    def _handle_boundaries(self):
        """Handle particle collisions with boundaries."""
        damping = 0.5
        
        for particle in self.particles:
            # Bottom boundary
            if particle.position[1] < 0:
                particle.position[1] = 0
                particle.velocity[1] *= -damping
            
            # Top boundary
            if particle.position[1] > self.height:
                particle.position[1] = self.height
                particle.velocity[1] *= -damping
            
            # Left boundary
            if particle.position[0] < 0:
                particle.position[0] = 0
                particle.velocity[0] *= -damping
            
            # Right boundary
            if particle.position[0] > self.width:
                particle.position[0] = self.width
                particle.velocity[0] *= -damping
    
    def step(self):
        """Perform one simulation step."""
        # Build spatial hash
        self.spatial_hash.clear()
        for particle in self.particles:
            self.spatial_hash.insert(particle)
        
        # Compute densities and pressures
        self._compute_density_pressure()
        
        # Compute forces
        self._compute_forces()
        
        # Update particles
        for particle in self.particles:
            particle.update(self.dt)
        
        # Handle boundary collisions
        self._handle_boundaries()
    
    def get_positions(self):
        """
        Get positions of all particles.
        
        Returns:
            numpy array of shape (n_particles, 2)
        """
        return np.array([p.position for p in self.particles])
    
    def get_velocities(self):
        """
        Get velocities of all particles.
        
        Returns:
            numpy array of shape (n_particles, 2)
        """
        return np.array([p.velocity for p in self.particles])
