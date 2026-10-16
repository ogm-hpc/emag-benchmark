// P03: multilayer signal via (pcb_problem_benchmark_settings.md 5.7, 15.3)
//
// Length unit: mm. 4-layer FR-4 board [-B, B] x [-B, B] (B = boardW/2), stack
// from the top: L1 signal / t12 / L2 GND / t23 / L3 signal / t34 / L4 GND.
//   z1 = t34 + t23 + t12  L1: microstrip (width wL1) from x = -B to the via, land
//   z2 = t34 + t23        L2: ground plane with an antipad (antipadD) at the via
//   z3 = t34              L3: stripline (width wL3) from the via to x = +B, land
//   z4 = 0                L4: ground plane with an antipad (board bottom face)
// All conductors are zero-thickness PEC sheets (internal surfaces) except the
// vias, which are removed from the mesh (their surfaces are PEC):
//   signal via  diameter viaD at the origin, from z4 (through via, stub L3-L4)
//               or from z3 (backdrill = 1, no stub) up to z1
//   return vias nReturnVias vias of diameter returnViaD between L4 and L2,
//               at distance returnViaDist from the signal via, at the angles
//               returnViaAng0 + 360 k / nReturnVias deg (default 45: 4 vias on the
//               diagonals). A return via that cuts the L3 trace or the land, or
//               does not clear the antipad, stops the meshing with an error.
// The dielectric is one region (Substrate). Air (airMargin) surrounds the board
// on all sides; the outer box is OuterBoundary (ABC).
// Lumped ports on the board edges (internal surfaces between board and air):
//   Port1  x = -B, |y| <= wL1/2, z2 <= z <= z1  (L1 over L2, direction +z)
//   Port2  x = +B, |y| <= wL3/2, z3 <= z <= z2  (L3 under L2, direction -z,
//          ground to trace; one-sided ground, an approximation for a stripline)
//
// Mesh: element size <= lambda0/(Nlambda*sqrt(eps)) in each material (lambda0 at
// meshFreqGHz, by default freqGHz), refined
//   min(wL1/nW, t12/nH) within t12 of the L1 trace and Port1,
//   min(wL3/nW, t23/nH) within t23 of the L3 trace and Port2,
//   pi*viaD/nCirc       within landD/2 of the via surfaces,
// graded outwards with ratio growth. In each dielectric layer of thickness t
// the size is at most aspectMax * t (flat elements in the 0.2 mm layer).
//
// Physical tags (settings 6.1):
//   volumes : Air = 1, Substrate = 2
//   surfaces: PEC_Ground = 11 (L2, L4), PEC_Trace = 12 (L1, L3 with lands),
//             OuterBoundary = 13, PEC_Via = 15, PEC_ReturnVia = 16 (only if
//             nReturnVias > 0), Port1 = 21, Port2 = 22
//
// Parameters below are overwritten per parameter set from
// freefem/pcb/pcb_case_parameters.json (one "name = value;" per line).

SetFactory("OpenCASCADE");

freqGHz = 10.0;      // frequency [GHz]
meshFreqGHz = 0;     // frequency for the mesh-size rule [GHz]; 0: freqGHz (diagnostic sets
                     // change only the solver frequency by fixing it)
epsSub = 4.4;        // substrate relative permittivity (real part)
boardW = 20.0;       // board size (x and y)
t12 = 0.2;           // L1-L2 dielectric thickness
t23 = 0.6;           // L2-L3 dielectric thickness
t34 = 0.6;           // L3-L4 dielectric thickness
wL1 = 0.38;          // L1 microstrip width
wL3 = 0.55;          // L3 stripline width
viaD = 0.3;          // signal via diameter
landD = 0.6;         // land diameter (L1, L3)
antipadD = 0.9;      // antipad diameter (L2, L4)
backdrill = 0;       // 0: through via (stub L3-L4), 1: back-drilled (ends at L3)
nReturnVias = 4;     // number of return vias (0: none)
returnViaDist = 1.0; // centre distance signal via - return via
returnViaD = 0.3;    // return via diameter
returnViaAng0 = 45;  // angle of the first return via [deg]
airMargin = 5.0;     // air around the board (sides, above, below)
Nlambda = 10;        // elements per wavelength
nW = 4;              // elements across a trace width
nH = 3;              // elements through the dielectric under a trace
nCirc = 8;           // elements around the via circumference
aspectMax = 4;       // in-plane size <= aspectMax * layer thickness in each dielectric layer
growth = 1.3;        // size growth rate away from the refined features
meshAlgo3D = 10;     // Gmsh 3D algorithm (Mesh.Algorithm3D): 1 Delaunay, 4 Frontal, 10 HXT

