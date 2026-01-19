#!/usr/bin/env python3
"""
Wire Duct for Cable Tray - Screw Mount Version
Generates STL file for 3D printing

Features:
- Matches cable tray slot dimensions (25mm x 20mm)
- U-channel profile with internal lip to retain cables
- Flat mounting base for screw attachment underneath desk
- 2 screw holes (one on each end, 20mm from ends)
"""

import trimesh
import numpy as np

# ============================================
# Parameters - adjust as needed
# ============================================

# Duct dimensions - match cable tray slot
DUCT_WIDTH = 25.0           # mm (matches CABLE_SLOT_WIDTH)
DUCT_HEIGHT = 20.0          # mm (matches CABLE_SLOT_HEIGHT)
DUCT_LENGTH = 200.0         # mm (duct segment length)

# Wall thickness
WALL_THICKNESS = 2.0        # mm (side and bottom walls)

# Mounting base (flat platform for screwing to desk)
BASE_WIDTH = 35.0           # mm (wider than duct for stability)
BASE_THICKNESS = 3.0        # mm (mounting platform thickness)

# Internal cable retention lip
LIP_DEPTH = 3.0             # mm (how far lip extends inward)
LIP_THICKNESS = 1.5         # mm (thickness of retention lip)
LIP_HEIGHT_FROM_TOP = 5.0   # mm (distance from top opening)

# Screw holes
SCREW_HOLE_DIA = 4.0        # mm (for #8 wood screws)
SCREW_COUNTERSINK_DIA = 8.0 # mm (countersink diameter)
SCREW_COUNTERSINK_DEPTH = 2.5  # mm (countersink depth)
SCREW_INSET_FROM_END = 20.0    # mm (distance from each end)

# Corner radius for smooth edges
CORNER_RADIUS = 2.0         # mm

# ============================================
# Helper functions
# ============================================

def create_box(width, height, depth, x=0, y=0, z=0):
    """Create a box mesh at the specified position."""
    box = trimesh.creation.box(extents=[width, height, depth])
    box.apply_translation([x + width/2, y + height/2, z + depth/2])
    return box

def create_cylinder(radius, height, x=0, y=0, z=0, segments=32):
    """Create a cylinder mesh at the specified position."""
    cyl = trimesh.creation.cylinder(radius=radius, height=height, sections=segments)
    cyl.apply_translation([x, y, z + height/2])
    return cyl

def create_rounded_box(width, length, height, radius, x=0, y=0, z=0):
    """Create a box with rounded vertical edges."""
    # Simplified - create regular box
    # For production, would add proper corner rounding
    return create_box(width, length, height, x, y, z)

# ============================================
# Main generation functions
# ============================================

def generate_duct_body():
    """Generate the main wire duct channel with mounting base."""

    print(f"=== Wire Duct with Screw Mount ===")
    print(f"Duct opening: {DUCT_WIDTH}mm W x {DUCT_HEIGHT}mm H")
    print(f"Duct length: {DUCT_LENGTH}mm")
    print(f"Mounting base: {BASE_WIDTH}mm W x {BASE_THICKNESS}mm thick")

    parts = []

    # Mounting base (flat platform at bottom)
    base = create_box(
        BASE_WIDTH,
        DUCT_LENGTH,
        BASE_THICKNESS,
        (DUCT_WIDTH - BASE_WIDTH) / 2,  # Center under duct
        0,
        -BASE_THICKNESS
    )
    parts.append(base)

    # Outer shell of U-channel
    outer = create_box(
        DUCT_WIDTH,
        DUCT_LENGTH,
        DUCT_HEIGHT,
        0, 0, 0
    )
    parts.append(outer)

    # Combine base and outer shell
    print("Combining base and channel...")
    body = parts[0]
    for part in parts[1:]:
        try:
            body = trimesh.boolean.union([body, part], engine='manifold')
        except:
            body = trimesh.util.concatenate([body, part])

    # Create inner cavity (U-shaped - open at top)
    inner_width = DUCT_WIDTH - 2 * WALL_THICKNESS
    inner_height = DUCT_HEIGHT + 1  # Extends above top to create opening
    inner_length = DUCT_LENGTH + 2  # Extra for clean cut

    inner = create_box(
        inner_width,
        inner_length,
        inner_height,
        WALL_THICKNESS,
        -1,
        WALL_THICKNESS  # Bottom wall remains
    )

    # Subtract inner cavity
    print("Creating U-channel cavity...")
    try:
        body = trimesh.boolean.difference([body, inner], engine='manifold')
    except Exception as e:
        print(f"Cavity subtraction failed: {e}")

    # Add internal cable retention lip
    # Lip extends inward from top of side walls
    lip_z = DUCT_HEIGHT - LIP_HEIGHT_FROM_TOP

    # Left lip
    left_lip = create_box(
        LIP_DEPTH,
        DUCT_LENGTH,
        LIP_THICKNESS,
        WALL_THICKNESS,  # Start at inner wall surface
        0,
        lip_z - LIP_THICKNESS/2
    )

    # Right lip
    right_lip = create_box(
        LIP_DEPTH,
        DUCT_LENGTH,
        LIP_THICKNESS,
        DUCT_WIDTH - WALL_THICKNESS - LIP_DEPTH,  # From right inner wall
        0,
        lip_z - LIP_THICKNESS/2
    )

    # Add lips to body
    print("Adding cable retention lips...")
    try:
        body = trimesh.boolean.union([body, left_lip], engine='manifold')
        body = trimesh.boolean.union([body, right_lip], engine='manifold')
    except Exception as e:
        print(f"Lip addition failed: {e}")

    return body

