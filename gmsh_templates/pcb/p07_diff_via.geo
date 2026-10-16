// P07: differential via pair, 4 ports (pcb_problem_benchmark_settings.md 5.11)
//
// Length unit: mm. The 4-layer board of P03 (p03_signal_via.geo):
// [-B, B] x [-B, B] (B = boardW/2), stack from the top
//   z1 = t34 + t23 + t12  L1: two microstrips (width wL1) from x = -B to the vias, lands
//   z2 = t34 + t23        L2: ground plane with an antipad (antipadD) at each via
//   z3 = t34              L3: two striplines (width wL3) from the vias to x = +B, lands
//   z4 = 0                L4: ground plane with an antipad at each via (board bottom face)
// Differential pair: line P at y = +pitch/2, line N at y = -pitch/2.
//   signal vias  diameter viaD, via P at (0, +pitch/2), via N at (viaShift, -pitch/2):
//                viaShift is the asymmetry (the N via moved along x; its L1 trace is
//                longer and its L3 trace shorter by viaShift). From z4 (through via,
//                stub L3-L4) or from z3 (backdrill = 1) up to z1.
//   return vias  nReturnVias (0, 2 or 4) vias of diameter returnViaD between L4 and L2:
//                2: at (0, +-(pitch/2 + returnViaDist)), outside the pair;
//                4: also at (-returnViaDist, +-pitch/2)
// All conductors are zero-thickness PEC sheets (internal surfaces) except the
// vias, which are removed from the mesh (their surfaces are PEC). The dielectric
// is one region (Substrate). Air (airMargin) surrounds the board; the outer box
// is OuterBoundary (ABC).
// Lumped ports on the board edges (internal surfaces between board and air):
//   Port1  x = -B, |y - pitch/2| <= wL1/2, z2 <= z <= z1  (L1 line P, direction +z)
//   Port2  x = -B, |y + pitch/2| <= wL1/2, z2 <= z <= z1  (L1 line N, direction +z)
//   Port3  x = +B, |y - pitch/2| <= wL3/2, z3 <= z <= z2  (L3 line P, direction -z)
//   Port4  x = +B, |y + pitch/2| <= wL3/2, z3 <= z <= z2  (L3 line N, direction -z)
// Differential ports: (Port1, Port2) on L1, (Port3, Port4) on L3.
//
// Mesh: the rules of P03. Element size <= lambda0/(Nlambda*sqrt(eps)) in each
// material (lambda0 at meshFreqGHz, by default freqGHz), refined
//   min(wL1/nW, t12/nH) within t12 of the L1 traces and Port1, Port2,
//   min(wL3/nW, t23/nH) within t23 of the L3 traces and Port3, Port4,
//   pi*viaD/nCirc       within landD/2 of the via surfaces,
// graded outwards with ratio growth; in each dielectric layer of thickness t
// the size is at most aspectMax * t.
//
// Physical tags (settings 6.1):
//   volumes : Air = 1, Substrate = 2
//   surfaces: PEC_Ground = 11 (L2, L4), PEC_Trace = 12 (L1, L3 with lands),
//             OuterBoundary = 13, PEC_Via = 15, PEC_ReturnVia = 16 (only if
//             nReturnVias > 0), Port1..Port4 = 21..24
//
// Parameters below are overwritten per parameter set from
// freefem/pcb/pcb_case_parameters.json (one "name = value;" per line).

SetFactory("OpenCASCADE");

freqGHz = 10.0;      // frequency [GHz]
meshFreqGHz = 0;     // frequency for the mesh-size rule [GHz]; 0: freqGHz
epsSub = 4.4;        // substrate relative permittivity (real part)
boardW = 20.0;       // board size (x and y)
t12 = 0.2;           // L1-L2 dielectric thickness
t23 = 0.6;           // L2-L3 dielectric thickness
t34 = 0.6;           // L3-L4 dielectric thickness
wL1 = 0.38;          // L1 microstrip width
wL3 = 0.55;          // L3 stripline width
pitch = 1.0;         // centre distance of the two lines and vias (y)
viaShift = 0.0;      // asymmetry: x offset of the N via (line at y = -pitch/2)
viaD = 0.3;          // signal via diameter
landD = 0.6;         // land diameter (L1, L3)
antipadD = 0.8;      // antipad diameter (L2, L4), one per via
backdrill = 0;       // 0: through vias (stub L3-L4), 1: back-drilled (end at L3)
nReturnVias = 2;     // number of return vias (0, 2 or 4)
returnViaDist = 1.0; // distance of the return vias from the signal vias
returnViaD = 0.3;    // return via diameter
airMargin = 5.0;     // air around the board (sides, above, below)
Nlambda = 10;        // elements per wavelength
nW = 4;              // elements across a trace width
nH = 3;              // elements through the dielectric under a trace
nCirc = 8;           // elements around the via circumference
aspectMax = 4;       // in-plane size <= aspectMax * layer thickness in each dielectric layer
growth = 1.3;        // size growth rate away from the refined features
meshAlgo3D = 10;     // Gmsh 3D algorithm (Mesh.Algorithm3D): 1 Delaunay, 10 HXT

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