c0 = 299.792458;     // speed of light [mm GHz]
fMesh = freqGHz;
If (meshFreqGHz > 0)
  fMesh = meshFreqGHz;
EndIf
lambda0 = c0 / fMesh;
lcAir = lambda0 / Nlambda;
lcSub = lambda0 / (Nlambda * Sqrt(epsSub));
lcL1 = Min(Min(wL1 / nW, t12 / nH), lcSub);
lcL3 = Min(Min(wL3 / nW, t23 / nH), lcSub);
lcVia = Min(Pi * viaD / nCirc, lcSub);

B = boardW / 2;
z4 = 0;
z3 = t34;
z2 = t34 + t23;
z1 = t34 + t23 + t12;
zViaBot = z4;
If (backdrill)
  zViaBot = z3;
EndIf

// ---------------------------------------------------------------------------
// Geometry
// ---------------------------------------------------------------------------
// Return vias (L4-L2) must clear the antipads, the L3 land and the L3 trace
// (x >= 0, |y| <= wL3/2), and stay on the board.
If (nReturnVias > 0)
  For k In {0 : nReturnVias - 1}
    ang = returnViaAng0*Pi/180 + 2*Pi*k/nReturnVias;
    xr = returnViaDist*Cos(ang);
    yr = returnViaDist*Sin(ang);
    rr = returnViaD/2;
    If (returnViaDist - rr <= antipadD/2 || returnViaDist - rr <= landD/2)
      Error("return via %g does not clear the antipad / land", k);
    EndIf
    If (xr + rr > 0 && Fabs(yr) - rr < wL3/2)
      Error("return via %g cuts the L3 trace", k);
    EndIf
    If (Fabs(xr) + rr >= B || Fabs(yr) + rr >= B)
      Error("return via %g is off the board", k);
    EndIf
  EndFor
EndIf

Box(1) = {-B, -B, z4, boardW, boardW, z1 - z4};
Box(2) = {-B - airMargin, -B - airMargin, z4 - airMargin,
          boardW + 2*airMargin, boardW + 2*airMargin, z1 - z4 + 2*airMargin};

// Signal via and return vias (solids, removed after the fragmentation).
Cylinder(3) = {0, 0, zViaBot, 0, 0, z1 - zViaBot, viaD/2};
vRetTool() = {};
If (nReturnVias > 0)
  For k In {0 : nReturnVias - 1}
    ang = returnViaAng0*Pi/180 + 2*Pi*k/nReturnVias;
    Cylinder(10 + k) = {returnViaDist*Cos(ang), returnViaDist*Sin(ang), z4, 0, 0, z2 - z4, returnViaD/2};
    vRetTool() += {10 + k};
  EndFor
EndIf

// Ground planes with antipads.
Rectangle(201) = {-B, -B, z2, boardW, boardW};
Disk(202) = {0, 0, z2, antipadD/2};
gL2() = BooleanDifference{ Surface{201}; Delete; }{ Surface{202}; Delete; };
Rectangle(203) = {-B, -B, z4, boardW, boardW};
Disk(204) = {0, 0, z4, antipadD/2};
gL4() = BooleanDifference{ Surface{203}; Delete; }{ Surface{204}; Delete; };

// Traces with lands; the via cross-section is cut out (it is a via face).
Rectangle(211) = {-B, -wL1/2, z1, B, wL1};
Disk(212) = {0, 0, z1, landD/2};
t1() = BooleanUnion{ Surface{211}; Delete; }{ Surface{212}; Delete; };
Disk(213) = {0, 0, z1, viaD/2};
t1() = BooleanDifference{ Surface{t1()}; Delete; }{ Surface{213}; Delete; };
Rectangle(221) = {0, -wL3/2, z3, B, wL3};
Disk(222) = {0, 0, z3, landD/2};
t3() = BooleanUnion{ Surface{221}; Delete; }{ Surface{222}; Delete; };
Disk(223) = {0, 0, z3, viaD/2};
t3() = BooleanDifference{ Surface{t3()}; Delete; }{ Surface{223}; Delete; };

