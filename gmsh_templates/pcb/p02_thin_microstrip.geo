// P02: thin-substrate microstrip (pcb_problem_benchmark_settings.md 5.6)
//
// Length unit: mm. Same layout, labels and ports as P01 (p01_microstrip.geo):
//   substrate  [-subW/2, subW/2] x [-L/2, L/2] x [0, h]   (FR-4, epsSub, tanDelta)
//   air        box around the substrate: lateral margin airSide (> 0), up to z = h + airH
//   ground     z = 0 under the substrate (PEC_Ground)
//   trace      zero-thickness PEC sheet at z = h, |x| <= w/2, |y| <= L/2 (PEC_Trace)
//   ports      |x| <= w/2, 0 <= z <= h at y = -L/2 (Port1) and y = +L/2 (Port2),
//              internal surfaces between the substrate end faces and the air
//   every other outer face: OuterBoundary (ABC, Silver-Mueller), including the
//   bottom of the lateral air margin (z = 0 outside the substrate)
//
// Mesh (settings 5.6): a Delaunay mesh of the thin substrate (h down to
// 0.05 mm) would need an isotropic size h/3 near the trace. Instead the
// substrate is the extrusion of its bottom face in nH element layers
// (Extrude ... Layers; each prism split into three tetrahedra), so the
// thickness direction has h/nH (settings 5.6: at least 3 elements under the
// trace) while the in-plane size is lcFine = min(w/nW, lcSub) within a
// distance dFine = h of the trace (at least nW elements across the width),
// graded outwards with ratio growth to lcSub = lambda0/(Nlambda*sqrt(epsSub)).
// The air above is meshed by Delaunay from the substrate's surface mesh and
// grows to lcAir = lambda0/Nlambda (capped at lcCap).
// The bottom face is split along x = -w/2 and x = +w/2, so that the trace
// footprint is a surface of its own: its top is PEC_Trace and its end faces
// at y = -L/2, +L/2 are the ports.
//
// Built-in geometry kernel (not OpenCASCADE): the extrusion of adjacent
// surfaces shares the lateral faces, and the air volume is closed by the
// substrate's surfaces.
//
// Solder resist (stage 5 of settings 5.5; tRes > 0): a dielectric layer of
// thickness tRes on the substrate over |x| <= w/2 + resMargin, the full length,
// covering the zero-thickness trace (volume Substrate2, epsSub2/tanDelta2). The
// bottom face is then also split along x = -w/2 - resMargin, +w/2 + resMargin
// and the three middle columns are extruded once more by tRes in nRes layers.
// tRes = 0 (default) gives the P02 geometry unchanged.
//
// Physical tags (settings 6.1, as P01):
//   volumes : Air = 1, Substrate = 2, Substrate2 = 3 (solder resist, tRes > 0)
//   surfaces: PEC_Ground = 11, PEC_Trace = 12, OuterBoundary = 13,
//             Port1 = 21, Port2 = 22
//
// Parameters below are overwritten per parameter set from
// freefem/pcb/pcb_case_parameters.json (one "name = value;" per line).

freqGHz = 10.0;   // frequency for the mesh-size rule [GHz]
epsSub = 4.4;     // substrate relative permittivity (real part)
h = 0.2;          // substrate thickness
w = 0.38;         // trace width
subW = 40.0;      // substrate width (x)
L = 40.0;         // substrate length = trace length (y)
airH = 20.0;      // air height above the substrate
airSide = 5.0;    // lateral air margin around the substrate (> 0)
Nlambda = 10;     // elements per wavelength
nW = 4;           // elements across the trace width
nH = 3;           // element layers through the substrate thickness
lcCap = 4.0;      // upper bound of the element size
growth = 1.3;     // size growth rate away from the trace
tRes = 0;         // solder-resist thickness (0: none)
resMargin = 1.6;  // the resist covers |x| <= w/2 + resMargin
nRes = 1;         // element layers through the resist

c0 = 299.792458;  // speed of light [mm GHz]
lambda0 = c0 / freqGHz;
lcAir = Min(lambda0 / Nlambda, lcCap);
lcSub = Min(lambda0 / (Nlambda * Sqrt(epsSub)), lcCap);
lcFine = Min(w / nW, lcSub);
dFine = h;        // distance from the trace with the size lcFine

// ---------------------------------------------------------------------------
// Geometry: substrate bottom face split along x = -w/2, +w/2
// ---------------------------------------------------------------------------
sx = subW / 2;
ly = L / 2;
vRes() = {};
If (tRes <= 0)
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

exL[] = Extrude {0, 0, h} { Surface{1}; Layers{nH}; };
exM[] = Extrude {0, 0, h} { Surface{2}; Layers{nH}; };
exR[] = Extrude {0, 0, h} { Surface{3}; Layers{nH}; };
vSub() = {exL[1], exM[1], exR[1]};
cOuter() = {1, 2, 3, 4, 5, 6, 7, 8};
Else
// With solder resist: five columns, split also at x = -xR, +xR.
xR = w/2 + resMargin;
Point(1) = {-sx, -ly, 0};
Point(2) = {-xR, -ly, 0};
Point(3) = {-w/2, -ly, 0};
Point(4) = {w/2, -ly, 0};
Point(5) = {xR, -ly, 0};
Point(6) = {sx, -ly, 0};
Point(7) = {sx, ly, 0};
Point(8) = {xR, ly, 0};
Point(9) = {w/2, ly, 0};
Point(10) = {-w/2, ly, 0};
Point(11) = {-xR, ly, 0};
Point(12) = {-sx, ly, 0};
For k In {1:11}
  Line(k) = {k, k + 1};