// Via centres: index 0 = line P, 1 = line N.
xv() = {0, viaShift};
yv() = {pitch/2, -pitch/2};
// Return via centres.
xr() = {};
yr() = {};
If (nReturnVias >= 2)
  xr() += {0, 0};
  yr() += {pitch/2 + returnViaDist, -pitch/2 - returnViaDist};
EndIf
If (nReturnVias >= 4)
  xr() += {-returnViaDist, -returnViaDist};
  yr() += {pitch/2, -pitch/2};
EndIf
nRet = #xr();

// ---------------------------------------------------------------------------
// Geometry
// ---------------------------------------------------------------------------
Box(1) = {-B, -B, z4, boardW, boardW, z1 - z4};
Box(2) = {-B - airMargin, -B - airMargin, z4 - airMargin,
          boardW + 2*airMargin, boardW + 2*airMargin, z1 - z4 + 2*airMargin};

// Signal vias and return vias (solids, removed after the fragmentation).
vTool() = {};
For k In {0 : 1}
  Cylinder(3 + k) = {xv(k), yv(k), zViaBot, 0, 0, z1 - zViaBot, viaD/2};
  vTool() += {3 + k};
EndFor
If (nRet > 0)
  For k In {0 : nRet - 1}
    Cylinder(10 + k) = {xr(k), yr(k), z4, 0, 0, z2 - z4, returnViaD/2};
    vTool() += {10 + k};
  EndFor
EndIf

// Ground planes with the two antipads.
Rectangle(201) = {-B, -B, z2, boardW, boardW};
Disk(202) = {xv(0), yv(0), z2, antipadD/2};
Disk(203) = {xv(1), yv(1), z2, antipadD/2};
gL2() = BooleanDifference{ Surface{201}; Delete; }{ Surface{202, 203}; Delete; };
Rectangle(204) = {-B, -B, z4, boardW, boardW};
Disk(205) = {xv(0), yv(0), z4, antipadD/2};
Disk(206) = {xv(1), yv(1), z4, antipadD/2};
gL4() = BooleanDifference{ Surface{204}; Delete; }{ Surface{205, 206}; Delete; };

// Traces with lands; the via cross-sections are cut out (they are via faces).
sTr() = {};
For k In {0 : 1}
  Rectangle(211 + 10*k) = {-B, yv(k) - wL1/2, z1, B + xv(k), wL1};
  Disk(212 + 10*k) = {xv(k), yv(k), z1, landD/2};
  ta() = BooleanUnion{ Surface{211 + 10*k}; Delete; }{ Surface{212 + 10*k}; Delete; };
  Disk(213 + 10*k) = {xv(k), yv(k), z1, viaD/2};
  ta() = BooleanDifference{ Surface{ta()}; Delete; }{ Surface{213 + 10*k}; Delete; };
  Rectangle(214 + 10*k) = {xv(k), yv(k) - wL3/2, z3, B - xv(k), wL3};
  Disk(215 + 10*k) = {xv(k), yv(k), z3, landD/2};
  tb() = BooleanUnion{ Surface{214 + 10*k}; Delete; }{ Surface{215 + 10*k}; Delete; };
  Disk(216 + 10*k) = {xv(k), yv(k), z3, viaD/2};
  tb() = BooleanDifference{ Surface{tb()}; Delete; }{ Surface{216 + 10*k}; Delete; };
  sTr() += {ta(), tb()};
EndFor

// Port rectangles: (u, v, 0) -> (0, u, v), then moved to x = -B / +B.
Rectangle(241) = {yv(0) - wL1/2, z2, 0, wL1, z1 - z2};
Rectangle(242) = {yv(1) - wL1/2, z2, 0, wL1, z1 - z2};
Rectangle(243) = {yv(0) - wL3/2, z3, 0, wL3, z2 - z3};
Rectangle(244) = {yv(1) - wL3/2, z3, 0, wL3, z2 - z3};
Rotate {{1, 0, 0}, {0, 0, 0}, Pi/2} { Surface{241, 242, 243, 244}; }
Rotate {{0, 0, 1}, {0, 0, 0}, Pi/2} { Surface{241, 242, 243, 244}; }
Translate {-B, 0, 0} { Surface{241, 242}; }
Translate {B, 0, 0} { Surface{243, 244}; }

BooleanFragments{ Volume{2}; Delete; }{ Volume{1, vTool()}; Surface{gL2(), gL4(), sTr(), 241, 242, 243, 244}; Delete; }

// ---------------------------------------------------------------------------
// Identification (bounding boxes) and removal of the via solids
// ---------------------------------------------------------------------------
eps = 1e-4 * t12;
rv = viaD/2;
vSig() = {};
For k In {0 : 1}
  vSig() += Volume In BoundingBox{xv(k) - rv - eps, yv(k) - rv - eps, zViaBot - eps, xv(k) + rv + eps, yv(k) + rv + eps, z1 + eps};
