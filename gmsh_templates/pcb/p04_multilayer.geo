// P04: multilayer board with permittivity jumps (pcb_problem_benchmark_settings.md 5.8)
//
// Length unit: mm. Layout as P01/P02 (propagation along y), with a layered board:
//   board      [-subW/2, subW/2] x [-L/2, L/2] x [0, 4*tLayer], four layers of
//              thickness tLayer; from the bottom: eps1, eps2, eps1, eps2
//              (layers 1 and 3: Substrate, epsSub/tanDelta;
//               layers 2 and 4: Substrate2, epsSub2/tanDelta2)
//   air        box around the board: lateral margin airSide (> 0), up to z = 4*tLayer + airH
//   ground     z = 0 under the board (PEC_Ground)
//   trace      zero-thickness PEC sheet at z = 4*tLayer, |x| <= w/2, |y| <= L/2 (PEC_Trace)
//   ports      |x| <= w/2, 0 <= z <= 4*tLayer at y = -L/2 (Port1) and y = +L/2 (Port2):
//              internal surfaces between the board end faces and the air, through
//              the four layers
//   every other outer face: OuterBoundary (ABC, Silver-Mueller), including the
//   bottom of the lateral air margin (z = 0 outside the board)
//
// Mesh (settings 5.8): as P02, the board is the extrusion of its bottom face
// (split along x = -w/2, +w/2), here layer by layer with nH element layers per
// material layer, so that the material interfaces are mesh faces and every
// layer has the same in-plane triangulation. The in-plane size is the
// wavelength rule of the densest layer, lcSub = lambda0/(Nlambda*sqrt(epsMesh)),
// epsMesh = max(epsSub, epsSub2) (5 GHz, eps 100: 0.6 mm), refined to
// lcFine = min(w/nW, lcSub) within dFine = 4*tLayer of the trace and graded
// outwards with ratio growth. The thickness direction has tLayer/nH
// (0.4 mm <= lambda0/(10*sqrt(100)) at 5 GHz). The air is meshed by Delaunay
// from the board's surface mesh and grows to lcAir = lambda0/Nlambda.
// meshEps > 0 replaces epsMesh (the contrast series on one mesh: the mesh of
// eps2 = 100 for every eps2).
//
// Built-in geometry kernel (not OpenCASCADE), as p02_thin_microstrip.geo.
//
// Physical tags (settings 6.1):
//   volumes : Air = 1, Substrate = 2 (layers 1, 3), Substrate2 = 3 (layers 2, 4)
//   surfaces: PEC_Ground = 11, PEC_Trace = 12, OuterBoundary = 13,
//             Port1 = 21, Port2 = 22
//
// Parameters below are overwritten per parameter set from
// freefem/pcb/pcb_case_parameters.json (one "name = value;" per line).

freqGHz = 5.0;    // frequency for the mesh-size rule [GHz]
epsSub = 1.0;     // eps1: relative permittivity of layers 1 and 3 (from the bottom)
epsSub2 = 4.4;    // eps2: relative permittivity of layers 2 and 4
meshEps = 0;      // permittivity of the mesh-size rule (0: max(epsSub, epsSub2))
tLayer = 0.4;     // thickness of each of the four layers
w = 1.0;          // trace width
subW = 40.0;      // board width (x)
L = 40.0;         // board length = trace length (y)
airH = 20.0;      // air height above the board
airSide = 5.0;    // lateral air margin around the board (> 0)
Nlambda = 10;     // elements per wavelength
nW = 4;           // elements across the trace width
nH = 1;           // element layers through each material layer
lcCap = 4.0;      // upper bound of the element size
growth = 1.3;     // size growth rate away from the trace

c0 = 299.792458;  // speed of light [mm GHz]
lambda0 = c0 / freqGHz;
h = 4 * tLayer;   // board thickness
epsMesh = (meshEps > 0) ? meshEps : Max(epsSub, epsSub2);
lcAir = Min(lambda0 / Nlambda, lcCap);
lcSub = Min(lambda0 / (Nlambda * Sqrt(epsMesh)), lcCap);
lcFine = Min(w / nW, lcSub);
dFine = h;        // distance from the trace with the size lcFine

// ---------------------------------------------------------------------------
// Geometry: board bottom face split along x = -w/2, +w/2, extruded layer by layer
// ---------------------------------------------------------------------------
sx = subW / 2;
ly = L / 2;
Point(1) = {-sx, -ly, 0};
Point(2) = {-w/2, -ly, 0};
Point(3) = {w/2, -ly, 0};
Point(4) = {sx, -ly, 0};
Point(5) = {sx, ly, 0};
Point(6) = {w/2, ly, 0};
Point(7) = {-w/2, ly, 0};
Point(8) = {-sx, ly, 0};

Line(1) = {1, 2};
Line(2) = {2, 3};   // Port1 segment
Line(3) = {3, 4};
Line(4) = {4, 5};
Line(5) = {5, 6};
Line(6) = {6, 7};   // Port2 segment
Line(7) = {7, 8};
Line(8) = {8, 1};
Line(9) = {2, 7};   // trace edge x = -w/2
Line(10) = {3, 6};  // trace edge x = +w/2

Curve Loop(1) = {1, 9, 7, 8};        // left of the trace
Plane Surface(1) = {1};
Curve Loop(2) = {2, 10, 6, -9};      // under the trace
Plane Surface(2) = {2};
Curve Loop(3) = {3, 4, 5, -10};      // right of the trace
Plane Surface(3) = {3};

