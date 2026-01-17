#!/usr/bin/env python3
"""
Enclosed Under-Desk Cable Tray with Ribbed Texture
Generates STL file for 3D printing

Features:
- Fully enclosed trough with front/back openings only
- Ribbed/fluted horizontal texture on exterior
- TROTTEN rail clip mounting system
"""

import trimesh
import numpy as np

# ============================================
# Parameters - adjust as needed
# ============================================

# Main tray dimensions
TRAY_LENGTH = 220.0      # mm (along desk, front-to-back openings)
TRAY_WIDTH = 120.0       # mm (side to side)
TRAY_DEPTH = 55.0        # mm (height/depth of tray cavity)

# Wall thickness
WALL_THICKNESS = 2.5     # mm (all walls)
BOTTOM_THICKNESS = 3.0   # mm (bottom is thicker for rigidity)

# Ribbed texture settings
RIB_SPACING = 4.0        # mm (center-to-center distance between ribs)
RIB_DEPTH = 1.2          # mm (how far ribs protrude)
RIB_WIDTH = 2.0          # mm (width of each rib)

# Corner radius
CORNER_RADIUS = 3.0      # mm (rounded corners on tray)

# T-slot slide-in mounting system
# Rail dimensions (T-shape: narrow neck + wide head) - minimal design
RAIL_NECK_WIDTH = 4.0        # mm (narrow part that goes through slot)
RAIL_NECK_HEIGHT = 2.0       # mm (height of neck - thinner)
RAIL_HEAD_WIDTH = 10.0       # mm (wide part that gets captured - narrower)
RAIL_HEAD_HEIGHT = 1.5       # mm (height of head - thinner)
RAIL_LENGTH = 30.0           # mm (length of each rail section - shorter)
RAIL_INSET = 10.0            # mm (distance from tray edge to rail center)
RAIL_POSITIONS = [30.0, 190.0]  # mm (Y positions along length)
RAIL_PAD_WIDTH = 15.0        # mm (width of mounting pad - smaller)

# Rail frame (single piece that mounts to desk)
FRAME_SCREW_HOLE = 4.5       # mm (for #8 wood screws)
FRAME_COUNTERSINK = 9.0      # mm (screw head recess)
FRAME_RAIL_WIDTH = 15.0      # mm (width of each side rail)
FRAME_RAIL_HEIGHT = 6.0      # mm (height/thickness of rails)
FRAME_BEAM_WIDTH = 12.0      # mm (width of cross beams)
FRAME_BEAM_HEIGHT = 4.0      # mm (height of cross beams - thinner than rails)
FRAME_SLOT_WIDTH = 5.0       # mm (comfortable fit for 4mm neck - 0.5mm clearance each side)
FRAME_CAVITY_WIDTH = 11.0    # mm (comfortable fit for 10mm head - 0.5mm clearance each side)
FRAME_CAVITY_HEIGHT = 2.0    # mm (comfortable fit for 1.5mm head - 0.5mm clearance)
FRAME_SLOT_HEIGHT = 2.5      # mm (comfortable fit for 2mm neck - 0.5mm clearance)
FRAME_STOP_THICKNESS = 2.5   # mm (wall at one end to stop tray)
FRAME_LENGTH = 180.0         # mm (length of frame, slightly shorter than tray)
FRAME_WIDTH = 100.0          # mm (distance between outer edges of rails)

# End walls with cable slots
END_WALL_THICKNESS = 2.5     # mm
CABLE_SLOT_WIDTH = 50.0      # mm (width of cable slot)
CABLE_SLOT_HEIGHT = 30.0     # mm (height of slot, open at top)

# Cross beam positions along frame length (as ratio of frame length)
FRAME_BEAM_POSITIONS = [0.0, 0.5, 1.0]  # Front, middle, back

# ============================================
# Helper functions
# ============================================

def create_box(width, height, depth, x=0, y=0, z=0):
    """Create a box mesh at the specified position."""
    box = trimesh.creation.box(extents=[width, height, depth])
    box.apply_translation([x + width/2, y + height/2, z + depth/2])
    return box

def create_rounded_box(width, height, depth, radius, x=0, y=0, z=0, segments=8):
    """Create a box with rounded vertical edges."""
    # For simplicity, create a regular box (rounded corners add complexity)
    # Can enhance with cylinder corners later if needed
    return create_box(width, height, depth, x, y, z)

def create_cylinder(radius, height, x=0, y=0, z=0, segments=32):
    """Create a cylinder mesh at the specified position."""
    cyl = trimesh.creation.cylinder(radius=radius, height=height, sections=segments)
    cyl.apply_translation([x, y, z + height/2])
    return cyl

