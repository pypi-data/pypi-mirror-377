#!/usr/bin/env python3
"""
Advanced Features Examples for PlotX
Demonstrates sophisticated visualization capabilities and techniques.
"""

import numpy as np
import sys
import os
from datetime import datetime, timedelta
import time

# Add src to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import plotxy
import plotxy.interaction3d as i3d


def financial_candlestick_example():
    """Advanced financial visualization with technical indicators."""
    print("💰 Creating advanced financial chart...")

    # Generate realistic OHLC data
    def generate_realistic_ohlc(days=200, start_price=100):
        """Generate realistic stock price data with trends and volatility."""
        dates = [datetime.now() - timedelta(days=days-i) for i in range(days)]

        # Base price movement with trend
        trend = np.linspace(0, 0.3, days)  # 30% upward trend over period
        volatility = 0.02 + 0.01 * np.sin(np.linspace(0, 4*np.pi, days))  # Variable volatility

        # Random walk with trend
        returns = np.random.normal(trend/days, volatility)
        prices = start_price * np.exp(np.cumsum(returns))

        # Generate OHLC from closes
        opens = prices * (1 + np.random.normal(0, 0.003, days))
        highs = np.maximum(opens, prices) * (1 + np.random.exponential(0.005, days))
        lows = np.minimum(opens, prices) * (1 - np.random.exponential(0.005, days))
        volume = np.random.lognormal(15, 0.5, days).astype(int)

        return dates, opens, highs, lows, prices, volume

    # Generate data
    dates, opens, highs, lows, closes, volume = generate_realistic_ohlc(150, 120)

    # Create advanced candlestick chart
    chart = plotxy.CandlestickChart(width=1400, height=1000)
    chart.plot(dates, opens, highs, lows, closes, volume)

    # Add technical indicators
    chart.add_moving_average(window=20, color='blue', linewidth=2, label='SMA 20')
    chart.add_moving_average(window=50, color='orange', linewidth=2, label='SMA 50')
    chart.add_exponential_moving_average(window=12, color='purple', linewidth=1.5, label='EMA 12')

    # Bollinger Bands
    chart.add_bollinger_bands(window=20, num_std=2, alpha=0.2, color='gray')

    # Volume analysis
    chart.add_volume_bars(alpha=0.4, bullish_color='green', bearish_color='red')
    chart.add_volume_sma(window=20, color='navy', linewidth=1)

    # Support and resistance
    chart.add_support_resistance_levels(window=20, min_touches=3)

    # Professional styling
    chart.set_title('Advanced Technical Analysis - AAPL', fontsize=18, fontweight='bold')
    chart.set_theme('financial')
    chart.add_legend(location='upper left')
    chart.add_grid(alpha=0.3)

    # Add annotations for key events
    chart.add_annotation(dates[50], highs[50], 'Breakout', fontsize=10,
                        arrow=True, arrowprops={'arrowstyle': '->', 'color': 'red'})

    chart.save('examples/outputs/advanced_candlestick.png', dpi=300)
    print("✓ Advanced candlestick chart saved")


def scientific_visualization_example():
    """Create scientific visualization with multiple datasets."""
    print("🔬 Creating scientific visualization...")

    # Simulate experimental data
    def simulate_experiment():
        """Simulate a physics experiment with measurement errors."""
        # Independent variable
        x = np.linspace(0, 10, 50)

        # Theoretical curve (exponential decay)
        y_theory = 100 * np.exp(-x/3)

        # Experimental data with noise
        y_experiment = y_theory + np.random.normal(0, 5, len(x))

        # Error bars (measurement uncertainty)
        errors = np.random.uniform(2, 8, len(x))

        return x, y_theory, y_experiment, errors

    x, y_theory, y_experiment, errors = simulate_experiment()

    # Create scientific plot
    chart = plotxy.LineChart(width=1000, height=700)

    # Plot theoretical curve
    chart.plot(x, y_theory, color='red', linewidth=2, linestyle='-', label='Theoretical')

    # Plot experimental data with error bars
    chart.errorbar(x, y_experiment, yerr=errors, color='blue', marker='o',
                  linestyle='none', capsize=5, label='Experimental')

    # Add fit line
    coeffs = np.polyfit(x, y_experiment, 2)  # Polynomial fit
    y_fit = np.polyval(coeffs, x)
    chart.plot(x, y_fit, color='green', linewidth=2, linestyle='--', label='Polynomial Fit')

    # Scientific styling
    chart.set_title('Radioactive Decay Experiment', fontsize=16)
    chart.set_labels('Time (hours)', 'Activity (counts/min)')
    chart.set_scale('linear', 'log')  # Semi-log plot
    chart.add_legend()
    chart.add_grid(True, which='both', alpha=0.3)

    # Add equation annotation
    equation = f'Fit: y = {coeffs[0]:.2f}x² + {coeffs[1]:.2f}x + {coeffs[2]:.2f}'
    chart.add_text(0.05, 0.95, equation, transform='axes', fontsize=12,
                  bbox={'boxstyle': 'round', 'facecolor': 'wheat', 'alpha': 0.8})

    chart.save('examples/outputs/scientific_plot.png', dpi=300)
    print("✓ Scientific plot saved")


