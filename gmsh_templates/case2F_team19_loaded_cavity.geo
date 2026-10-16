// Case 2F: TEAM Workshop Problem 19 -- "Microwave Field in a Loaded Cavity"
// (A. Bossavit, J.F. Lamaudiere, B. Maestrali, Electricite de France, 1992;
// https://www.compumag.org/jsite/images/stories/TEAM/problem19.pdf)
//
// A standard rectangular waveguide (86.36 x 43.18 mm, inside dimensions)
// abuts a cylindrical cavity (diameter 90mm) through a rectangular iris
// (height = the waveguide's own 43.18mm dimension, variable width l). A
// vertical dielectric rod (Plexiglas eps_r=2.7-0.01i or PVC eps_r=4.0-0.1i,
// diameter 7 or 9mm) can be inserted at the cavity axis, spanning its full
// height (held by pegs top/bottom in the real apparatus).
//
// Simplifications relative to the original experiment (both deliberate,
// documented choices, not oversights):
//  1. Excitation is this project's standard Gaussian volume source placed
//     inside the waveguide stub, NOT a true TE10 modal port. The system
//     MATRIX A (curl-curl - k0^2*epsEff, PEC walls, dielectric rod, iris
//     coupling) that this project's solver/preconditioner benchmark actually
//     evaluates is unaffected by this choice -- only the RHS vector b
//     differs. A true modal port would matter for matching the paper's S11
//     values quantitatively; it does not matter for Krylov/preconditioner
//     conditioning, which is this project's focus.
//  2. PEC walls are ideal (copper's sigma=4.7e7 S/m finite conductivity is
//     not modeled), matching every other case in this project.
//  3. The iris septum (real thickness d~0.7mm) is idealized as the boundary
//     of a short connecting channel rather than a modeled thin plate --
//     the channel's cross-section (irisWidth x bWg) is the physically
//     important quantity (the coupling aperture), not its exact length.
//
// lambda0 is set (in case_parameters.json) to the WAVELENGTH AT EACH LOADING
// CONDITION'S OWN EXPERIMENTALLY MEASURED RESONANT FREQUENCY (Bossavit et
// al., Fig. 5): empty=2541MHz, plex7=2490MHz, plex9=2462MHz, pvc7=2482MHz,
// pvc9=2446MHz -- mirroring this project's established near-resonance
// analysis convention (case2A/2B/2C/2D), but here grounded in a real,
// externally measured reference value rather than an analytically estimated
// mode.

SetFactory("OpenCASCADE");

lambda0 = 117.982; // mm; default = empty-cavity resonance (2541 MHz)

aWg = 86.36;    // waveguide width (y), mm -- inside dimension
bWg = 43.18;    // waveguide height (z), mm = iris height -- inside dimension
Lwg = 150.0;    // waveguide stub length, mm
Rcav = 45.0;    // cavity radius, mm (diameter 90mm)
Hcav = 85.0;    // cavity height (z), mm
irisWidth = 15.0; // l, mm (11-18mm tested in the original experiment; 15mm
                  // is the paper's own suggested reference configuration)
rodR = 4.5;     // dielectric rod radius, mm (0 = empty cavity, no rod)
epsLossy = 2.7; // rod real permittivity (Plexiglas 2.7, PVC 4.0)
tanDelta = 0.0037037; // rod loss tangent = Im(eps)/Re(eps)
                       // (Plexiglas 0.01/2.7; PVC 0.1/4.0=0.025)

chGap = 4.0;    // gap (mm) from the waveguide's end face to the cylinder's
                // near (tangent) point
chPen = 6.0;    // connecting-channel penetration (mm) past that gap, into
                // the cylinder -- comfortably exceeds the ~1mm sagitta at
                // the iris edges for the tested iris widths (11-18mm) and
                // Rcav=45mm, guaranteeing genuine volumetric overlap

lcCoarse = lambda0 / 8.0;
lcFine = lambda0 / 16.0;
Mesh.CharacteristicLengthMin = lcFine;
Mesh.CharacteristicLengthMax = lcCoarse;
Mesh.CharacteristicLengthExtendFromBoundary = 0;
Mesh.CharacteristicLengthFromPoints = 0;
Mesh.CharacteristicLengthFromCurvature = 0;

// Waveguide stub: x in [-Lwg, 0].
Box(1) = {-Lwg, -aWg/2, -bWg/2, Lwg, aWg, bWg};