def create_cylinder_x(radius, length, x=0, y=0, z=0, segments=32):
    """Create a cylinder aligned along X axis."""
    cyl = trimesh.creation.cylinder(radius=radius, height=length, sections=segments)
    # Rotate to align with X axis
    rotation = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
    cyl.apply_transform(rotation)
    cyl.apply_translation([x + length/2, y, z])
    return cyl

# ============================================
# Main generation functions
# ============================================

def generate_tray_shell():
    """Generate the tray body with end walls and cable slot notches."""

    outer_width = TRAY_WIDTH
    outer_length = TRAY_LENGTH
    outer_depth = TRAY_DEPTH + BOTTOM_THICKNESS

    inner_width = TRAY_WIDTH - 2 * WALL_THICKNESS
    inner_length = TRAY_LENGTH - 2 * END_WALL_THICKNESS  # Closed ends now
    inner_depth = TRAY_DEPTH + 1  # Open top

    print(f"=== Enclosed Cable Tray with End Walls ===")
    print(f"Outer: {outer_width}mm W x {outer_length}mm L x {outer_depth}mm D")
    print(f"End walls: {END_WALL_THICKNESS}mm thick")
    print(f"Cable slots: {CABLE_SLOT_WIDTH}mm x {CABLE_SLOT_HEIGHT}mm (open at top)")

    # Create outer shell (now includes end walls)
    outer = create_box(outer_width, outer_length, outer_depth, 0, 0, 0)

    # Create inner cavity (closed at ends)
    inner = create_box(
        inner_width,
        inner_length,
        inner_depth,
        WALL_THICKNESS,
        END_WALL_THICKNESS,  # Start after front end wall
        BOTTOM_THICKNESS
    )

    # Boolean difference to create enclosed trough
    print("Creating enclosed trough with end walls...")
    try:
        shell = trimesh.boolean.difference([outer, inner], engine='manifold')
    except Exception as e:
        print(f"Boolean failed: {e}")
        shell = outer

    # Create cable slot notches (open at top) on both ends
    slot_x = (TRAY_WIDTH - CABLE_SLOT_WIDTH) / 2  # Centered

    # Front slot (Y = 0)
    front_slot = create_box(
        CABLE_SLOT_WIDTH,
        END_WALL_THICKNESS + 2,
        CABLE_SLOT_HEIGHT + 1,  # Extends above top to create open notch
        slot_x,
        -1,
        outer_depth - CABLE_SLOT_HEIGHT
    )

    # Back slot (Y = TRAY_LENGTH - END_WALL_THICKNESS)
    back_slot = create_box(
        CABLE_SLOT_WIDTH,
        END_WALL_THICKNESS + 2,
        CABLE_SLOT_HEIGHT + 1,
        slot_x,
        TRAY_LENGTH - END_WALL_THICKNESS - 1,
        outer_depth - CABLE_SLOT_HEIGHT
    )

    # Subtract slots
    try:
        slots = trimesh.boolean.union([front_slot, back_slot], engine='manifold')
        shell = trimesh.boolean.difference([shell, slots], engine='manifold')
    except Exception as e:
        print(f"Slot subtraction failed: {e}")

    return shell

def generate_ribs():
    """Generate horizontal ribbed texture for exterior surfaces."""

    ribs = []
    outer_depth = TRAY_DEPTH + BOTTOM_THICKNESS  # No top wall now

    # Calculate number of ribs based on spacing
    num_ribs = int(outer_depth / RIB_SPACING)

    print(f"Generating {num_ribs} horizontal ribs (spacing: {RIB_SPACING}mm, depth: {RIB_DEPTH}mm)")

    for i in range(num_ribs):
        z_pos = i * RIB_SPACING + RIB_SPACING / 2

        if z_pos + RIB_WIDTH/2 > outer_depth:
            continue

        # Left side rib (on outer surface)
        left_rib = create_box(
            RIB_DEPTH,
            TRAY_LENGTH,
            RIB_WIDTH,
            -RIB_DEPTH,  # Protrude outward from left wall
            0,
            z_pos - RIB_WIDTH/2
        )
        ribs.append(left_rib)

        # Right side rib
        right_rib = create_box(
            RIB_DEPTH,
            TRAY_LENGTH,
            RIB_WIDTH,
            TRAY_WIDTH,  # Protrude outward from right wall
            0,
            z_pos - RIB_WIDTH/2
        )
        ribs.append(right_rib)

        # Bottom rib (only if above bottom thickness)
        if z_pos < BOTTOM_THICKNESS + RIB_WIDTH:
            bottom_rib = create_box(
                TRAY_WIDTH,
                TRAY_LENGTH,
                RIB_DEPTH,
                0,
                0,
                -RIB_DEPTH  # Protrude downward
            )
            ribs.append(bottom_rib)

    # Add ribs on bottom surface (running along length)
    num_bottom_ribs = int(TRAY_WIDTH / RIB_SPACING)
    for i in range(num_bottom_ribs):
        x_pos = i * RIB_SPACING + RIB_SPACING / 2

        if x_pos + RIB_WIDTH/2 > TRAY_WIDTH:
            continue

        bottom_rib = create_box(
            RIB_WIDTH,
            TRAY_LENGTH,
            RIB_DEPTH,
            x_pos - RIB_WIDTH/2,
            0,
            -RIB_DEPTH
        )
        ribs.append(bottom_rib)

    return ribs


