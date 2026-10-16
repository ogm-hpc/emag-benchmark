// P06: microstrip over a slot in the reference plane (pcb_problem_benchmark_settings.md 5.10)
//
// Length unit: mm. Coordinates:
//   substrate  [-subW/2, subW/2] x [-L/2, L/2] x [0, h]   (FR-4, epsSub, tanDelta)
//   air        box around the substrate: lateral margin airSide, up to z = h + airH
//              above and down to z = -airBelow below (the slot radiates downwards)
//   ground     z = 0 under the substrate (PEC_Ground), an internal surface of the
//              mesh, without the slot aperture
//   slot       aperture |x| <= slotL/2, |y| <= slotW/2 in the ground, crossing under
//              the trace at the middle of the line (slotL = 0: no slot). The
//              aperture is an unnamed internal surface (no condition).
//   stitching  stitchD > 0: two PEC bridges of width stitchW across the slot at
//              x = -stitchD and x = +stitchD (ideal stitching). They are part of
//              PEC_Ground: the aperture is cut into three pieces.
//   trace      zero-thickness PEC sheet at z = h, |x| <= w/2, |y| <= L/2 (PEC_Trace)
//   ports      |x| <= w/2, 0 <= z <= h at y = -L/2 (Port1) and y = +L/2 (Port2),
//              internal surfaces (substrate end face / lateral air)
//   outer faces of the air box: OuterBoundary (ABC, Silver-Mueller)
// Propagation along y, slot along x.
//
// Mesh (settings 5.10, rules of P01): element size <= lambda0/(Nlambda*sqrt(eps))
// in each material at the mesh frequency, capped at lcCap; lcFine = min(w/nW, h/nH)
// within a distance h of the trace and the ports, lcSlot = min(slotW/nSlot, lcFine)
// within a distance h of the slot aperture, graded outwards with ratio growth.
// meshFreqGHz > 0 sets the frequency of the size rule (the series is solved at
// several frequencies on the mesh of the highest one); 0: freqGHz.
//
// Physical tags (settings 6.1):
//   volumes : Air = 1, Substrate = 2
//   surfaces: PEC_Ground = 11, PEC_Trace = 12, OuterBoundary = 13,
//             Port1 = 21, Port2 = 22
//
// Parameters below are overwritten per parameter set from
// freefem/pcb/pcb_case_parameters.json (one "name = value;" per line).

SetFactory("OpenCASCADE");

freqGHz = 3.0;      // solve frequency [GHz] (mesh-size rule if meshFreqGHz = 0)
meshFreqGHz = 10.0; // frequency of the mesh-size rule [GHz] (0: freqGHz)
epsSub = 4.4;       // substrate relative permittivity (real part)
h = 0.8;            // substrate thickness
w = 1.54;           // trace width
subW = 60.0;        // substrate width (x)
L = 60.0;           // substrate length = trace length (y)
airH = 20.0;        // air height above the substrate
airBelow = 20.0;    // air depth below the ground plane
airSide = 5.0;      // lateral air margin around the substrate
slotL = 30.0;       // slot length (x), symmetric about the trace (0: no slot)
slotW = 1.0;        // slot width (y)
stitchD = 0.0;      // stitching bridges at x = -stitchD, +stitchD (0: none)
stitchW = 1.0;      // width (x) of a stitching bridge
Nlambda = 10;       // elements per wavelength
nW = 4;             // elements across the trace width
nH = 3;             // elements through the substrate thickness under the trace
nSlot = 4;          // elements across the slot width
lcCap = 4.0;        // upper bound of the element size
growth = 1.3;       // size growth rate away from the trace and the slot

c0 = 299.792458;    // speed of light [mm GHz]
fMesh = (meshFreqGHz > 0) ? meshFreqGHz : freqGHz;
lambda0 = c0 / fMesh;
lcAir = Min(lambda0 / Nlambda, lcCap);
lcSub = Min(lambda0 / (Nlambda * Sqrt(epsSub)), lcCap);
lcFine = Min(Min(w / nW, h / nH), lcSub);
lcSlot = Min(slotW / nSlot, lcFine);

// ---------------------------------------------------------------------------
// Geometry
// ---------------------------------------------------------------------------
Box(1) = {-subW/2, -L/2, 0, subW, L, h};
Box(2) = {-subW/2 - airSide, -L/2 - airSide, -airBelow, subW + 2*airSide, L + 2*airSide, airBelow + h + airH};
Rectangle(101) = {-w/2, -L/2, h, w, L};
// Port rectangles: drawn in the xy plane, rotated into the xz plane.
Rectangle(102) = {-w/2, 0, 0, w, h};
Rotate {{1, 0, 0}, {0, 0, 0}, Pi/2} { Surface{102}; }
Translate {0, -L/2, 0} { Surface{102}; }
Rectangle(103) = {-w/2, 0, 0, w, h};
Rotate {{1, 0, 0}, {0, 0, 0}, Pi/2} { Surface{103}; }
Translate {0, L/2, 0} { Surface{103}; }