// Port rectangles: (u, v, 0) -> (0, u, v), then moved to x = -B / +B.
Rectangle(231) = {-wL1/2, z2, 0, wL1, z1 - z2};
Rectangle(232) = {-wL3/2, z3, 0, wL3, z2 - z3};
Rotate {{1, 0, 0}, {0, 0, 0}, Pi/2} { Surface{231, 232}; }
Rotate {{0, 0, 1}, {0, 0, 0}, Pi/2} { Surface{231, 232}; }
Translate {-B, 0, 0} { Surface{231}; }
Translate {B, 0, 0} { Surface{232}; }

BooleanFragments{ Volume{2}; Delete; }{ Volume{1, 3, vRetTool()}; Surface{gL2(), gL4(), t1(), t3(), 231, 232}; Delete; }

// ---------------------------------------------------------------------------
// Identification (bounding boxes) and removal of the via solids
// ---------------------------------------------------------------------------
eps = 1e-4 * t12;
rv = viaD/2;
vSig() = Volume In BoundingBox{-rv - eps, -rv - eps, zViaBot - eps, rv + eps, rv + eps, z1 + eps};
vRet() = {};
If (nReturnVias > 0)
  For k In {0 : nReturnVias - 1}
    ang = returnViaAng0*Pi/180 + 2*Pi*k/nReturnVias;
    xr = returnViaDist*Cos(ang);
    yr = returnViaDist*Sin(ang);
    rr = returnViaD/2;
    vRet() += Volume In BoundingBox{xr - rr - eps, yr - rr - eps, z4 - eps, xr + rr + eps, yr + rr + eps, z2 + eps};
  EndFor
EndIf
sVia() = Abs(CombinedBoundary{ Volume{vSig()}; });
sRet() = {};
If (nReturnVias > 0)
  sRet() = Abs(CombinedBoundary{ Volume{vRet()}; });
EndIf
Delete { Volume{vSig(), vRet()}; }

vAll() = Volume{:};
vSub() = Volume In BoundingBox{-B - eps, -B - eps, z4 - eps, B + eps, B + eps, z1 + eps};
vAir() = vAll();
vAir() -= vSub();

// Half-widths of the trace-with-land outlines (the land can be narrower than the trace).
yL1 = Max(landD, wL1)/2;
yL3 = Max(landD, wL3)/2;
sTrace() = Surface In BoundingBox{-B - eps, -yL1 - eps, z1 - eps, landD/2 + eps, yL1 + eps, z1 + eps};
sTrace() += Surface In BoundingBox{-landD/2 - eps, -yL3 - eps, z3 - eps, B + eps, yL3 + eps, z3 + eps};
sTrace() -= sVia();
sGnd() = Surface In BoundingBox{-B - eps, -B - eps, z2 - eps, B + eps, B + eps, z2 + eps};
sGnd() += Surface In BoundingBox{-B - eps, -B - eps, z4 - eps, B + eps, B + eps, z4 + eps};
sAntipad4() = Surface In BoundingBox{-antipadD/2 - eps, -antipadD/2 - eps, z4 - eps, antipadD/2 + eps, antipadD/2 + eps, z4 + eps};
sGnd() -= sAntipad4();
sGnd() -= sVia();
sGnd() -= sRet();
sPort1() = Surface In BoundingBox{-B - eps, -wL1/2 - eps, z2 - eps, -B + eps, wL1/2 + eps, z1 + eps};
sPort2() = Surface In BoundingBox{B - eps, -wL3/2 - eps, z3 - eps, B + eps, wL3/2 + eps, z2 + eps};
sOuter() = Abs(CombinedBoundary{ Volume{vAll()}; });
sOuter() -= sVia();
sOuter() -= sRet();

Physical Volume("Air", 1) = {vAir()};
Physical Volume("Substrate", 2) = {vSub()};
Physical Surface("PEC_Ground", 11) = {sGnd()};
Physical Surface("PEC_Trace", 12) = {sTrace()};
Physical Surface("OuterBoundary", 13) = {sOuter()};
Physical Surface("PEC_Via", 15) = {sVia()};
If (nReturnVias > 0)
  Physical Surface("PEC_ReturnVia", 16) = {sRet()};
EndIf
Physical Surface("Port1", 21) = {sPort1()};
Physical Surface("Port2", 22) = {sPort2()};