def add_screw_holes(body):
    """Add screw holes to the mounting base (2 holes, one on each end)."""

    print(f"\nAdding screw holes:")
    print(f"  2 holes, {SCREW_INSET_FROM_END}mm from each end")
    print(f"  Hole: {SCREW_HOLE_DIA}mm dia")
    print(f"  Countersink: {SCREW_COUNTERSINK_DIA}mm dia x {SCREW_COUNTERSINK_DEPTH}mm deep")

    # Screw hole positions (Y coordinates along length)
    hole_y_positions = [
        SCREW_INSET_FROM_END,                      # Near front end
        DUCT_LENGTH - SCREW_INSET_FROM_END         # Near back end
    ]

    # X position (center of mounting base)
    hole_x = DUCT_WIDTH / 2

    # Z position (through mounting base from bottom)
    hole_z_bottom = -BASE_THICKNESS - 1

    # Create and subtract each screw hole
    for i, y_pos in enumerate(hole_y_positions):
        # Screw shaft hole (through entire base)
        shaft = create_cylinder(
            SCREW_HOLE_DIA / 2,
            BASE_THICKNESS + 2,
            hole_x,
            y_pos,
            hole_z_bottom
        )

        # Countersink (from bottom surface)
        countersink = create_cylinder(
            SCREW_COUNTERSINK_DIA / 2,
            SCREW_COUNTERSINK_DEPTH + 0.5,
            hole_x,
            y_pos,
            hole_z_bottom
        )

        # Combine shaft and countersink
        try:
            hole = trimesh.boolean.union([shaft, countersink], engine='manifold')
            body = trimesh.boolean.difference([body, hole], engine='manifold')
            print(f"  Hole {i+1} at Y={y_pos:.1f}mm")
        except Exception as e:
            print(f"  Warning: Hole {i+1} subtraction failed: {e}")

    return body

def generate_wire_duct():
    """Generate complete wire duct with mounting base and screw holes."""

    print("\n=== Generating Wire Duct ===\n")

    # Generate main duct body with mounting base
    duct = generate_duct_body()

    # Add screw holes
    duct = add_screw_holes(duct)

    # Validate mesh
    print(f"\nMesh validation:")
    print(f"  Watertight: {duct.is_watertight}")
    print(f"  Valid volume: {duct.is_volume}")

    if not duct.is_watertight:
        print("  Attempting mesh repair...")
        duct.fill_holes()

    return duct

def main():
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Generate the wire duct
    duct = generate_wire_duct()

    # Get bounds for info
    bounds = duct.bounds
    size = bounds[1] - bounds[0]
    print(f"\nFinal dimensions: {size[0]:.1f}mm x {size[1]:.1f}mm x {size[2]:.1f}mm")

    # Export STL
    output_path = os.path.join(script_dir, "wire_duct_screw_mount.stl")
    duct.export(output_path)
    print(f"STL exported to: {output_path}")

    print("\n" + "="*60)
    print("ASSEMBLY INSTRUCTIONS:")
    print("="*60)
    print("1. Print wire_duct_screw_mount.stl")
    print("2. Position duct so it aligns with cable tray slot opening")
    print("3. Mark screw hole positions on desk underside")
    print("4. Pre-drill pilot holes if needed")
    print("5. Attach with 2x #8 wood screws through countersunk holes")
    print("6. Route cables through duct - internal lip retains cables")
    print("7. Print multiple segments for longer cable runs")
    print("="*60)

if __name__ == "__main__":
    main()