def generate_tray_rails():
    """Generate T-shaped rails with mounting pads on top of side walls."""

    rails = []
    wall_top = TRAY_DEPTH + BOTTOM_THICKNESS  # Top of side walls
    total_rail_height = RAIL_NECK_HEIGHT + RAIL_HEAD_HEIGHT

    print(f"Generating T-rails: neck {RAIL_NECK_WIDTH}x{RAIL_NECK_HEIGHT}mm, head {RAIL_HEAD_WIDTH}x{RAIL_HEAD_HEIGHT}mm")
    print(f"Rail positions along length: {RAIL_POSITIONS}")
    print(f"Mounting pads: {RAIL_PAD_WIDTH}mm wide, connecting to side walls")

    for y_pos in RAIL_POSITIONS:
        # Left side rail (sits on left wall)
        left_x = WALL_THICKNESS / 2  # Center of left wall

        # Mounting pad (sits on top of wall, connects rail to tray)
        left_pad = create_box(
            WALL_THICKNESS + 2,  # Slightly wider than wall for good bond
            RAIL_PAD_WIDTH,
            RAIL_NECK_HEIGHT,  # Same height as neck base
            0,
            y_pos - RAIL_PAD_WIDTH / 2,
            wall_top
        )
        rails.append(left_pad)

        # Neck (narrow part)
        left_neck = create_box(
            RAIL_NECK_WIDTH,
            RAIL_LENGTH,
            RAIL_NECK_HEIGHT,
            left_x - RAIL_NECK_WIDTH / 2,
            y_pos - RAIL_LENGTH / 2,
            wall_top
        )
        rails.append(left_neck)

        # Head (wide part, gets captured)
        left_head = create_box(
            RAIL_HEAD_WIDTH,
            RAIL_LENGTH,
            RAIL_HEAD_HEIGHT,
            left_x - RAIL_HEAD_WIDTH / 2,
            y_pos - RAIL_LENGTH / 2,
            wall_top + RAIL_NECK_HEIGHT
        )
        rails.append(left_head)

        # Right side rail (sits on right wall)
        right_x = TRAY_WIDTH - WALL_THICKNESS / 2  # Center of right wall

        # Mounting pad
        right_pad = create_box(
            WALL_THICKNESS + 2,
            RAIL_PAD_WIDTH,
            RAIL_NECK_HEIGHT,
            TRAY_WIDTH - WALL_THICKNESS - 1,
            y_pos - RAIL_PAD_WIDTH / 2,
            wall_top
        )
        rails.append(right_pad)

        # Neck
        right_neck = create_box(
            RAIL_NECK_WIDTH,
            RAIL_LENGTH,
            RAIL_NECK_HEIGHT,
            right_x - RAIL_NECK_WIDTH / 2,
            y_pos - RAIL_LENGTH / 2,
            wall_top
        )
        rails.append(right_neck)

        # Head
        right_head = create_box(
            RAIL_HEAD_WIDTH,
            RAIL_LENGTH,
            RAIL_HEAD_HEIGHT,
            right_x - RAIL_HEAD_WIDTH / 2,
            y_pos - RAIL_LENGTH / 2,
            wall_top + RAIL_NECK_HEIGHT
        )
        rails.append(right_head)

    return rails