// Slot aperture pieces at z = 0 (between the stitching bridges, if any).
sCut() = {101, 102, 103};
If (slotL > 0)
  If (stitchD > 0)
    Rectangle(111) = {-slotL/2, -slotW/2, 0, slotL/2 - stitchD - stitchW/2, slotW};
    Rectangle(112) = {-stitchD + stitchW/2, -slotW/2, 0, 2*stitchD - stitchW, slotW};
    Rectangle(113) = {stitchD + stitchW/2, -slotW/2, 0, slotL/2 - stitchD - stitchW/2, slotW};
    sCut() += {111, 112, 113};
  Else
    Rectangle(111) = {-slotL/2, -slotW/2, 0, slotL, slotW};
    sCut() += {111};
  EndIf
EndIf

BooleanFragments{ Volume{2}; Delete; }{ Volume{1}; Surface{sCut()}; Delete; }

// ---------------------------------------------------------------------------
// Physical groups (identified by bounding boxes)
// ---------------------------------------------------------------------------
eps = 1e-4 * h;
vAll() = Volume{:};
vSub() = Volume In BoundingBox{-subW/2 - eps, -L/2 - eps, -eps, subW/2 + eps, L/2 + eps, h + eps};
vAir() = vAll();
vAir() -= vSub();

sTrace() = Surface In BoundingBox{-w/2 - eps, -L/2 - eps, h - eps, w/2 + eps, L/2 + eps, h + eps};
sPort1() = Surface In BoundingBox{-w/2 - eps, -L/2 - eps, -eps, w/2 + eps, -L/2 + eps, h + eps};
sPort2() = Surface In BoundingBox{-w/2 - eps, L/2 - eps, -eps, w/2 + eps, L/2 + eps, h + eps};
sGnd() = Surface In BoundingBox{-subW/2 - eps, -L/2 - eps, -eps, subW/2 + eps, L/2 + eps, eps};
sSlot() = {};
If (slotL > 0)
  sSlot() = Surface In BoundingBox{-slotL/2 - eps, -slotW/2 - eps, -eps, slotL/2 + eps, slotW/2 + eps, eps};
  sGnd() -= sSlot();
EndIf
sOuter() = CombinedBoundary{ Volume{vAll()}; };

Physical Volume("Air", 1) = {vAir()};
Physical Volume("Substrate", 2) = {vSub()};
Physical Surface("PEC_Ground", 11) = {sGnd()};
Physical Surface("PEC_Trace", 12) = {sTrace()};
Physical Surface("OuterBoundary", 13) = {sOuter()};
Physical Surface("Port1", 21) = {sPort1()};
Physical Surface("Port2", 22) = {sPort2()};

// ---------------------------------------------------------------------------
// Mesh size
// ---------------------------------------------------------------------------
Mesh.MeshSizeExtendFromBoundary = 0;
Mesh.MeshSizeFromPoints = 0;
Mesh.MeshSizeFromCurvature = 0;
Mesh.MeshSizeMin = lcSlot;
Mesh.MeshSizeMax = lcAir;

// Refinement around the trace and the ports: lcFine up to a distance h, then
// linear growth (slope growth - 1) up to lcAir.
Field[1] = Distance;
Field[1].SurfacesList = {sTrace(), sPort1(), sPort2()};
Field[1].Sampling = Ceil(2 * Max(L, subW) / lcFine);
Field[2] = Threshold;
Field[2].InField = 1;
Field[2].SizeMin = lcFine;
Field[2].SizeMax = lcAir;
Field[2].DistMin = h;
Field[2].DistMax = h + (lcAir - lcFine) / (growth - 1);
// Wavelength rule in the substrate, graded (not a jump) into the air.
Field[3] = Box;
Field[3].VIn = lcSub;
Field[3].VOut = lcAir;
Field[3].XMin = -subW/2;
Field[3].XMax = subW/2;
Field[3].YMin = -L/2;
Field[3].YMax = L/2;
Field[3].ZMin = 0;
Field[3].ZMax = h;
Field[3].Thickness = (lcAir - lcSub) / (growth - 1);
fields() = {2, 3};
// Refinement around the slot aperture (both sides of the ground plane).
If (slotL > 0)
  Field[4] = Distance;
  Field[4].SurfacesList = {sSlot()};
  Field[4].Sampling = Ceil(2 * slotL / lcSlot);
  Field[5] = Threshold;
  Field[5].InField = 4;
  Field[5].SizeMin = lcSlot;
  Field[5].SizeMax = lcAir;
  Field[5].DistMin = h;
  Field[5].DistMax = h + (lcAir - lcSlot) / (growth - 1);
  fields() += {5};
EndIf
Field[6] = Min;
Field[6].FieldsList = {fields()};
Background Field = 6;

Mesh.Algorithm3D = 1;   // Delaunay
Mesh.Optimize = 1;
Mesh.OptimizeNetgen = 1;
Mesh.MshFileVersion = 2.2;
