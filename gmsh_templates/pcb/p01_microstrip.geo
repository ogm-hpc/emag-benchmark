// P01: uniform microstrip (pcb_problem_benchmark_settings.md 5.5, 15.3)
//
// Length unit: mm. Coordinates:
//   substrate  [-subW/2, subW/2] x [-L/2, L/2] x [0, h]   (FR-4, epsSub, tanDelta)
//   air        box around the substrate: lateral margin airSide, up to z = h + airH
//   ground     z = 0 under the substrate (PEC_Ground)
//   trace      zero-thickness PEC sheet at z = h, |x| <= w/2, |y| <= L/2 (PEC_Trace),
//              an internal surface of the mesh (stage 1 of 5.5);
//              tTrace > 0: a PEC strip of thickness tTrace on the substrate,
//              [-w/2, w/2] x [-L/2, L/2] x [h, h + tTrace], removed from the mesh
//              (its surface is PEC_Trace; stage 2 of 5.5)
//   ports      lumped-port rectangles |x| <= w/2, 0 <= z <= h at y = -L/2 (Port1)
//              and y = +L/2 (Port2), joining the trace ends to the ground.
//              With airSide > 0 they are internal surfaces (substrate end face /
//              lateral air); with airSide = 0 they lie on the outer boundary.
//   every other outer face: OuterBoundary (ABC, Silver-Mueller)
// Propagation along y. The trace length equals the substrate length L (P01-b
// varies both together).
//
// Mesh (settings 5.5, 6.2): element size <= lambda0/(Nlambda*sqrt(eps)) in each
// material, capped at lcCap (the geometry, not the wavelength, limits the size
// at low frequency). Local refinement to lcFine = min(w/nW, h/nH) within a
// distance h of the trace and port surfaces, graded outwards with ratio growth.
// With tTrace > 0 also lcEdge = edgeFactor * tTrace within tTrace of the strip
// edges (the side faces are tTrace high), graded outwards with ratio growth.
//
// Physical tags are fixed so that the FreeFEM configuration does not depend on
// the Gmsh entity numbering:
//   volumes : Air = 1, Substrate = 2
//   surfaces: PEC_Ground = 11, PEC_Trace = 12, OuterBoundary = 13,
//             Port1 = 21, Port2 = 22
//
// Parameters below are overwritten per parameter set from
// freefem/pcb/pcb_case_parameters.json (one "name = value;" per line).

SetFactory("OpenCASCADE");

freqGHz = 1.0;    // frequency for the mesh-size rule [GHz]
epsSub = 4.4;     // substrate relative permittivity (real part)
h = 1.6;          // substrate thickness
w = 3.07;         // trace width
subW = 40.0;      // substrate width (x)
L = 40.0;         // substrate length = trace length (y)
airH = 20.0;      // air height above the substrate
airSide = 5.0;    // lateral air margin around the substrate (0: ports on the outer boundary)
Nlambda = 10;     // elements per wavelength
nW = 4;           // elements across the trace width
nH = 3;           // elements through the substrate thickness under the trace
lcCap = 4.0;      // upper bound of the element size
growth = 1.3;     // size growth rate away from the trace
tTrace = 0;       // trace thickness (0: zero-thickness sheet, stage 1)
edgeFactor = 2;   // element size at the edges of a thick trace = edgeFactor * tTrace

c0 = 299.792458;  // speed of light [mm GHz]
lambda0 = c0 / freqGHz;
lcAir = Min(lambda0 / Nlambda, lcCap);
lcSub = Min(lambda0 / (Nlambda * Sqrt(epsSub)), lcCap);
lcFine = Min(Min(w / nW, h / nH), lcSub);

// ---------------------------------------------------------------------------
// Geometry
// ---------------------------------------------------------------------------
Box(1) = {-subW/2, -L/2, 0, subW, L, h};
Box(2) = {-subW/2 - airSide, -L/2 - airSide, 0, subW + 2*airSide, L + 2*airSide, h + airH};
If (tTrace > 0)
  Box(3) = {-w/2, -L/2, h, w, L, tTrace};