// ---------------------------------------------------------------------------
// Mesh size
// ---------------------------------------------------------------------------
Mesh.MeshSizeExtendFromBoundary = 0;
Mesh.MeshSizeFromPoints = 0;
Mesh.MeshSizeFromCurvature = 0;
Mesh.MeshSizeMin = Min(Min(lcL1, lcL3), lcVia);
Mesh.MeshSizeMax = lcAir;

sL1() = Surface In BoundingBox{-B - eps, -yL1 - eps, z1 - eps, landD/2 + eps, yL1 + eps, z1 + eps};
sL3() = Surface In BoundingBox{-landD/2 - eps, -yL3 - eps, z3 - eps, B + eps, yL3 + eps, z3 + eps};

Field[1] = Distance;
Field[1].SurfacesList = {sL1(), sPort1()};
Field[1].Sampling = Ceil(2 * boardW / lcL1);
Field[2] = Threshold;
Field[2].InField = 1;
Field[2].SizeMin = lcL1;
Field[2].SizeMax = lcAir;
Field[2].DistMin = t12;
Field[2].DistMax = t12 + (lcAir - lcL1) / (growth - 1);

Field[3] = Distance;
Field[3].SurfacesList = {sL3(), sPort2()};
Field[3].Sampling = Ceil(2 * boardW / lcL3);
Field[4] = Threshold;
Field[4].InField = 3;
Field[4].SizeMin = lcL3;
Field[4].SizeMax = lcAir;
Field[4].DistMin = t23;
Field[4].DistMax = t23 + (lcAir - lcL3) / (growth - 1);

Field[5] = Distance;
Field[5].SurfacesList = {sVia(), sRet()};
Field[5].Sampling = 40;
Field[6] = Threshold;
Field[6].InField = 5;
Field[6].SizeMin = lcVia;
Field[6].SizeMax = lcAir;
Field[6].DistMin = landD/2;
Field[6].DistMax = landD/2 + (lcAir - lcVia) / (growth - 1);

// Wavelength rule in the substrate, graded (not a jump) into the air.
Field[7] = Box;
Field[7].VIn = lcSub;
Field[7].VOut = lcAir;
Field[7].XMin = -B;
Field[7].XMax = B;
Field[7].YMin = -B;
Field[7].YMax = B;
Field[7].ZMin = z4;
Field[7].ZMax = z1;
Field[7].Thickness = (lcAir - lcSub) / (growth - 1);

// Thin layers: in-plane size <= aspectMax * thickness (L1-L2, L2-L3, L3-L4).
Field[9] = Box;
Field[9].VIn = Min(aspectMax * t12, lcSub);
Field[9].VOut = lcAir;
Field[9].XMin = -B;
Field[9].XMax = B;
Field[9].YMin = -B;
Field[9].YMax = B;
Field[9].ZMin = z2;
Field[9].ZMax = z1;
Field[9].Thickness = (lcAir - Min(aspectMax * t12, lcSub)) / (growth - 1);
Field[10] = Box;
Field[10].VIn = Min(aspectMax * t23, lcSub);
Field[10].VOut = lcAir;
Field[10].XMin = -B;
Field[10].XMax = B;
Field[10].YMin = -B;
Field[10].YMax = B;
Field[10].ZMin = z3;
Field[10].ZMax = z2;
Field[10].Thickness = (lcAir - Min(aspectMax * t23, lcSub)) / (growth - 1);
Field[11] = Box;
Field[11].VIn = Min(aspectMax * t34, lcSub);
Field[11].VOut = lcAir;
Field[11].XMin = -B;
Field[11].XMax = B;
Field[11].YMin = -B;
Field[11].YMax = B;
Field[11].ZMin = z4;
Field[11].ZMax = z3;
Field[11].Thickness = (lcAir - Min(aspectMax * t34, lcSub)) / (growth - 1);

Field[8] = Min;
Field[8].FieldsList = {2, 4, 6, 7, 9, 10, 11};
Background Field = 8;

Mesh.Optimize = 1;
// HXT: fewer slivers than the default Delaunay here (min gamma 0.16 vs 0.06).
Mesh.Algorithm3D = meshAlgo3D;
// Mesh.OptimizeNetgen = 1 crashes Gmsh 4.15.2 (segmentation fault) on this geometry.
Mesh.OptimizeNetgen = 0;
Mesh.MshFileVersion = 2.2;
