# MITO foundation — status and measurement register

## Reference and scope
The five supplied photographs are the only appearance reference. No EMO styling was used. This is editable solid KCL, not a mesh. No electronics, face display, motor, servo, wiring or rotating mechanism has been added. The face aperture is open; the white surface visible through it is the inside of the rear hood.

## Components
`main.kcl` places headFront, headBack, bodyFront, bodyBack, leftHand, rightHand, leftFoot, rightFoot, backpack and chestButton. Sleeves and short trouser legs belong to the body halves. Identical left/right hands and feet share native part definitions. The backpack and button are additional separate parts, not fused into the requested eight components.

## Editable inputs
`parameters.kcl` uses lowerCamelCase equivalents of the requested uppercase names. Every unknown dimensional input is marked `REQUIRES_PHYSICAL_MEASUREMENT`. Numerical values are necessary to execute CAD; none is a recovered physical measurement.

| Driving input | Provisional value, mm |
|---|---:|
| Target H × W × D | 118 × 94 × 66 |
| Head section W × H × D | 66 × 59 × 56 |
| Aperture W × H | 50.16 × 43.66 |
| Aperture cutter rear stop from head seam | 5 |
| Aperture corner radius | 21 |
| Torso section W × H × D | 52.14 × 38 × 34 |
| Button diameter / projection | 16 / 6 |
| Backpack W × H × D | 35 × 29 × 12 |
| Rear hole diameter / center spacing | 4.5 / 25 |
| Foot section W × D × H, excluding peg | 17 × 27 × 14 |
| Nominal wall allowance / assembly clearance | 2 / 0.3 |

94 mm width is retained as an envelope target, not forced onto the photographed silhouette. All section dimensions are driving inputs, not certified overall maximum extents. Loft interpolation can change extrema. The physical-analysis tool reported assembly bounds about W66.8 × D61.9 × H141.5 mm, inconsistent with nominal Z placement (sole 0, crown 118); individual part bounds also disagreed with driving dimensions. The cause has NOT been established. Overall-envelope validation is unresolved; do not claim this is a verified 118 × 94 × 66 mm model.

## Validation and construction
The root executes. Instantiated solver sketches were checked in the part/master files and are fully constrained. Face aperture, neck opening and paired backpack holes were visually inspected as voids. Root and part lint passed. Curvature uses constrained circles/arcs and smooth lofts.

The torso is constructed as a native half-section loft before sleeve/leg unions; tiny 0.05 mm feature seam offsets avoid failed coplanar booleans. Main body halves are separated by 0.3 mm; local arm/leg seam gaps can be 0.4 mm. The cavity is defined by reduced loft sections, NOT a constant-normal 2 mm shell. Local wall thickness and assembly interference have not been certified.

Repeated-profile helper functions preserve numerical editability, but sketches inside function bodies are not point-and-click editable. Keep `faceCornerRadius` below half of both aperture dimensions. Revalidate after dimensional changes. Import order and shared `bodyShell.kcl` ownership matter: bodyFront clones the shared shell, bodyBack consumes the original.

## Known incomplete areas — do not call this a finished reproduction
- Aperture remains more oval than the photographed rounded-trapezoid opening.
- Hand shapes, pose and forward projection are simplified and not a faithful pocket-hand reconstruction.
- Hood piping/rear raised panel, drawstrings, pocket relief, rounded hem/cuff details and backpack flap are not reproduced.
- Crown is a provisional split cylindrical mounting pad, not a confirmed copy of the original keychain attachment.
- Front/back seams exist, but retaining lips, screws/latches and validated serviceable fastening are not completed.
- Backpack rear holes exist; its final contoured attachment interface, spacers and fasteners are unresolved.
- Foot, hand, neck and button locating features are provisional; no test fit or interference certification has been performed.
- No print orientation/support plan, wall-thickness study or FDM test print has been completed.

## Physical measurements and better references needed
Measure all head/aperture/body/backpack dimensions, rear-hole diameter/spacing/depth, shell seam position, hand/foot sizes and pose, neck interface, button projection and top mounting feature. Supply square-on front/back/left/right/top/bottom photographs with a ruler in the part plane. Existing views are oblique, not calibrated; the top is partly hidden by the keychain, the rear has opaque markings, and internal shell/fastening details are unseen.