def interactive_3d_scene_example():
    """Create complex interactive 3D scene."""
    print("🎮 Creating interactive 3D scene...")

    # Create scene
    scene = i3d.Scene3D()

    # Add various 3D objects
    objects = []

    # Central sphere
    center_sphere = i3d.Sphere(position=[0, 0, 0], radius=1.0, color='gold')
    objects.append(center_sphere)

    # Orbiting cubes
    for i in range(8):
        angle = i * 2 * np.pi / 8
        x = 3 * np.cos(angle)
        z = 3 * np.sin(angle)
        y = np.sin(2 * angle)

        cube = i3d.Cube(position=[x, y, z], size=0.5,
                       color=f'hsl({i*45}, 70%, 50%)')
        objects.append(cube)

    # Add connecting lines
    for i in range(8):
        start = objects[i+1].position
        end = [0, 0, 0]  # Center
        line = i3d.Line(start=start, end=end, color='white', width=2)
        objects.append(line)

    # Add all objects to scene
    scene.add_objects(objects)

    # Setup advanced camera
    camera = i3d.OrbitController(
        target=[0, 0, 0],
        distance=8.0,
        azimuth=45.0,
        elevation=30.0,
        min_distance=3.0,
        max_distance=20.0
    )
    scene.set_camera(camera)

    # Enable interaction
    scene.enable_selection(mode="multiple")
    scene.enable_manipulation(transforms=["translate", "rotate", "scale"])

    # Add lighting
    scene.add_directional_light(direction=[1, -1, -1], intensity=0.8)
    scene.add_ambient_light(intensity=0.3)
    scene.add_point_light(position=[5, 5, 5], intensity=0.6)

    # Animation
    animator = i3d.KeyFrameSystem()

    # Rotate central sphere
    sphere_anim = animator.create_animation("sphere_rotation")
    sphere_anim.add_keyframe(0.0, {"rotation": [0, 0, 0]})
    sphere_anim.add_keyframe(4.0, {"rotation": [0, 360, 0]})
    sphere_anim.set_loop(True)

    # Orbit camera
    camera_anim = i3d.CameraAnimator(camera)
    camera_anim.orbit_around_target(radius=8.0, duration=10.0, loops=-1)

    # Save snapshot
    scene.render_to_file('examples/outputs/interactive_3d_scene.png')
    print("✓ Interactive 3D scene saved")

    # Export scene description
    scene_data = {
        'objects': len(objects),
        'lighting': 'Directional + Ambient + Point',
        'camera': 'Orbit Controller',
        'interaction': 'Selection + Manipulation',
        'animation': 'Keyframe System'
    }

    with open('examples/outputs/3d_scene_description.txt', 'w') as f:
        f.write("3D Scene Configuration\n")
        f.write("=" * 25 + "\n")
        for key, value in scene_data.items():
            f.write(f"{key.capitalize()}: {value}\n")

    print("✓ Scene description saved")


