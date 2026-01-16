#!/usr/bin/env python3
"""
Rain the101 Router Wall Mount - Sandwich Design
Generates STL file for 3D printing
"""

import trimesh
import numpy as np

# ============================================
# Parameters - adjust as needed
# ============================================

# Plate dimensions
BRACKET_WIDTH = 112.0    # mm (inner clip spacing is 113mm)
BRACKET_HEIGHT = 100.0   # mm (more coverage for better support)

# Front plate (slides under clips)
FRONT_PLATE_THICKNESS = 2.5  # mm (tighter fit for clips)

# Back plate (mounts to wall)
BACK_PLATE_THICKNESS = 5.0   # mm (thicker for rigidity)

# Spacer
SPACER_GAP = 2.0         # mm (gap between plates)
SPACER_WALL = 5.0        # mm (thickness of spacer walls)

# Edge insets (how far spacer walls are from edges, creating visible gap)
INSET_LEFT = 10.0        # mm from left edge
INSET_RIGHT = 10.0       # mm from right edge
INSET_TOP = 4.0          # mm from top edge
INSET_BOTTOM = 0.0       # mm from bottom edge (0 = at edge for strength)

# Rib grid settings (prevents front plate overhang sagging)
RIB_DIVISIONS = 4        # divide each axis into N sections (4 = 16 cells total)
THIN_RIB = 0.8           # mm - thickness of support ribs (2 nozzle widths)

# Screw holes (screws go from front plate through to wall)
SCREW_HOLE_DIAMETER = 6.0    # mm (for #8 screw SHAFT + concrete anchors)
SCREW_SPACING_H = 70.0       # mm (horizontal center-to-center) - wider bracket
SCREW_SPACING_V = 60.0       # mm (vertical center-to-center) - taller bracket
COUNTERSINK_DIAMETER = 10.0  # mm (for #8 screw HEAD to sit flush)
# COUNTERSINK_DEPTH calculated dynamically as half of total thickness
SCREW_PILLAR_DIAMETER = 14.0 # mm (solid pillar around screw hole - larger for 10mm countersink)

# ============================================
# Generate the bracket
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