EndFor
vRet() = {};
If (nRet > 0)
  rr = returnViaD/2;
  For k In {0 : nRet - 1}
    vRet() += Volume In BoundingBox{xr(k) - rr - eps, yr(k) - rr - eps, z4 - eps, xr(k) + rr + eps, yr(k) + rr + eps, z2 + eps};
  EndFor
EndIf
sVia() = Abs(CombinedBoundary{ Volume{vSig()}; });
sRet() = {};
If (nRet > 0)
  sRet() = Abs(CombinedBoundary{ Volume{vRet()}; });
EndIf
Delete { Volume{vSig(), vRet()}; }

vAll() = Volume{:};
vSub() = Volume In BoundingBox{-B - eps, -B - eps, z4 - eps, B + eps, B + eps, z1 + eps};
vAir() = vAll();
vAir() -= vSub();

xMax = Max(xv(0), xv(1));
xMin = Min(xv(0), xv(1));
yT = pitch/2 + landD/2;
sL1() = Surface In BoundingBox{-B - eps, -yT - eps, z1 - eps, xMax + landD/2 + eps, yT + eps, z1 + eps};
sL1() -= sVia();
sL3() = Surface In BoundingBox{xMin - landD/2 - eps, -yT - eps, z3 - eps, B + eps, yT + eps, z3 + eps};
sL3() -= sVia();
sTrace() = {sL1(), sL3()};
sGnd() = Surface In BoundingBox{-B - eps, -B - eps, z2 - eps, B + eps, B + eps, z2 + eps};
sGnd() += Surface In BoundingBox{-B - eps, -B - eps, z4 - eps, B + eps, B + eps, z4 + eps};
For k In {0 : 1}
  sAp() = Surface In BoundingBox{xv(k) - antipadD/2 - eps, yv(k) - antipadD/2 - eps, z4 - eps, xv(k) + antipadD/2 + eps, yv(k) + antipadD/2 + eps, z4 + eps};
  sGnd() -= sAp();
EndFor
sGnd() -= sVia();
sGnd() -= sRet();
sPort1() = Surface In BoundingBox{-B - eps, yv(0) - wL1/2 - eps, z2 - eps, -B + eps, yv(0) + wL1/2 + eps, z1 + eps};
sPort2() = Surface In BoundingBox{-B - eps, yv(1) - wL1/2 - eps, z2 - eps, -B + eps, yv(1) + wL1/2 + eps, z1 + eps};
sPort3() = Surface In BoundingBox{B - eps, yv(0) - wL3/2 - eps, z3 - eps, B + eps, yv(0) + wL3/2 + eps, z2 + eps};
sPort4() = Surface In BoundingBox{B - eps, yv(1) - wL3/2 - eps, z3 - eps, B + eps, yv(1) + wL3/2 + eps, z2 + eps};
sOuter() = Abs(CombinedBoundary{ Volume{vAll()}; });
sOuter() -= sVia();
sOuter() -= sRet();

Physical Volume("Air", 1) = {vAir()};
Physical Volume("Substrate", 2) = {vSub()};
Physical Surface("PEC_Ground", 11) = {sGnd()};
Physical Surface("PEC_Trace", 12) = {sTrace()};
Physical Surface("OuterBoundary", 13) = {sOuter()};
Physical Surface("PEC_Via", 15) = {sVia()};
If (nRet > 0)
  Physical Surface("PEC_ReturnVia", 16) = {sRet()};
EndIf
Physical Surface("Port1", 21) = {sPort1()};
Physical Surface("Port2", 22) = {sPort2()};
Physical Surface("Port3", 23) = {sPort3()};
Physical Surface("Port4", 24) = {sPort4()};

// ---------------------------------------------------------------------------
// Mesh size
// ---------------------------------------------------------------------------
Mesh.MeshSizeExtendFromBoundary = 0;
Mesh.MeshSizeFromPoints = 0;
Mesh.MeshSizeFromCurvature = 0;
Mesh.MeshSizeMin = Min(Min(lcL1, lcL3), lcVia);
Mesh.MeshSizeMax = lcAir;

Field[1] = Distance;
Field[1].SurfacesList = {sL1(), sPort1(), sPort2()};
Field[1].Sampling = Ceil(2 * boardW / lcL1);
Field[2] = Threshold;
Field[2].InField = 1;
Field[2].SizeMin = lcL1;
Field[2].SizeMax = lcAir;
Field[2].DistMin = t12;
Field[2].DistMax = t12 + (lcAir - lcL1) / (growth - 1);

Field[3] = Distance;
Field[3].SurfacesList = {sL3(), sPort3(), sPort4()};
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
// HXT, as P03 (fewer slivers than the default Delaunay).
Mesh.Algorithm3D = meshAlgo3D;
// Mesh.OptimizeNetgen = 1 crashes Gmsh 4.15.2 (segmentation fault) on the P03 geometry.
Mesh.OptimizeNetgen = 0;
Mesh.MshFileVersion = 2.2;
