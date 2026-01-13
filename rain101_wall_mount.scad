// Rain the101 Router Wall Mount - Sandwich Design
// Two plates with spacer for maximum rigidity

/* [Plate Dimensions] */
// Width of bracket (inner clip spacing is 110mm)
bracket_width = 105;  // mm

// Height of bracket (doesn't need full 130mm, half is fine)
bracket_height = 65;  // mm

/* [Front Plate - slides under clips] */
// Thickness of front plate (must fit under clips - 1.5mm gap)
front_plate_thickness = 1.4;  // mm

/* [Back Plate - mounts to wall] */
// Thickness of back plate
back_plate_thickness = 3;  // mm

/* [Spacer] */
// Gap between plates (creates the C-channel)
spacer_gap = 2;  // mm

// Spacer wall thickness
spacer_wall = 8;  // mm

/* [Screw Holes] */
// Screw hole diameter (for #8 screws, use ~4.5mm)
screw_hole_diameter = 4.5;  // mm

// Horizontal spacing between screw holes (center to center)
screw_spacing_h = 70;  // mm

// Vertical spacing between screw holes (center to center)
screw_spacing_v = 40;  // mm

// Countersink depth
countersink_depth = 1.5;  // mm

// Countersink diameter
countersink_diameter = 9;  // mm

/* [Rendering] */
$fn = 32;  // Circle smoothness

// ============================================
// Calculated values
// ============================================
total_thickness = back_plate_thickness + spacer_gap + front_plate_thickness;

// ============================================
// Main Module - Sandwich Bracket
// ============================================

module sandwich_bracket() {
    difference() {
        union() {
            // Back plate (against wall)
            cube([bracket_width, bracket_height, back_plate_thickness]);

            // Spacer walls (top and bottom edges, creating C-channel)
            // Bottom spacer
            translate([0, 0, back_plate_thickness])
                cube([bracket_width, spacer_wall, spacer_gap]);

            // Top spacer
            translate([0, bracket_height - spacer_wall, back_plate_thickness])
                cube([bracket_width, spacer_wall, spacer_gap]);

            // Left spacer (connects top and bottom)
            translate([0, 0, back_plate_thickness])
                cube([spacer_wall, bracket_height, spacer_gap]);

            // Right spacer (connects top and bottom)
            translate([bracket_width - spacer_wall, 0, back_plate_thickness])
                cube([spacer_wall, bracket_height, spacer_gap]);

            // Front plate (slides under clips)
            translate([0, 0, back_plate_thickness + spacer_gap])
                cube([bracket_width, bracket_height, front_plate_thickness]);
        }

        // Screw holes through back plate (4 holes in rectangle pattern)
        // Bottom left
        translate([bracket_width/2 - screw_spacing_h/2, bracket_height/2 - screw_spacing_v/2, -0.1])
            cylinder(h = back_plate_thickness + 0.2, d = screw_hole_diameter);

        // Bottom right
        translate([bracket_width/2 + screw_spacing_h/2, bracket_height/2 - screw_spacing_v/2, -0.1])
            cylinder(h = back_plate_thickness + 0.2, d = screw_hole_diameter);

        // Top left
        translate([bracket_width/2 - screw_spacing_h/2, bracket_height/2 + screw_spacing_v/2, -0.1])
            cylinder(h = back_plate_thickness + 0.2, d = screw_hole_diameter);

        // Top right
        translate([bracket_width/2 + screw_spacing_h/2, bracket_height/2 + screw_spacing_v/2, -0.1])
            cylinder(h = back_plate_thickness + 0.2, d = screw_hole_diameter);

        // Countersinks (from back/wall side)
        translate([bracket_width/2 - screw_spacing_h/2, bracket_height/2 - screw_spacing_v/2, -0.1])
            cylinder(h = countersink_depth + 0.1, d1 = countersink_diameter, d2 = screw_hole_diameter);

        translate([bracket_width/2 + screw_spacing_h/2, bracket_height/2 - screw_spacing_v/2, -0.1])
            cylinder(h = countersink_depth + 0.1, d1 = countersink_diameter, d2 = screw_hole_diameter);

        translate([bracket_width/2 - screw_spacing_h/2, bracket_height/2 + screw_spacing_v/2, -0.1])
            cylinder(h = countersink_depth + 0.1, d1 = countersink_diameter, d2 = screw_hole_diameter);

        translate([bracket_width/2 + screw_spacing_h/2, bracket_height/2 + screw_spacing_v/2, -0.1])
            cylinder(h = countersink_depth + 0.1, d1 = countersink_diameter, d2 = screw_hole_diameter);
    }
}

// Render the bracket
sandwich_bracket();

// ============================================
// Info
// ============================================
echo("=== Rain the101 Wall Mount - Sandwich Design ===");
echo(str("Bracket size: ", bracket_width, "mm x ", bracket_height, "mm"));
echo(str("Total thickness: ", total_thickness, "mm"));
echo(str("  - Back plate: ", back_plate_thickness, "mm"));
echo(str("  - Spacer gap: ", spacer_gap, "mm"));
echo(str("  - Front plate: ", front_plate_thickness, "mm"));
echo(str("Screw pattern: ", screw_spacing_h, "mm x ", screw_spacing_v, "mm"));