// Connecting iris channel: bridges from the waveguide's end face (x=0) into
// the cylinder. Cross-section = the iris aperture (irisWidth x bWg).
Box(2) = {0, -irisWidth/2, -bWg/2, chGap + chPen, irisWidth, bWg};

// Cavity cylinder: axis along z, positioned so its near (tangent) point
// sits chGap past the waveguide's end face.
xc = chGap + Rcav;
Cylinder(3) = {xc, 0, -Hcav/2, 0, 0, Hcav, Rcav, 2*Pi};

// NOTE: no Coherence here -- Coherence can renumber/merge entities, which
// would invalidate airMerged[]'s captured volume IDs before they're used in
// the rod BooleanDifference below (confirmed empirically: caused
// "overlapping facets" mesh errors). Coherence is called exactly once, at
// the very end, after all boolean operations are done.
airMerged[] = BooleanUnion{ Volume{1,3}; Delete; }{ Volume{2}; Delete; };

If (rodR > 0)
  // Trimmed very slightly short of the cavity's flat top/bottom faces
  // (rodEps) -- an exact-height rod makes its end caps EXACTLY coincide
  // with the cylinder's end caps, a degenerate-boundary case that OCC's
  // boolean difference cannot mesh ("overlapping facets" / empty result).
  // Physically indistinguishable at this geometry's scale (0.5mm on an
  // 85mm-tall cavity); the real apparatus' pegs are a similarly small
  // detail this project does not model either way.
  rodEps = 0.5;
  Cylinder(4) = {xc, 0, -Hcav/2 + rodEps, 0, 0, Hcav - 2*rodEps, rodR, 2*Pi};
  air[] = BooleanDifference{ Volume{airMerged[]}; Delete; }{ Volume{4}; };
  Coherence;
  Physical Volume("Air") = {air[]};
  Physical Volume("LossyMaterial") = {4};
  // Local refinement via a Cylinder field, NOT MeshSize{PointsOf{...}}: an
  // OCC Cylinder primitive has too few actual Point entities (just the
  // circle-arc seam points) for point-based sizing to meaningfully control
  // its curved surface's discretization. A mesh size comparable to or
  // larger than the rod's diameter produced a reproducible OCC/gmsh seam-
  // triangulation defect on the rod's curved lateral surface ("duplicated
  // facets" / empty volume) -- confirmed empirically (isolated cylinder-
  // minus-concentric-rod test: failed at lc=10mm with EITHER sizing
  // approach, meshed cleanly only once the GLOBAL characteristic length was
  // reduced to lc=3mm). The geometric constraint (rodR/3) is the binding one
  // here, well below the physical-wavelength constraint
  // (lambda0/(16*sqrt(epsLossy))~3.75mm).
  lcRod = rodR / 3.0;
  Field[1] = Cylinder;
  Field[1].VIn = lcRod;
  Field[1].VOut = lcCoarse;
  Field[1].Radius = rodR * 2.0;
  Field[1].XCenter = xc; Field[1].YCenter = 0; Field[1].ZCenter = 0;
  Field[1].XAxis = 0; Field[1].YAxis = 0; Field[1].ZAxis = Hcav;
  Background Field = 1;
Else
  air[] = {airMerged[]};
  Coherence;
  Physical Volume("Air") = {air[]};
EndIf

// PEC = every boundary face of the air region EXCEPT the port face (x=-Lwg),
// which gets a separate Silver-Mueller absorbing tag (PortOut). Computed as
// an explicit set difference (not relying on later Physical Surface
// declarations to "win") to avoid ambiguity from a surface being included in
// two Physical groups.
allBnd[] = Boundary{ Volume{air[]}; };
sPort[] = Surface In BoundingBox{
  -Lwg-1e-3, -aWg/2-1e-3, -bWg/2-1e-3,
  -Lwg+1e-3,  aWg/2+1e-3,  bWg/2+1e-3
};

pecBnd[] = {};
For i In {0:#allBnd[]-1}
  isPort = 0;
  For j In {0:#sPort[]-1}
    If (allBnd[i] == sPort[j])
      isPort = 1;
    EndIf
  EndFor
  If (!isPort)
    pecBnd[] += {allBnd[i]};
  EndIf
EndFor

Physical Surface("PEC") = {pecBnd[]};
Physical Surface("PortOut") = {sPort[]};
