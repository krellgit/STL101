# STL101 Checkpoints

## R101-003 - 2026-01-16T05:45:00

**Summary:** Optimized ribs to 0.8mm, weight reduction complete

**Goal:** Reduce material usage and print time while maintaining structural integrity and preventing front plate sag.

**Status:** Complete

**Changes:**
1. Reduced rib thickness from 1.5mm to 0.8mm (2 nozzle widths) - minimal needed for bridging support
2. Tested reducing spacer walls from 5mm to 3mm - reverted as it increased weight (longer ribs outweighed wall savings)
3. Resolved blue lines mystery - was just travel moves display in Bambu Studio
4. Confirmed ribs prevent sagging during print

**Files modified:**
1. rain101/generate_mount.py - THIN_RIB reduced to 0.8mm
2. rain101/rain101_wall_mount.stl - Regenerated with optimized ribs

**Commits:**
1. 0fd52a1 - Initial commit: Rain101 wall mount for 3D printing

**Key decisions:**
1. Ribs at 0.8mm are sufficient - they only need to exist for bridging, not carry load
2. Spacer walls stay at 5mm - reducing them increased weight due to longer ribs spanning larger interior
3. Cutouts rejected - user said they look weird
4. Back plate stays 5mm thick - users want it thick for rigidity
5. Further weight reduction via slicer infill settings (support cubic at 15-20%) rather than model changes

**Blockers:** None

**Next steps:**
1. Test print with current design
2. Use support cubic infill at 15-20% on back plate (Z 0-5mm) in Bambu Studio for weight reduction
3. Verify rib grid prevents sagging at 0.8mm thickness

---

## R101-002 - 2026-01-16T05:15:00

**Summary:** Added rib grid to prevent front plate sag

**Goal:** Fix printing issue where front plate overhang was sagging during print, hitting the hot end and causing tears in the print.

**Status:** In Progress

**Changes:**
1. Added configurable rib grid system with RIB_DIVISIONS parameter
2. Changed from original 2-rib cross to 4x4 grid (16 cells, 3x3 ribs)
3. Reduced rib thickness from 3.0mm to 1.5mm to save print time
4. Added 0.1mm rib margin to prevent geometry overlap with frame walls
5. Tested 8x8 grid first but added 40 mins print time - reverted to 4x4

**Files modified:**
1. rain101/generate_mount.py - Added RIB_DIVISIONS, THIN_RIB parameters and grid generation
2. rain101/rain101_wall_mount.stl - Regenerated with rib grid

**Commits:**
1. 0fd52a1 - Initial commit: Rain101 wall mount for 3D printing

**Key decisions:**
1. Chose 4x4 grid (16 cells) as balance between print time and overhang support - 8x8 grid added 40 minutes which was excessive
2. Used 1.5mm thin ribs (down from 3mm) to minimize material and print time while still providing bridge support
3. Cell size ~20mm x 21mm which is at the upper limit for bridging but acceptable for most printers
4. Added small margin (0.1mm) to rib dimensions to avoid geometry artifacts from boolean operations

**Blockers:** Blue lines appearing in sliced preview in Bambu Studio - need to investigate if this is mesh geometry issue or just display artifact

**Next steps:**
1. Investigate what the blue lines represent in the sliced preview
2. Check specific layer in slicer to see if it's internal geometry, travel moves, or support
3. Test print to verify rib grid prevents sagging
4. If 20mm cells still sag, increase RIB_DIVISIONS to 5 (25 cells, ~16mm spans)

---

## R101-001 - 2026-01-14T03:45:00

**Summary:** Updated screw holes for concrete mounting

**Goal:** Modify the Rain101 wall mount design to support concrete mounting with #8 screws and fix the shallow countersink issue.

**Status:** Complete

**Changes:**
1. Increased screw hole diameter from 3.5mm to 5.0mm (for #8 screws + concrete anchors)
2. Increased countersink diameter from 8.0mm to 10.0mm (for #8 screw heads)
3. Increased countersink depth from 4.5mm to 5.0mm (over half of total thickness)
4. Increased screw pillar diameter from 10.0mm to 14.0mm (to support larger countersink)
5. Adjusted front plate thickness from 2.3mm to 2.4mm (tighter clip fit)
6. Regenerated STL file with all updates

**Files modified:**
1. generate_mount.py - Updated screw hole parameters
2. rain101_wall_mount.stl - Regenerated with new dimensions

**Commits:**
- No git repository initialized for this project

**Key decisions:**
1. Chose 5.0mm screw holes to accommodate standard 5-6mm concrete wall anchors with #8 screws (original 3.5mm was too small for concrete mounting)
2. Increased countersink to 5.0mm depth (over half of 9.4mm total) to ensure screw heads sit fully flush - user reported original 4.5mm was printing at ~3mm
3. Set front plate to 2.4mm as middle ground between 2.3mm (too loose) and 2.5mm (potentially too tight)

**Blockers:** None

**Next steps:**
1. Print the updated mount and test fit
2. Verify screw holes accept #8 screws with concrete anchors
3. Confirm countersink depth is correct
4. Test front plate fit under router clips

---
