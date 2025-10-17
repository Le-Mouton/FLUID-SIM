"""
Main script to run the fluid simulation with visualization.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from fluid_simulator import FluidSimulator


def create_dam_break_scenario(simulator):
    """
    Create a dam break scenario with fluid particles.
    
    Args:
        simulator: FluidSimulator instance
    """
    # Create a block of fluid particles on the left side
    spacing = 0.2
    for x in np.arange(0.5, 3.0, spacing):
        for y in np.arange(0.5, 7.0, spacing):
            # Add small random velocity for more realistic behavior
            velocity = np.random.randn(2) * 0.1
            simulator.add_particle([x, y], velocity, mass=1.0)


def create_drop_scenario(simulator):
    """
    Create a water drop scenario.
    
    Args:
        simulator: FluidSimulator instance
    """
    # Create a circular drop of fluid
    spacing = 0.2
    center = np.array([5.0, 7.0])
    radius = 1.5
    
    for x in np.arange(center[0] - radius, center[0] + radius, spacing):
        for y in np.arange(center[1] - radius, center[1] + radius, spacing):
            pos = np.array([x, y])
            if np.linalg.norm(pos - center) < radius:
                velocity = np.random.randn(2) * 0.1
                simulator.add_particle(pos, velocity, mass=1.0)


def run_simulation(scenario='dam_break', num_frames=500, steps_per_frame=5):
    """
    Run the fluid simulation with visualization.
    
    Args:
        scenario: 'dam_break' or 'drop'
        num_frames: number of frames to simulate
        steps_per_frame: simulation steps per frame
    """
    # Create simulator
    sim = FluidSimulator(width=10.0, height=10.0)
    
    # Set up scenario
    if scenario == 'dam_break':
        create_dam_break_scenario(sim)
        title = "Fluid Simulation - Dam Break"
    elif scenario == 'drop':
        create_drop_scenario(sim)
        title = "Fluid Simulation - Water Drop"
    else:
        print(f"Unknown scenario: {scenario}")
        return
    
    print(f"Simulating {len(sim.particles)} particles...")
    
    # Set up visualization
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(0, sim.width)
    ax.set_ylim(0, sim.height)
    ax.set_aspect('equal')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    
    # Initialize scatter plot
    positions = sim.get_positions()
    scatter = ax.scatter(positions[:, 0], positions[:, 1], 
                        c='blue', s=30, alpha=0.6)
    
    # Frame counter text
    frame_text = ax.text(0.02, 0.98, '', transform=ax.transAxes,
                        verticalalignment='top')
    
    def animate(frame):
        """Animation update function."""
        # Perform multiple simulation steps per frame
        for _ in range(steps_per_frame):
            sim.step()
        
        # Update visualization
        positions = sim.get_positions()
        scatter.set_offsets(positions)
        
        # Color particles by velocity magnitude
        velocities = sim.get_velocities()
        speeds = np.linalg.norm(velocities, axis=1)
        scatter.set_array(speeds)
        scatter.set_cmap('viridis')
        
        frame_text.set_text(f'Frame: {frame}/{num_frames}\nParticles: {len(sim.particles)}')
        
        return scatter, frame_text
    
    # Create animation
    anim = animation.FuncAnimation(fig, animate, frames=num_frames,
                                  interval=20, blit=True)
    
    # Add colorbar for velocity
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Speed (m/s)')
    
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    import sys
    
    # Parse command line arguments
    scenario = 'dam_break'
    if len(sys.argv) > 1:
        scenario = sys.argv[1]
    
    print("Fluid Simulation with Particle Interactions")
    print("=" * 50)
    print(f"Scenario: {scenario}")
    print("Close the window to exit the simulation.")
    print()
    
    run_simulation(scenario=scenario, num_frames=500, steps_per_frame=5)