def real_time_data_simulation():
    """Simulate real-time data streaming visualization."""
    print("⚡ Creating real-time data simulation...")

    # Setup streaming chart
    chart = plotxy.StreamingChart(width=1200, height=600, buffer_size=100)

    # Data generators
    def sensor_data_generator():
        """Generate realistic sensor data."""
        t = 0
        while t < 10:  # 10 seconds of data
            # Multiple sensor readings
            temperature = 20 + 5 * np.sin(t/2) + np.random.normal(0, 0.5)
            humidity = 60 + 10 * np.cos(t/3) + np.random.normal(0, 2)
            pressure = 1013 + 3 * np.sin(t/4) + np.random.normal(0, 1)

            yield t, temperature, humidity, pressure
            t += 0.1  # 10Hz sampling rate

    # Initialize chart
    chart.add_stream('Temperature', color='red', linewidth=2)
    chart.add_stream('Humidity', color='blue', linewidth=2)
    chart.add_stream('Pressure', color='green', linewidth=2)

    chart.set_title('Real-time Sensor Data')
    chart.set_labels('Time (s)', 'Sensor Values')
    chart.add_legend()

    # Simulate streaming
    frames = []
    for i, (t, temp, hum, press) in enumerate(sensor_data_generator()):
        chart.append_data('Temperature', t, temp)
        chart.append_data('Humidity', t, hum)
        chart.append_data('Pressure', t, press)

        # Save frames for animation
        if i % 10 == 0:  # Every second
            chart.save(f'examples/outputs/streaming_frame_{i//10:03d}.png')
            frames.append(f'streaming_frame_{i//10:03d}.png')

    print(f"✓ Generated {len(frames)} streaming frames")

    # Create summary chart
    chart.save('examples/outputs/real_time_final.png', dpi=300)
    print("✓ Real-time simulation saved")