def generate_wall_mount():
    """Generate the complete wall mount bracket."""

    total_thickness = BACK_PLATE_THICKNESS + SPACER_GAP + FRONT_PLATE_THICKNESS

    back_plate_w = BRACKET_WIDTH - INSET_LEFT - INSET_RIGHT
    back_plate_h = BRACKET_HEIGHT - INSET_TOP - INSET_BOTTOM

    print("=== Rain the101 Wall Mount - Sandwich Design ===")
    print(f"Front plate (router side): {BRACKET_WIDTH}mm x {BRACKET_HEIGHT}mm x {FRONT_PLATE_THICKNESS}mm")
    print(f"Back plate (wall side): {back_plate_w}mm x {back_plate_h}mm x {BACK_PLATE_THICKNESS}mm")
    print(f"Spacer gap: {SPACER_GAP}mm")
    print(f"Total thickness: {total_thickness}mm")
    print(f"Edge insets: L={INSET_LEFT}mm, R={INSET_RIGHT}mm, T={INSET_TOP}mm, B={INSET_BOTTOM}mm")
    print(f"Screw hole: {SCREW_HOLE_DIAMETER}mm diameter")
    print(f"Countersink: {COUNTERSINK_DIAMETER}mm diameter, {total_thickness/2}mm deep (straight cylinder, half thickness)")
    print(f"Screw pattern: {SCREW_SPACING_H}mm x {SCREW_SPACING_V}mm (4 holes)")
    print(f"Screw pillars: {SCREW_PILLAR_DIAMETER}mm diameter")
    print(f"Screws: Insert from front (router side), through bracket, into wall")
    print(f"Recommended screw length: {total_thickness + 25}mm+ (to reach into wall)")
    print()

    # Create the solid parts
    parts = []

    # 1. Back plate (against wall) - smaller, matches spacer footprint
    back_plate_width = BRACKET_WIDTH - INSET_LEFT - INSET_RIGHT
    back_plate_height = BRACKET_HEIGHT - INSET_TOP - INSET_BOTTOM
    back_plate = create_box(
        back_plate_width,
        back_plate_height,
        BACK_PLATE_THICKNESS,
        INSET_LEFT,      # x position (inset from left)
        INSET_BOTTOM,    # y position (inset from bottom)
        0
    )
    parts.append(back_plate)

    # 2. Spacer - frame walls + rib grid
    spacer_z = BACK_PLATE_THICKNESS

    # Frame walls around perimeter (holds sandwich together)
    # Bottom wall
    bottom_spacer = create_box(
        BRACKET_WIDTH - INSET_LEFT - INSET_RIGHT,
        SPACER_WALL,
        SPACER_GAP,
        INSET_LEFT,
        INSET_BOTTOM,
        spacer_z
    )
    parts.append(bottom_spacer)

    # Top wall
    top_spacer = create_box(
        BRACKET_WIDTH - INSET_LEFT - INSET_RIGHT,
        SPACER_WALL,
        SPACER_GAP,
        INSET_LEFT,
        BRACKET_HEIGHT - SPACER_WALL - INSET_TOP,
        spacer_z
    )
    parts.append(top_spacer)

    # Left wall
    left_spacer = create_box(
        SPACER_WALL,
        BRACKET_HEIGHT - INSET_TOP - INSET_BOTTOM - 2*SPACER_WALL,
        SPACER_GAP,
        INSET_LEFT,
        INSET_BOTTOM + SPACER_WALL,
        spacer_z
    )
    parts.append(left_spacer)

    # Right wall
    right_spacer = create_box(
        SPACER_WALL,
        BRACKET_HEIGHT - INSET_TOP - INSET_BOTTOM - 2*SPACER_WALL,
        SPACER_GAP,
        BRACKET_WIDTH - SPACER_WALL - INSET_RIGHT,
        INSET_BOTTOM + SPACER_WALL,
        spacer_z
    )
    parts.append(right_spacer)

    # Calculate rib grid based on RIB_DIVISIONS
    interior_width = BRACKET_WIDTH - INSET_LEFT - INSET_RIGHT - 2*SPACER_WALL
    interior_height = BRACKET_HEIGHT - INSET_TOP - INSET_BOTTOM - 2*SPACER_WALL
    interior_x_start = INSET_LEFT + SPACER_WALL
    interior_y_start = INSET_BOTTOM + SPACER_WALL

    # Number of ribs = divisions - 1 (e.g., 4 divisions = 3 ribs)
    num_vertical_ribs = RIB_DIVISIONS - 1
    num_horizontal_ribs = RIB_DIVISIONS - 1

    actual_h_span = interior_width / RIB_DIVISIONS
    actual_v_span = interior_height / RIB_DIVISIONS

    print(f"Rib grid: {num_vertical_ribs} vertical x {num_horizontal_ribs} horizontal ribs ({RIB_DIVISIONS}x{RIB_DIVISIONS} = {RIB_DIVISIONS**2} cells)")
    print(f"Cell size: ~{actual_h_span:.1f}mm x ~{actual_v_span:.1f}mm, rib thickness: {THIN_RIB}mm")

    # Create vertical ribs (evenly spaced, slightly inset to avoid overlap)
    rib_margin = 0.1  # small margin to keep ribs cleanly inside frame
    for i in range(num_vertical_ribs):
        rib_x = interior_x_start + (i + 1) * actual_h_span - THIN_RIB / 2
        rib = create_box(
            THIN_RIB,
            interior_height - 2 * rib_margin,
            SPACER_GAP,
            rib_x,
            interior_y_start + rib_margin,
            spacer_z
        )
        parts.append(rib)

    # Create horizontal ribs (evenly spaced, slightly inset to avoid overlap)
    for i in range(num_horizontal_ribs):
        rib_y = interior_y_start + (i + 1) * actual_v_span - THIN_RIB / 2
        rib = create_box(
            interior_width - 2 * rib_margin,
            THIN_RIB,
            SPACER_GAP,
            interior_x_start + rib_margin,
            rib_y,
            spacer_z
        )
        parts.append(rib)

    # 3. Front plate (slides under clips)
    front_z = BACK_PLATE_THICKNESS + SPACER_GAP
    front_plate = create_box(BRACKET_WIDTH, BRACKET_HEIGHT, FRONT_PLATE_THICKNESS, 0, 0, front_z)
    parts.append(front_plate)

    # 4. Screw pillars (solid cylinders connecting front and back plates)
    # These provide solid material for screws to pass through
    cx = INSET_LEFT + back_plate_width / 2
    cy = INSET_BOTTOM + back_plate_height / 2
    pillar_positions = [
        (cx - SCREW_SPACING_H/2, cy - SCREW_SPACING_V/2),
        (cx + SCREW_SPACING_H/2, cy - SCREW_SPACING_V/2),
        (cx - SCREW_SPACING_H/2, cy + SCREW_SPACING_V/2),
        (cx + SCREW_SPACING_H/2, cy + SCREW_SPACING_V/2),
    ]

    for px, py in pillar_positions:
        pillar = create_cylinder(
            SCREW_PILLAR_DIAMETER / 2,
            SPACER_GAP,
            px, py,
            BACK_PLATE_THICKNESS
        )
        parts.append(pillar)

    # Combine all solid parts using boolean union for manifold mesh
    print("Merging parts (boolean union)...")
    bracket = parts[0]
    for part in parts[1:]:
        try:
            bracket = trimesh.boolean.union([bracket, part], engine='manifold')
        except Exception as e:
            print(f"Warning: Union failed, using concatenate: {e}")
            bracket = trimesh.util.concatenate([bracket, part])

    # Create screw holes with countersinks
    # Screws go from FRONT (router side) through entire bracket to wall
    holes = []

    # Hole positions (4 corners in rectangle pattern) - centered on back plate
    hole_cx = INSET_LEFT + back_plate_width / 2
    hole_cy = INSET_BOTTOM + back_plate_height / 2
    hole_positions = [
        (hole_cx - SCREW_SPACING_H/2, hole_cy - SCREW_SPACING_V/2),  # Bottom left
        (hole_cx + SCREW_SPACING_H/2, hole_cy - SCREW_SPACING_V/2),  # Bottom right
        (hole_cx - SCREW_SPACING_H/2, hole_cy + SCREW_SPACING_V/2),  # Top left
        (hole_cx + SCREW_SPACING_H/2, hole_cy + SCREW_SPACING_V/2),  # Top right
    ]

    # Countersink: straight cylinder, depth = half of total thickness
    countersink_depth = total_thickness / 2

    for hx, hy in hole_positions:
        # Screw shaft hole through entire bracket
        shaft_hole = create_cylinder(
            SCREW_HOLE_DIAMETER/2,
            total_thickness + 0.4,
            hx, hy,
            -0.2
        )

        # Straight countersink cylinder at top (screw head sits here)
        countersink = create_cylinder(
            COUNTERSINK_DIAMETER/2,
            countersink_depth + 0.1,
            hx, hy,
            total_thickness - countersink_depth
        )

        # Union shaft hole and countersink
        try:
            combined_hole = trimesh.boolean.union([shaft_hole, countersink], engine='manifold')
            holes.append(combined_hole)
        except Exception:
            holes.append(shaft_hole)
            holes.append(countersink)

    # Combine all holes into one shape
    print("Combining hole shapes...")
    all_holes = holes[0]
    for h in holes[1:]:
        try:
            all_holes = trimesh.boolean.union([all_holes, h], engine='manifold')
        except Exception:
            all_holes = trimesh.util.concatenate([all_holes, h])

    # Boolean difference to create holes
    print("Creating screw holes (boolean operation)...")
    try:
        result = trimesh.boolean.difference([bracket, all_holes], engine='blender')
    except Exception:
        try:
            result = trimesh.boolean.difference([bracket, all_holes], engine='manifold')
        except Exception:
            print("Warning: Boolean operations not available, creating bracket without screw holes.")
            print("You can add screw holes in Bambu Studio or drill them manually.")
            result = bracket

    # Check if mesh is valid and try to repair if needed
    if not result.is_watertight:
        print("Mesh is not watertight, attempting repair...")
        result.fill_holes()

    return result

def main():
    # Generate the mount
    mount = generate_wall_mount()

    # Final validation
    print(f"Mesh is watertight: {mount.is_watertight}")
    print(f"Mesh is valid: {mount.is_volume}")

    # Export to STL
    output_path = "/mnt/c/Users/Krell/Documents/Imps/gits/STL101/rain101/rain101_wall_mount.stl"
    mount.export(output_path)
    print(f"STL exported to: {output_path}")
    print()
    print("Open this file in Bambu Studio to slice and print!")

if __name__ == "__main__":
    main()
