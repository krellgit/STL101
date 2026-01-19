#!/usr/bin/env python3
"""
Simple Wire Duct for Cable Tray
Matches reference cable channel design - simple rectangular U-channel

Features:
- Simple U-shaped channel (rectangular trough)
- Matches cable tray slot dimensions (25mm x 20mm)
- Flat mounting base with 2 screw holes
- Optional ribbed texture on exterior
"""

import trimesh
import numpy as np

# ============================================
# Parameters
# ============================================

# Channel dimensions - match cable tray slot
CHANNEL_WIDTH = 25.0        # mm (inner width - matches CABLE_SLOT_WIDTH)
CHANNEL_HEIGHT = 20.0       # mm (inner height - matches CABLE_SLOT_HEIGHT)
CHANNEL_LENGTH = 200.0      # mm (segment length)

# Wall thickness
WALL_THICKNESS = 2.5        # mm (walls and bottom)

# Mounting base (extends beyond channel for screw clearance)
BASE_EXTENSION = 5.0        # mm (extra width on each side)
# Total base width = CHANNEL_WIDTH + 2*WALL_THICKNESS + 2*BASE_EXTENSION

# Screw holes
SCREW_HOLE_DIA = 4.0        # mm (#8 wood screws)
SCREW_COUNTERSINK_DIA = 8.0 # mm
SCREW_COUNTERSINK_DEPTH = 2.0  # mm
SCREW_INSET_FROM_END = 20.0    # mm (distance from each end)

# Ribs (optional texture)
ADD_RIBS = True
RIB_SPACING = 10.0          # mm (center-to-center)
RIB_WIDTH = 1.5             # mm
RIB_DEPTH = 0.8             # mm (how far ribs protrude)

# ============================================
# Helper functions
# ============================================

def create_box(width, height, depth, x=0, y=0, z=0):
    """Create a box mesh."""
    box = trimesh.creation.box(extents=[width, height, depth])
    box.apply_translation([x + width/2, y + height/2, z + depth/2])
    return box

def create_cylinder(radius, height, x=0, y=0, z=0, segments=32):
    """Create a cylinder mesh."""
    cyl = trimesh.creation.cylinder(radius=radius, height=height, sections=segments)
    cyl.apply_translation([x, y, z + height/2])
    return cyl

def generate_channel_body():
    """Generate simple U-shaped channel with flat mounting base."""

    # Calculate dimensions
    outer_width = CHANNEL_WIDTH + 2 * WALL_THICKNESS
    outer_height = CHANNEL_HEIGHT + WALL_THICKNESS  # Bottom wall
    base_width = outer_width + 2 * BASE_EXTENSION

    print(f"=== Simple U-Channel Wire Duct ===")
    print(f"Inner channel: {CHANNEL_WIDTH}mm W x {CHANNEL_HEIGHT}mm H")
    print(f"Outer dimensions: {outer_width}mm W x {outer_height}mm H")
    print(f"Mounting base: {base_width}mm W x {WALL_THICKNESS}mm thick")
    print(f"Length: {CHANNEL_LENGTH}mm\n")

    parts = []

    # Mounting base (wider than channel)
    base = create_box(
        base_width,
        CHANNEL_LENGTH,
        WALL_THICKNESS,
        -BASE_EXTENSION,  # Extends beyond channel walls
        0,
        0
    )
    parts.append(base)

    # Channel outer shell
    outer = create_box(
        outer_width,
        CHANNEL_LENGTH,
        outer_height,
        0, 0, WALL_THICKNESS
    )
    parts.append(outer)

    # Combine base and channel
    print("Creating channel body...")
    body = parts[0]
    for part in parts[1:]:
        try:
            body = trimesh.boolean.union([body, part], engine='manifold')
        except:
            body = trimesh.util.concatenate([body, part])

    # Create inner cavity (hollow out the channel)
    inner_cavity = create_box(
        CHANNEL_WIDTH,
        CHANNEL_LENGTH + 2,  # Extra length for clean cut
        CHANNEL_HEIGHT + 1,  # Extends above top to create opening
        WALL_THICKNESS,
        -1,
        WALL_THICKNESS * 2  # Start above bottom wall
    )

    # Subtract cavity
    print("Hollowing channel...")
    try:
        body = trimesh.boolean.difference([body, inner_cavity], engine='manifold')
    except Exception as e:
        print(f"Warning: Cavity subtraction failed: {e}")

    return body