def machine_learning_visualization():
    """Visualize machine learning model performance."""
    print("🤖 Creating ML visualization...")

    # Generate classification data
    def generate_classification_data():
        """Generate 2D classification dataset."""
        np.random.seed(42)
        n_samples = 500

        # Class 1: Circular cluster
        class1_r = np.random.normal(2, 0.5, n_samples//2)
        class1_theta = np.random.uniform(0, 2*np.pi, n_samples//2)
        class1_x = class1_r * np.cos(class1_theta)
        class1_y = class1_r * np.sin(class1_theta)

        # Class 2: Ring around class 1
        class2_r = np.random.normal(4, 0.3, n_samples//2)
        class2_theta = np.random.uniform(0, 2*np.pi, n_samples//2)
        class2_x = class2_r * np.cos(class2_theta)
        class2_y = class2_r * np.sin(class2_theta)

        return (np.concatenate([class1_x, class2_x]),
                np.concatenate([class1_y, class2_y]),
                np.concatenate([np.zeros(n_samples//2), np.ones(n_samples//2)]))

    x, y, labels = generate_classification_data()

    # Create decision boundary visualization
    chart = plotxy.ScatterChart(width=1000, height=800)

    # Plot data points
    class_colors = ['blue', 'red']
    for class_label in [0, 1]:
        mask = labels == class_label
        chart.scatter(x[mask], y[mask],
                     color=class_colors[int(class_label)],
                     alpha=0.6, s=50,
                     label=f'Class {int(class_label)}')

    # Create decision boundary (simple circular boundary)
    theta = np.linspace(0, 2*np.pi, 100)
    boundary_r = 3.0
    boundary_x = boundary_r * np.cos(theta)
    boundary_y = boundary_r * np.sin(theta)

    chart.plot(boundary_x, boundary_y, color='black', linewidth=3,
              linestyle='--', label='Decision Boundary')

    # Add confidence regions
    for radius in [2.5, 3.5]:
        conf_x = radius * np.cos(theta)
        conf_y = radius * np.sin(theta)
        chart.plot(conf_x, conf_y, color='gray', linewidth=1,
                  alpha=0.5, linestyle=':')

    chart.set_title('Machine Learning Classification Visualization')
    chart.set_labels('Feature 1', 'Feature 2')
    chart.add_legend()
    chart.add_grid(alpha=0.3)

    # Add performance metrics text
    accuracy = 0.92
    precision = 0.89
    recall = 0.94

    metrics_text = f'Model Performance:\nAccuracy: {accuracy:.2f}\nPrecision: {precision:.2f}\nRecall: {recall:.2f}'
    chart.add_text(0.02, 0.98, metrics_text, transform='axes',
                  fontsize=10, verticalalignment='top',
                  bbox={'boxstyle': 'round', 'facecolor': 'lightblue', 'alpha': 0.8})

    chart.save('examples/outputs/ml_classification.png', dpi=300)
    print("✓ ML visualization saved")


def network_graph_visualization():
    """Create network/graph visualization."""
    print("🕸️ Creating network graph...")

    # Generate network data
    def generate_network(n_nodes=30):
        """Generate random network with clustering."""
        np.random.seed(123)

        # Node positions using force-directed layout simulation
        positions = np.random.randn(n_nodes, 2) * 2

        # Create edges with distance-based probability
        edges = []
        for i in range(n_nodes):
            for j in range(i+1, n_nodes):
                distance = np.linalg.norm(positions[i] - positions[j])
                if distance < 2.5 or np.random.random() < 0.1:
                    edges.append((i, j))

        # Node properties
        node_sizes = np.random.uniform(50, 200, n_nodes)
        node_colors = np.random.randint(0, 5, n_nodes)

        return positions, edges, node_sizes, node_colors

    positions, edges, node_sizes, node_colors = generate_network()

    # Create network chart
    chart = plotxy.NetworkChart(width=1000, height=1000)

    # Add nodes
    chart.add_nodes(positions, sizes=node_sizes, colors=node_colors,
                   cmap='Set3', alpha=0.8)

    # Add edges
    for i, j in edges:
        chart.add_edge(positions[i], positions[j], color='gray',
                      alpha=0.6, linewidth=1)

    # Highlight important nodes (high degree)
    node_degrees = np.zeros(len(positions))
    for i, j in edges:
        node_degrees[i] += 1
        node_degrees[j] += 1

    # Find hub nodes (top 10% by degree)
    hub_threshold = np.percentile(node_degrees, 90)
    hub_nodes = np.where(node_degrees >= hub_threshold)[0]

    for hub in hub_nodes:
        chart.highlight_node(positions[hub], color='red', size=300, alpha=0.3)

    chart.set_title('Network Topology Visualization')
    chart.set_labels('X Position', 'Y Position')

    # Add network statistics
    n_nodes = len(positions)
    n_edges = len(edges)
    avg_degree = 2 * n_edges / n_nodes
    density = 2 * n_edges / (n_nodes * (n_nodes - 1))

    stats_text = f'Network Statistics:\nNodes: {n_nodes}\nEdges: {n_edges}\nAvg Degree: {avg_degree:.1f}\nDensity: {density:.3f}'
    chart.add_text(0.02, 0.98, stats_text, transform='axes',
                  fontsize=10, verticalalignment='top',
                  bbox={'boxstyle': 'round', 'facecolor': 'yellow', 'alpha': 0.8})

    chart.save('examples/outputs/network_graph.png', dpi=300)
    print("✓ Network visualization saved")


def geospatial_visualization():
    """Create geospatial data visualization."""
    print("🌍 Creating geospatial visualization...")

    # Generate sample geographic data
    def generate_geographic_data():
        """Generate sample geographic dataset."""
        np.random.seed(456)

        # Major cities (simplified coordinates)
        cities = {
            'New York': (40.7128, -74.0060),
            'Los Angeles': (34.0522, -118.2437),
            'Chicago': (41.8781, -87.6298),
            'Houston': (29.7604, -95.3698),
            'Phoenix': (33.4484, -112.0740),
            'Philadelphia': (39.9526, -75.1652),
            'San Antonio': (29.4241, -98.4936),
            'San Diego': (32.7157, -117.1611),
            'Dallas': (32.7767, -96.7970),
            'San Jose': (37.3382, -121.8863)
        }

        # Generate population and growth data
        populations = np.random.uniform(500, 8000, len(cities))  # In thousands
        growth_rates = np.random.normal(2.5, 1.5, len(cities))  # Percent per year

        return cities, populations, growth_rates

    cities, populations, growth_rates = generate_geographic_data()

    # Create map visualization
    chart = plotxy.MapChart(width=1200, height=800, projection='usa')

    # Plot cities
    lats, lons = zip(*cities.values())
    city_names = list(cities.keys())

    # Size by population, color by growth rate
    chart.scatter(lons, lats, s=populations/10, c=growth_rates,
                 cmap='RdYlBu', alpha=0.7, edgecolors='black')

    # Add city labels
    for i, city in enumerate(city_names):
        chart.annotate(city, (lons[i], lats[i]),
                      xytext=(5, 5), textcoords='offset points',
                      fontsize=8, fontweight='bold')

    # Add connections (flight routes simulation)
    major_hubs = ['New York', 'Los Angeles', 'Chicago']
    for hub in major_hubs:
        hub_coords = cities[hub]
        for city, coords in cities.items():
            if city != hub and np.random.random() < 0.4:
                chart.plot_great_circle(hub_coords, coords,
                                      color='red', alpha=0.3, linewidth=1)

    chart.set_title('US Cities: Population and Growth Analysis')
    chart.add_colorbar(label='Growth Rate (%/year)')

    # Add legend for population sizes
    legend_sizes = [1000, 5000, 8000]
    legend_labels = ['1M', '5M', '8M']
    chart.add_size_legend(legend_sizes, legend_labels, title='Population')

    chart.save('examples/outputs/geospatial_map.png', dpi=300)
    print("✓ Geospatial visualization saved")


def animation_sequence_example():
    """Create animation sequence."""
    print("🎬 Creating animation sequence...")

    # Animation parameters
    n_frames = 60
    duration = 4.0  # seconds

    # Create animated scatter plot
    for frame in range(n_frames):
        t = frame / n_frames * duration

        # Animated data
        n_points = 100
        theta = np.linspace(0, 4*np.pi, n_points) + t
        r = np.linspace(0.1, 3, n_points)

        x = r * np.cos(theta)
        y = r * np.sin(theta)
        colors = np.sin(theta + t) * 0.5 + 0.5

        # Create frame
        chart = plotxy.ScatterChart(width=800, height=800)
        chart.plot(x, y, c=colors, s=50, cmap='plasma', alpha=0.8)

        # Fixed limits for smooth animation
        chart.set_limits(xlim=(-3.5, 3.5), ylim=(-3.5, 3.5))
        chart.set_title(f'Animated Spiral - Frame {frame+1}/{n_frames}')
        chart.set_labels('X', 'Y')

        # Add time indicator
        chart.add_text(0.02, 0.98, f'Time: {t:.2f}s', transform='axes',
                      fontsize=12, verticalalignment='top',
                      bbox={'boxstyle': 'round', 'facecolor': 'white'})

        # Save frame
        chart.save(f'examples/outputs/animation_frame_{frame:03d}.png')

    print(f"✓ Generated {n_frames} animation frames")

    # Create animation instructions
    with open('examples/outputs/animation_instructions.txt', 'w') as f:
        f.write("Animation Creation Instructions\n")
        f.write("=" * 32 + "\n\n")
        f.write("To create animation video, use FFmpeg:\n")
        f.write("ffmpeg -r 15 -i animation_frame_%03d.png -c:v libx264 -pix_fmt yuv420p animation.mp4\n\n")
        f.write("To create GIF:\n")
        f.write("ffmpeg -r 15 -i animation_frame_%03d.png -vf palettegen palette.png\n")
        f.write("ffmpeg -r 15 -i animation_frame_%03d.png -i palette.png -lavfi paletteuse animation.gif\n")

    print("✓ Animation instructions saved")


def create_output_directory():
    """Ensure output directory exists."""
    output_dir = 'examples/outputs'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Created output directory: {output_dir}")


def main():
    """Run all advanced examples."""
    print("🚀 PlotX Advanced Features Examples")
    print("=" * 50)

    # Create output directory
    create_output_directory()

    try:
        # Run all advanced examples
        financial_candlestick_example()
        scientific_visualization_example()
        interactive_3d_scene_example()
        real_time_data_simulation()
        machine_learning_visualization()
        network_graph_visualization()
        geospatial_visualization()
        animation_sequence_example()

        print("\n🎉 All advanced examples completed successfully!")
        print("\nGenerated files:")
        print("  💰 examples/outputs/advanced_candlestick.png")
        print("  🔬 examples/outputs/scientific_plot.png")
        print("  🎮 examples/outputs/interactive_3d_scene.png")
        print("  ⚡ examples/outputs/real_time_final.png")
        print("  🤖 examples/outputs/ml_classification.png")
        print("  🕸️ examples/outputs/network_graph.png")
        print("  🌍 examples/outputs/geospatial_map.png")
        print("  🎬 examples/outputs/animation_frame_*.png (60 frames)")

        print(f"\n✅ Advanced features demonstration complete!")
        print(f"🚀 PlotX is ready for professional use!")

    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()