sL = 1; sM = 2; sR = 3;              // current top faces of the three columns
vEps1() = {};
vEps2() = {};
For k In {1:4}
  exL[] = Extrude {0, 0, tLayer} { Surface{sL}; Layers{nH}; };
  exM[] = Extrude {0, 0, tLayer} { Surface{sM}; Layers{nH}; };
  exR[] = Extrude {0, 0, tLayer} { Surface{sR}; Layers{nH}; };
  If (k % 2 == 1)
    vEps1() += {exL[1], exM[1], exR[1]};
  Else
    vEps2() += {exL[1], exM[1], exR[1]};
  EndIf
  sL = exL[0]; sM = exM[0]; sR = exR[0];
EndFor
vSub() = {vEps1(), vEps2()};

// Air box; its bottom face at z = 0 has the board footprint as a hole.
ax = sx + airSide;
ay = ly + airSide;
az = h + airH;
Point(1001) = {-ax, -ay, 0};
Point(1002) = {ax, -ay, 0};
Point(1003) = {ax, ay, 0};
Point(1004) = {-ax, ay, 0};
Point(1005) = {-ax, -ay, az};
Point(1006) = {ax, -ay, az};
Point(1007) = {ax, ay, az};
Point(1008) = {-ax, ay, az};
Line(1001) = {1001, 1002};
Line(1002) = {1002, 1003};
Line(1003) = {1003, 1004};
Line(1004) = {1004, 1001};
Line(1005) = {1005, 1006};
Line(1006) = {1006, 1007};
Line(1007) = {1007, 1008};
Line(1008) = {1008, 1005};
Line(1009) = {1001, 1005};
Line(1010) = {1002, 1006};
Line(1011) = {1003, 1007};
Line(1012) = {1004, 1008};

Curve Loop(1001) = {1001, 1002, 1003, 1004};
Curve Loop(1002) = {1, 2, 3, 4, 5, 6, 7, 8};
Plane Surface(1001) = {1001, 1002};                 // air bottom (annulus)
Curve Loop(1003) = {1005, 1006, 1007, 1008};
Plane Surface(1002) = {1003};                      // air top
Curve Loop(1004) = {1001, 1010, -1005, -1009};
Plane Surface(1003) = {1004};                      // y = -ay
Curve Loop(1005) = {1002, 1011, -1006, -1010};
Plane Surface(1004) = {1005};                      // x = +ax
Curve Loop(1006) = {1003, 1012, -1007, -1011};
Plane Surface(1005) = {1006};                      // y = +ay
Curve Loop(1007) = {1004, 1009, -1008, -1012};
Plane Surface(1006) = {1007};                      // x = -ax

// Board faces in contact with the air: its boundary without the bottom.
eps = 1e-4 * tLayer;
sSubBnd() = CombinedBoundary{ Volume{vSub()}; };
sSubBot() = Surface In BoundingBox{-sx - eps, -ly - eps, -eps, sx + eps, ly + eps, eps};
sSubAir() = Abs(sSubBnd());
sSubAir() -= sSubBot();
Surface Loop(1001) = {1001, 1002, 1003, 1004, 1005, 1006, sSubAir()};
Volume(10000) = {1001};

// ---------------------------------------------------------------------------
// Physical groups (identified by bounding boxes)
// ---------------------------------------------------------------------------
sGnd() = sSubBot();
sTrace() = Surface In BoundingBox{-w/2 - eps, -ly - eps, h - eps, w/2 + eps, ly + eps, h + eps};
sPort1() = Surface In BoundingBox{-w/2 - eps, -ly - eps, -eps, w/2 + eps, -ly + eps, h + eps};
sPort2() = Surface In BoundingBox{-w/2 - eps, ly - eps, -eps, w/2 + eps, ly + eps, h + eps};

Physical Volume("Air", 1) = {10000};
Physical Volume("Substrate", 2) = {vEps1()};
Physical Volume("Substrate2", 3) = {vEps2()};
Physical Surface("PEC_Ground", 11) = {sGnd()};
Physical Surface("PEC_Trace", 12) = {sTrace()};
Physical Surface("OuterBoundary", 13) = {1001, 1002, 1003, 1004, 1005, 1006};
Physical Surface("Port1", 21) = {sPort1()};
Physical Surface("Port2", 22) = {sPort2()};

// ---------------------------------------------------------------------------
// Mesh size (the thickness direction is set by the layers)
// ---------------------------------------------------------------------------
Mesh.MeshSizeExtendFromBoundary = 0;
Mesh.MeshSizeFromPoints = 0;
Mesh.MeshSizeFromCurvature = 0;
Mesh.MeshSizeMin = lcFine;
Mesh.MeshSizeMax = lcAir;

// lcFine within dFine of the trace (in-plane and above), then linear growth
// (slope growth - 1) up to lcAir.
Field[1] = Box;
Field[1].VIn = lcFine;
Field[1].VOut = lcAir;
Field[1].XMin = -w/2 - dFine;
Field[1].XMax = w/2 + dFine;
Field[1].YMin = -ly - dFine;
Field[1].YMax = ly + dFine;
Field[1].ZMin = -dFine;
Field[1].ZMax = h + dFine;
Field[1].Thickness = (lcAir - lcFine) / (growth - 1);
// Wavelength rule in the board, graded (not a jump) into the air.
Field[2] = Box;
Field[2].VIn = lcSub;
Field[2].VOut = lcAir;
Field[2].XMin = -sx;
Field[2].XMax = sx;
Field[2].YMin = -ly;
Field[2].YMax = ly;
Field[2].ZMin = -eps;
Field[2].ZMax = h;
Field[2].Thickness = (lcAir - lcSub) / (growth - 1);
Field[3] = Min;
Field[3].FieldsList = {1, 2};
Background Field = 3;

Mesh.Algorithm3D = 1;   // Delaunay (air)
Mesh.Optimize = 1;
Mesh.MshFileVersion = 2.2;