EndFor
Line(12) = {12, 1};
Line(13) = {2, 11};
Line(14) = {3, 10};  // trace edge x = -w/2
Line(15) = {4, 9};   // trace edge x = +w/2
Line(16) = {5, 8};
Curve Loop(1) = {1, 13, 11, 12};
Plane Surface(1) = {1};
Curve Loop(2) = {2, 14, 10, -13};
Plane Surface(2) = {2};
Curve Loop(3) = {3, 15, 9, -14};     // under the trace (Port1 segment 3, Port2 segment 9)
Plane Surface(3) = {3};
Curve Loop(4) = {4, 16, 8, -15};
Plane Surface(4) = {4};
Curve Loop(5) = {5, 6, 7, -16};
Plane Surface(5) = {5};
vSub() = {};
sTop() = {};
For k In {1:5}
  ex[] = Extrude {0, 0, h} { Surface{k}; Layers{nH}; };
  vSub() += {ex[1]};
  If (k >= 2 && k <= 4)
    sTop() += {ex[0]};
  EndIf
EndFor
For k In {0:2}
  ex[] = Extrude {0, 0, tRes} { Surface{sTop(k)}; Layers{nRes}; };
  vRes() += {ex[1]};
EndFor
cOuter() = {1:12};
EndIf

// Air box; its bottom face at z = 0 has the substrate footprint as a hole.
// Tag offset T: 0 as before; 1000 with solder resist (the extra extrusions use tags above 100).
T = (tRes > 0) ? 1000 : 0;
ax = sx + airSide;
ay = ly + airSide;
az = h + airH;
Point(101 + T) = {-ax, -ay, 0};
Point(102 + T) = {ax, -ay, 0};
Point(103 + T) = {ax, ay, 0};
Point(104 + T) = {-ax, ay, 0};
Point(105 + T) = {-ax, -ay, az};
Point(106 + T) = {ax, -ay, az};
Point(107 + T) = {ax, ay, az};
Point(108 + T) = {-ax, ay, az};
Line(101 + T) = {101 + T, 102 + T};
Line(102 + T) = {102 + T, 103 + T};
Line(103 + T) = {103 + T, 104 + T};
Line(104 + T) = {104 + T, 101 + T};
Line(105 + T) = {105 + T, 106 + T};
Line(106 + T) = {106 + T, 107 + T};
Line(107 + T) = {107 + T, 108 + T};
Line(108 + T) = {108 + T, 105 + T};
Line(109 + T) = {101 + T, 105 + T};
Line(110 + T) = {102 + T, 106 + T};
Line(111 + T) = {103 + T, 107 + T};
Line(112 + T) = {104 + T, 108 + T};

Curve Loop(101 + T) = {101 + T, 102 + T, 103 + T, 104 + T};
Curve Loop(102 + T) = {cOuter()};
Plane Surface(101 + T) = {101 + T, 102 + T};                 // air bottom (annulus)
Curve Loop(103 + T) = {105 + T, 106 + T, 107 + T, 108 + T};
Plane Surface(102 + T) = {103 + T};                      // air top
Curve Loop(104 + T) = {101 + T, 110 + T, -(105 + T), -(109 + T)};
Plane Surface(103 + T) = {104 + T};                      // y = -ay
Curve Loop(105 + T) = {102 + T, 111 + T, -(106 + T), -(110 + T)};
Plane Surface(104 + T) = {105 + T};                      // x = +ax
Curve Loop(106 + T) = {103 + T, 112 + T, -(107 + T), -(111 + T)};
Plane Surface(105 + T) = {106 + T};                      // y = +ay
Curve Loop(107 + T) = {104 + T, 109 + T, -(108 + T), -(112 + T)};
Plane Surface(106 + T) = {107 + T};                      // x = -ax

// Substrate faces in contact with the air: its boundary without the bottom.
eps = 1e-4 * h;
sSubBnd() = CombinedBoundary{ Volume{vSub(), vRes()}; };
sSubBot() = Surface In BoundingBox{-sx - eps, -ly - eps, -eps, sx + eps, ly + eps, eps};
sSubAir() = Abs(sSubBnd());
sSubAir() -= sSubBot();
Surface Loop(1) = {101 + T, 102 + T, 103 + T, 104 + T, 105 + T, 106 + T, sSubAir()};
Volume(1000) = {1};

// ---------------------------------------------------------------------------
// Physical groups (identified by bounding boxes)
// ---------------------------------------------------------------------------
sGnd() = sSubBot();
sTrace() = Surface In BoundingBox{-w/2 - eps, -ly - eps, h - eps, w/2 + eps, ly + eps, h + eps};
sPort1() = Surface In BoundingBox{-w/2 - eps, -ly - eps, -eps, w/2 + eps, -ly + eps, h + eps};
sPort2() = Surface In BoundingBox{-w/2 - eps, ly - eps, -eps, w/2 + eps, ly + eps, h + eps};

Physical Volume("Air", 1) = {1000};
Physical Volume("Substrate", 2) = {vSub()};
If (tRes > 0)
  Physical Volume("Substrate2", 3) = {vRes()};
EndIf
Physical Surface("PEC_Ground", 11) = {sGnd()};
Physical Surface("PEC_Trace", 12) = {sTrace()};
Physical Surface("OuterBoundary", 13) = {101 + T, 102 + T, 103 + T, 104 + T, 105 + T, 106 + T};
Physical Surface("Port1", 21) = {sPort1()};
Physical Surface("Port2", 22) = {sPort2()};

// ---------------------------------------------------------------------------
// Mesh size (the substrate thickness direction is set by the layers)
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
// Wavelength rule in the substrate, graded (not a jump) into the air.
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

Mesh.Optimize = 1;
Mesh.MshFileVersion = 2.2;