Else
  Rectangle(101) = {-w/2, -L/2, h, w, L};
EndIf
// Port rectangles: drawn in the xy plane, rotated into the xz plane.
Rectangle(102) = {-w/2, 0, 0, w, h};
Rotate {{1, 0, 0}, {0, 0, 0}, Pi/2} { Surface{102}; }
Translate {0, -L/2, 0} { Surface{102}; }
Rectangle(103) = {-w/2, 0, 0, w, h};
Rotate {{1, 0, 0}, {0, 0, 0}, Pi/2} { Surface{103}; }
Translate {0, L/2, 0} { Surface{103}; }

If (tTrace > 0)
  BooleanFragments{ Volume{2}; Delete; }{ Volume{1, 3}; Surface{102, 103}; Delete; }
Else
  BooleanFragments{ Volume{2}; Delete; }{ Volume{1}; Surface{101, 102, 103}; Delete; }
EndIf

// ---------------------------------------------------------------------------
// Physical groups (identified by bounding boxes)
// ---------------------------------------------------------------------------
eps = 1e-4 * h;
If (tTrace > 0)
  // the strip volume: its surface is PEC, the volume is removed from the mesh
  epsT = 1e-3 * tTrace;
  vTr() = Volume In BoundingBox{-w/2 - epsT, -L/2 - epsT, h - epsT, w/2 + epsT, L/2 + epsT, h + tTrace + epsT};
  sTrace() = Abs(CombinedBoundary{ Volume{vTr()}; });
  Delete { Volume{vTr()}; }
EndIf
vAll() = Volume{:};
vSub() = Volume In BoundingBox{-subW/2 - eps, -L/2 - eps, -eps, subW/2 + eps, L/2 + eps, h + eps};
vAir() = vAll();
vAir() -= vSub();

If (tTrace <= 0)
  sTrace() = Surface In BoundingBox{-w/2 - eps, -L/2 - eps, h - eps, w/2 + eps, L/2 + eps, h + eps};
EndIf
sPort1() = Surface In BoundingBox{-w/2 - eps, -L/2 - eps, -eps, w/2 + eps, -L/2 + eps, h + eps};
sPort2() = Surface In BoundingBox{-w/2 - eps, L/2 - eps, -eps, w/2 + eps, L/2 + eps, h + eps};
sGnd() = Surface In BoundingBox{-subW/2 - eps, -L/2 - eps, -eps, subW/2 + eps, L/2 + eps, eps};
sOuter() = CombinedBoundary{ Volume{vAll()}; };
sOuter() -= sGnd();
sOuter() -= sPort1();
sOuter() -= sPort2();
If (tTrace > 0)
  sOuter() = Abs(sOuter());
  sOuter() -= sTrace();
EndIf

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
Mesh.MeshSizeMin = lcFine;
Mesh.MeshSizeMax = lcAir;

// Refinement around the trace and the ports: lcFine up to a distance h, then
// linear growth (slope growth - 1) up to lcSub.
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
fl() = {2, 3};
If (tTrace > 0)
  // Edges of the thick strip: lcEdge within tTrace, then linear growth.
  lcEdge = Min(edgeFactor * tTrace, lcFine);
  cTr() = Abs(Boundary{ Surface{sTrace()}; });
  Field[5] = Distance;
  Field[5].CurvesList = {cTr()};
  Field[5].Sampling = Ceil(2 * L / lcEdge);
  Field[6] = Threshold;
  Field[6].InField = 5;
  Field[6].SizeMin = lcEdge;
  Field[6].SizeMax = lcAir;
  Field[6].DistMin = tTrace;
  Field[6].DistMax = tTrace + (lcAir - lcEdge) / (growth - 1);
  fl() += {6};
  Mesh.MeshSizeMin = lcEdge;
EndIf
Field[4] = Min;
Field[4].FieldsList = {fl()};
Background Field = 4;

Mesh.Optimize = 1;
Mesh.OptimizeNetgen = 1;
Mesh.MshFileVersion = 2.2;