def add_ribs(body):
    """Add ribbed texture pattern to exterior sides."""
    if not ADD_RIBS:
        return body

    print(f"Adding ribs (spacing: {RIB_SPACING}mm)...")

    num_ribs = int(CHANNEL_LENGTH / RIB_SPACING)
    outer_width = CHANNEL_WIDTH + 2 * WALL_THICKNESS

    for i in range(1, num_ribs):  # Skip first and last positions
        y_pos = i * RIB_SPACING

        # Left side rib
        left_rib = create_box(
            RIB_DEPTH,
            RIB_WIDTH,
            CHANNEL_HEIGHT,
            -RIB_DEPTH,  # Protrude outward from left wall
            y_pos - RIB_WIDTH/2,
            WALL_THICKNESS
        )

        # Right side rib
        right_rib = create_box(
            RIB_DEPTH,
            RIB_WIDTH,
            CHANNEL_HEIGHT,
            outer_width,  # Protrude outward from right wall
            y_pos - RIB_WIDTH/2,
            WALL_THICKNESS
        )

        # Add ribs
        try:
            body = trimesh.boolean.union([body, left_rib], engine='manifold')
            body = trimesh.boolean.union([body, right_rib], engine='manifold')
        except:
            pass

    return body

def add_screw_holes(body):
    """Add 2 screw holes (one on each end, 20mm from ends)."""

    print(f"\nAdding screw holes:")
    print(f"  2 holes, {SCREW_INSET_FROM_END}mm from each end")
    print(f"  Hole: {SCREW_HOLE_DIA}mm dia, Countersink: {SCREW_COUNTERSINK_DIA}mm dia")

    hole_y_positions = [
        SCREW_INSET_FROM_END,
        CHANNEL_LENGTH - SCREW_INSET_FROM_END
    ]

    # X position (center of channel)
    hole_x = CHANNEL_WIDTH / 2 + WALL_THICKNESS

    # Z position (through base from bottom)
    hole_z_bottom = -0.5

    for i, y_pos in enumerate(hole_y_positions):
        # Screw shaft
        shaft = create_cylinder(
            SCREW_HOLE_DIA / 2,
            WALL_THICKNESS + 1,
            hole_x, y_pos, hole_z_bottom
        )

        # Countersink
        countersink = create_cylinder(
            SCREW_COUNTERSINK_DIA / 2,
            SCREW_COUNTERSINK_DEPTH + 0.5,
            hole_x, y_pos, hole_z_bottom
        )

        # Combine and subtract
        try:
            hole = trimesh.boolean.union([shaft, countersink], engine='manifold')
            body = trimesh.boolean.difference([body, hole], engine='manifold')
            print(f"  Hole {i+1} at Y={y_pos:.1f}mm")
        except Exception as e:
            print(f"  Warning: Hole {i+1} failed: {e}")

    return body

def generate_wire_duct():
    """Generate complete wire duct."""

    print("\n=== Generating Wire Duct ===\n")

    # Create channel body
    duct = generate_channel_body()

    # Add ribs
    if ADD_RIBS:
        duct = add_ribs(duct)

    # Add screw holes
    duct = add_screw_holes(duct)

    # Validate
    print(f"\nMesh validation:")
    print(f"  Watertight: {duct.is_watertight}")
    print(f"  Valid volume: {duct.is_volume}")

    if not duct.is_watertight:
        print("  Attempting repair...")
        duct.fill_holes()

    return duct

def main():
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Generate
    duct = generate_wire_duct()

    # Info
    bounds = duct.bounds
    size = bounds[1] - bounds[0]
    print(f"\nFinal dimensions: {size[0]:.1f}mm W x {size[1]:.1f}mm L x {size[2]:.1f}mm H")

    # Export
    output_path = os.path.join(script_dir, "wire_duct_simple.stl")
    duct.export(output_path)
    print(f"\nSTL exported to: {output_path}")

    print("\n" + "="*60)
    print("DESIGN:")
    print("="*60)
    print(f"- Simple U-shaped rectangular channel")
    print(f"- Inner dimensions: {CHANNEL_WIDTH}mm x {CHANNEL_HEIGHT}mm (matches cable tray slots)")
    print(f"- Wall thickness: {WALL_THICKNESS}mm")
    print(f"- 2 screw holes: {SCREW_INSET_FROM_END}mm from each end")
    print(f"- Ribs: {'Yes' if ADD_RIBS else 'No'}")
    print("="*60)
    print("\nASSEMBLY:")
    print("1. Align duct with cable tray slot opening")
    print("2. Attach with 2x #8 wood screws")
    print("3. Insert cables through open top")
    print("4. Print multiple segments for longer runs")
    print("="*60)

if __name__ == "__main__":
    main()
