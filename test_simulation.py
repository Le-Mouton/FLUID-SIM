"""
Test script to verify the fluid simulation and generate a sample output.
"""
import numpy as np
import matplotlib.pyplot as plt
from fluid_simulator import FluidSimulator


def test_simulation():
    """Run a test simulation and save visualization."""
    print("Running fluid simulation test...")
    
    # Create simulator
    sim = FluidSimulator(width=10.0, height=10.0)
    
    # Create a dam break scenario with fewer particles for testing
    spacing = 0.3
    particle_count = 0
    for x in np.arange(0.5, 3.0, spacing):
        for y in np.arange(0.5, 5.0, spacing):
            velocity = np.random.randn(2) * 0.1
            sim.add_particle([x, y], velocity, mass=1.0)
            particle_count += 1
    
    print(f"Created {particle_count} particles")
    
    # Create figure for multiple frames
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Fluid Simulation - Dam Break Evolution', fontsize=16)
    
    frames = [0, 20, 40, 60, 80, 100]
    
    for idx, (ax, target_frame) in enumerate(zip(axes.flat, frames)):
        # Run simulation to target frame
        current_frame = 0 if idx == 0 else frames[idx - 1]
        steps_to_run = (target_frame - current_frame) * 5
        
        for _ in range(steps_to_run):
            sim.step()
        
        # Get positions and velocities
        positions = sim.get_positions()
        velocities = sim.get_velocities()
        speeds = np.linalg.norm(velocities, axis=1)
        
        # Plot
        scatter = ax.scatter(positions[:, 0], positions[:, 1], 
                           c=speeds, s=30, alpha=0.6, cmap='viridis')
        ax.set_xlim(0, sim.width)
        ax.set_ylim(0, sim.height)
        ax.set_aspect('equal')
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_title(f'Frame {target_frame} (t={target_frame*5*sim.dt:.3f}s)')
        ax.grid(True, alpha=0.3)
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Speed (m/s)')
        
        print(f"Frame {target_frame}: {len(positions)} particles, "
              f"avg speed = {speeds.mean():.3f} m/s")
    
    plt.tight_layout()
    plt.savefig('/tmp/fluid_simulation_test.png', dpi=150, bbox_inches='tight')
    print(f"\nVisualization saved to /tmp/fluid_simulation_test.png")
    plt.close()
    
    # Verify simulation results
    print("\nSimulation Statistics:")
    print(f"  Total particles: {len(sim.particles)}")
    print(f"  Position X range: [{positions[:, 0].min():.2f}, {positions[:, 0].max():.2f}]")
    print(f"  Position Y range: [{positions[:, 1].min():.2f}, {positions[:, 1].max():.2f}]")
    print(f"  Speed range: [{speeds.min():.3f}, {speeds.max():.3f}] m/s")
    print(f"  Average density: {np.mean([p.density for p in sim.particles]):.2f} kg/m³")
    
    # Check that particles stay within bounds
    assert positions[:, 0].min() >= 0, "Particles escaped left boundary"
    assert positions[:, 0].max() <= sim.width, "Particles escaped right boundary"
    assert positions[:, 1].min() >= 0, "Particles escaped bottom boundary"
    assert positions[:, 1].max() <= sim.height, "Particles escaped top boundary"
    
    print("\n✓ All tests passed!")
    return True


if __name__ == '__main__':
    test_simulation()
