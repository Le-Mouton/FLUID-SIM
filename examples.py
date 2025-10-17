"""
Example usage of the fluid simulator.
Demonstrates how to create custom scenarios and configure parameters.
"""
import numpy as np
from fluid_simulator import FluidSimulator


def example_basic_usage():
    """Basic example of creating and running a simulation."""
    print("Example 1: Basic Usage")
    print("-" * 50)
    
    # Create simulator
    sim = FluidSimulator(width=10.0, height=10.0)
    
    # Add some particles
    sim.add_particle([5.0, 8.0], [0.0, 0.0], mass=1.0)
    sim.add_particle([5.0, 8.5], [0.0, 0.0], mass=1.0)
    sim.add_particle([5.5, 8.0], [0.0, 0.0], mass=1.0)
    
    print(f"Created simulator with {len(sim.particles)} particles")
    
    # Run simulation for 100 steps
    for i in range(100):
        sim.step()
    
    # Get results
    positions = sim.get_positions()
    velocities = sim.get_velocities()
    
    print(f"After 100 steps:")
    print(f"  Particle 0 position: {positions[0]}")
    print(f"  Particle 0 velocity: {velocities[0]}")
    print()


def example_custom_parameters():
    """Example of customizing simulation parameters."""
    print("Example 2: Custom Parameters")
    print("-" * 50)
    
    # Create simulator
    sim = FluidSimulator(width=20.0, height=15.0)
    
    # Customize physics parameters
    sim.smoothing_radius = 0.8  # Larger interaction radius
    sim.gas_constant = 3000.0   # Stiffer pressure
    sim.viscosity = 0.05        # More viscous (like honey)
    sim.gravity = np.array([0.0, -5.0])  # Weaker gravity
    
    print(f"Custom parameters:")
    print(f"  Smoothing radius: {sim.smoothing_radius}")
    print(f"  Gas constant: {sim.gas_constant}")
    print(f"  Viscosity: {sim.viscosity}")
    print(f"  Gravity: {sim.gravity}")
    print()


def example_custom_scenario():
    """Example of creating a custom particle arrangement."""
    print("Example 3: Custom Scenario - Circle of Particles")
    print("-" * 50)
    
    # Create simulator
    sim = FluidSimulator(width=10.0, height=10.0)
    
    # Create particles in a circle
    center = np.array([5.0, 5.0])
    radius = 2.0
    num_particles = 20
    
    for i in range(num_particles):
        angle = 2 * np.pi * i / num_particles
        position = center + radius * np.array([np.cos(angle), np.sin(angle)])
        
        # Give particles velocity towards center
        velocity = -0.5 * np.array([np.cos(angle), np.sin(angle)])
        
        sim.add_particle(position, velocity, mass=1.0)
    
    print(f"Created {len(sim.particles)} particles in a circle")
    
    # Run simulation
    for _ in range(50):
        sim.step()
    
    positions = sim.get_positions()
    avg_distance = np.mean(np.linalg.norm(positions - center, axis=1))
    print(f"After 50 steps, average distance from center: {avg_distance:.2f}")
    print()


def example_query_particle_info():
    """Example of querying particle information."""
    print("Example 4: Querying Particle Information")
    print("-" * 50)
    
    # Create simulator
    sim = FluidSimulator(width=10.0, height=10.0)
    
    # Add particles
    for i in range(5):
        sim.add_particle([2.0 + i * 0.3, 5.0], [0.0, 0.0], mass=1.0)
    
    # Run simulation
    for _ in range(50):
        sim.step()
    
    # Query particle properties
    for i, particle in enumerate(sim.particles):
        print(f"Particle {i}:")
        print(f"  Position: [{particle.position[0]:.2f}, {particle.position[1]:.2f}]")
        print(f"  Velocity: [{particle.velocity[0]:.2f}, {particle.velocity[1]:.2f}]")
        print(f"  Density: {particle.density:.2f} kg/m³")
        print(f"  Pressure: {particle.pressure:.2f} Pa")
    print()


if __name__ == '__main__':
    print("=" * 50)
    print("Fluid Simulator Usage Examples")
    print("=" * 50)
    print()
    
    example_basic_usage()
    example_custom_parameters()
    example_custom_scenario()
    example_query_particle_info()
    
    print("=" * 50)
    print("All examples completed successfully!")
    print("=" * 50)