def generate_rail_frame():
    """Generate single rail frame with T-slots on both sides (mounts to desk)."""

    parts = []

    # Inner width between the two rails (where tray fits)
    inner_width = FRAME_WIDTH - 2 * FRAME_RAIL_WIDTH

    print(f"=== Rail Frame ===")
    print(f"Frame: {FRAME_WIDTH}mm W x {FRAME_LENGTH}mm L")
    print(f"Rails: {FRAME_RAIL_WIDTH}mm wide, {FRAME_RAIL_HEIGHT}mm tall")
    print(f"T-slot: cavity {FRAME_CAVITY_WIDTH}mm, slot {FRAME_SLOT_WIDTH}mm")

    # Left rail (solid bar with T-slot on inner side)
    left_rail = create_box(
        FRAME_RAIL_WIDTH,
        FRAME_LENGTH,
        FRAME_RAIL_HEIGHT,
        0, 0, 0
    )
    parts.append(left_rail)

    # Right rail
    right_rail = create_box(
        FRAME_RAIL_WIDTH,
        FRAME_LENGTH,
        FRAME_RAIL_HEIGHT,
        FRAME_WIDTH - FRAME_RAIL_WIDTH, 0, 0
    )
    parts.append(right_rail)

    # Cross beams connecting the rails (thin, same as T-slot roof)
    beam_overlap = 5  # mm to extend into each rail
    t_roof_thickness = FRAME_RAIL_HEIGHT - FRAME_SLOT_HEIGHT - FRAME_CAVITY_HEIGHT  # ~1.5mm
    beam_z = FRAME_SLOT_HEIGHT + FRAME_CAVITY_HEIGHT  # Sits at top of rail (same level as T-roof)

    for pos_ratio in FRAME_BEAM_POSITIONS:
        y_pos = pos_ratio * (FRAME_LENGTH - FRAME_BEAM_WIDTH)
        beam = create_box(
            inner_width + 2 * beam_overlap,  # Extends into both rails
            FRAME_BEAM_WIDTH,
            t_roof_thickness,  # Same thickness as T-slot roof
            FRAME_RAIL_WIDTH - beam_overlap,  # Start inside left rail
            y_pos,
            beam_z  # At top of rail
        )
        parts.append(beam)

    # Combine all frame parts
    print("Combining frame parts...")
    frame = parts[0]
    for part in parts[1:]:
        try:
            frame = trimesh.boolean.union([frame, part], engine='manifold')
        except:
            frame = trimesh.util.concatenate([frame, part])

    # Subtract T-slots from both rails
    # T-slot: narrow slot at bottom (open down & inward), wide cavity above (open inward)
    # The slots must extend PAST the inner edge to be open on the inner face

    # Left rail T-slot (opens toward center/right)
    # Slot and cavity extend from inside the rail to past the inner edge
    left_cavity_start = FRAME_RAIL_WIDTH - FRAME_CAVITY_WIDTH + 2  # Start inside rail

    # Narrow slot at bottom (open down and toward inner face)
    left_slot = create_box(
        FRAME_SLOT_WIDTH + 4,  # Wider to ensure it opens on inner face
        FRAME_LENGTH - FRAME_STOP_THICKNESS + 1,
        FRAME_SLOT_HEIGHT + 1,  # Extends through bottom
        FRAME_RAIL_WIDTH - FRAME_SLOT_WIDTH - 1,  # Positioned to open on inner edge
        FRAME_STOP_THICKNESS,
        -0.5
    )
    # Wide cavity above (open toward inner face)
    left_cavity = create_box(
        FRAME_CAVITY_WIDTH + 2,  # Extends past inner edge
        FRAME_LENGTH - FRAME_STOP_THICKNESS + 1,
        FRAME_CAVITY_HEIGHT,
        FRAME_RAIL_WIDTH - FRAME_CAVITY_WIDTH,  # Starts inside, extends past inner edge
        FRAME_STOP_THICKNESS,
        FRAME_SLOT_HEIGHT
    )

    # Right rail T-slot (opens toward center/left)
    right_rail_inner = FRAME_WIDTH - FRAME_RAIL_WIDTH  # Inner edge of right rail

    # Narrow slot at bottom
    right_slot = create_box(
        FRAME_SLOT_WIDTH + 4,
        FRAME_LENGTH - FRAME_STOP_THICKNESS + 1,
        FRAME_SLOT_HEIGHT + 1,
        right_rail_inner - 3,  # Extends past inner edge (into center)
        FRAME_STOP_THICKNESS,
        -0.5
    )
    # Wide cavity above
    right_cavity = create_box(
        FRAME_CAVITY_WIDTH + 2,
        FRAME_LENGTH - FRAME_STOP_THICKNESS + 1,
        FRAME_CAVITY_HEIGHT,
        right_rail_inner - 2,  # Extends past inner edge
        FRAME_STOP_THICKNESS,
        FRAME_SLOT_HEIGHT
    )

    # Combine all slots
    try:
        all_slots = trimesh.boolean.union([left_cavity, left_slot, right_cavity, right_slot], engine='manifold')
        frame = trimesh.boolean.difference([frame, all_slots], engine='manifold')
    except Exception as e:
        print(f"  Warning: T-slot subtraction failed: {e}")

    # Add screw bosses and holes in the rails
    # Bosses are thicker pads around each screw for proper countersink
    hole_x_left = FRAME_RAIL_WIDTH / 4  # In solid part of left rail
    hole_x_right = FRAME_WIDTH - FRAME_RAIL_WIDTH / 4  # In solid part of right rail

    hole_y_positions = [FRAME_LENGTH * 0.2, FRAME_LENGTH * 0.5, FRAME_LENGTH * 0.8]

    boss_height = 8.0  # Total height for countersink
    boss_diameter = 12.0  # Diameter of boss

    # First add bosses
    for y_pos in hole_y_positions:
        for x_pos in [hole_x_left, hole_x_right]:
            boss = create_cylinder(
                boss_diameter / 2,
                boss_height,
                x_pos, y_pos, 0
            )
            try:
                frame = trimesh.boolean.union([frame, boss], engine='manifold')
            except:
                frame = trimesh.util.concatenate([frame, boss])

    # Then subtract screw holes from bosses
    for y_pos in hole_y_positions:
        for x_pos in [hole_x_left, hole_x_right]:
            shaft = create_cylinder(
                FRAME_SCREW_HOLE / 2,
                boss_height + 1,
                x_pos, y_pos, -0.5
            )
            countersink = create_cylinder(
                FRAME_COUNTERSINK / 2,
                4.0,  # 4mm deep countersink
                x_pos, y_pos, -0.1
            )
            try:
                hole = trimesh.boolean.union([shaft, countersink], engine='manifold')
                frame = trimesh.boolean.difference([frame, hole], engine='manifold')
            except:
                pass

    return frame

def generate_cable_tray():
    """Generate the cable tray with T-profiles that slide into the rail frame."""

    print("\n=== Generating Cable Tray ===\n")

    # Generate main shell (with end walls and cable slots)
    shell = generate_tray_shell()

    # Generate ribs
    ribs = generate_ribs()

    # Generate T-profiles on sides (slide into rail frame)
    rails = generate_tray_rails()

    # Combine all solid parts
    print("\nCombining all parts...")
    all_parts = [shell] + ribs + rails

    result = all_parts[0]
    for i, part in enumerate(all_parts[1:], 1):
        try:
            result = trimesh.boolean.union([result, part], engine='manifold')
        except Exception as e:
            print(f"Warning: Union {i} failed, using concatenate")
            result = trimesh.util.concatenate([result, part])

    # Validate mesh
    print(f"\nMesh is watertight: {result.is_watertight}")
    print(f"Mesh is valid volume: {result.is_volume}")

    if not result.is_watertight:
        print("Attempting mesh repair...")
        result.fill_holes()

    return result

def main():
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Generate the tray
    tray = generate_cable_tray()

    # Get bounds for info
    bounds = tray.bounds
    size = bounds[1] - bounds[0]
    print(f"\nTray dimensions: {size[0]:.1f}mm x {size[1]:.1f}mm x {size[2]:.1f}mm")

    # Export tray STL
    tray_path = os.path.join(script_dir, "cable_tray.stl")
    tray.export(tray_path)
    print(f"Tray STL exported to: {tray_path}")

    # Generate rail frame
    print("\n")
    frame = generate_rail_frame()

    bounds = frame.bounds
    size = bounds[1] - bounds[0]
    print(f"Frame dimensions: {size[0]:.1f}mm x {size[1]:.1f}mm x {size[2]:.1f}mm")

    # Export frame STL
    frame_path = os.path.join(script_dir, "rail_frame.stl")
    frame.export(frame_path)
    print(f"Frame STL exported to: {frame_path}")

    print("\n" + "="*50)
    print("ASSEMBLY INSTRUCTIONS:")
    print("="*50)
    print("1. Print 1x cable_tray.stl")
    print("2. Print 1x rail_frame.stl")
    print("3. Screw the rail frame to desk underside (6 screws)")
    print("4. Slide tray into frame from the open end")
    print("5. Tray stops at the frame's stop walls")
    print("="*50)

if __name__ == "__main__":
    main()
