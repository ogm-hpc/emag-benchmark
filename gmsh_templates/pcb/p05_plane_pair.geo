// P05: power/ground plane pair (pcb_problem_benchmark_settings.md 5.9, 15.3)
//
// Length unit: mm. The dielectric slab [0, planeX] x [0, planeY] x [0, gap]
// is the whole domain (no air): ground plane at z = 0 (PEC_Ground), power plane
// at z = gap (PEC_Power), open edges x = 0, planeX, y = 0, planeY with no
// condition (PMC_Edge; the natural boundary condition of the edge-element
// formulation is PMC).
// Feed: z-directed lumped port Port1, the rectangle
//   feedX - portW/2 <= x <= feedX + portW/2, y = feedY, 0 <= z <= gap
// (direction +z, ground to power), an internal surface.
//
// Mesh (settings 5.9): the in-plane triangulation of the bottom face is extruded
// through the gap in nLayers layers (Extrude ... Layers); each prism is split
// into three tetrahedra. In-plane size lcPlane (lambda_g/20 at 3 GHz), refined
// to lcFeed within portW of the feed and graded outwards with ratio growth.
// The bottom face is split along y = feedY into two surfaces so that the port
// segment is a shared edge; its extrusion is the port surface. The two volumes
// both belong to Substrate; the other pieces of the plane y = feedY are
// unlabelled internal faces.
//
// Built-in geometry kernel (not OpenCASCADE): the extrusion of adjacent
// surfaces shares the lateral faces.
//
// Volume conductors (tCond > 0; P01 stage 4 of settings 5.5, the SIBC check
// of handoff task N): both planes become metal slabs of thickness tCond,
// z in [-tCond, 0] and [gap, gap + tCond] (volume Conductor), extruded from the
// same in-plane triangulation in nCond graded layers: the layer next to the
// dielectric is at most condH1 thick (skin depth / 2) and the layers grow by
// condGrowth away from it. PEC_Ground / PEC_Power are then the outer faces of
// the slabs (the field there is ~exp(-tCond/delta)); the dielectric-metal
// interfaces are unlabelled internal faces. tCond = 0 (default) gives the
// original mesh.
//
// Parallel-plate line (portFull = 1, handoff task N): no feed split; the port is
// the whole dielectric end face y = 0 (an outer face), the other end and the
// sides stay PMC, so the line is open-ended with fields uniform in x.
//
// Physical tags (settings 6.1):
//   volumes : Substrate = 2, Conductor = 9 (tCond > 0 only)
//   surfaces: PEC_Ground = 11, PEC_Power = 14, PMC_Edge = 18, Port1 = 21
//
// Parameters below are overwritten per parameter set from
// freefem/pcb/pcb_case_parameters.json (one "name = value;" per line).

freqGHz = 0.77;   // frequency (not used by the mesh; the in-plane size is fixed by lcPlane)
epsSub = 4.0;     // relative permittivity (real part)
planeX = 100.0;   // plane size (x)
planeY = 95.0;    // plane size (y)
gap = 0.4;        // plane separation
nLayers = 2;      // element layers through the gap
feedX = 10.0;     // feed point (port centre)
feedY = 10.0;
portW = 0.4;      // port width (x)
lcPlane = 2.5;    // in-plane element size
lcFeed = 0.2;     // in-plane element size at the feed
growth = 1.3;     // size growth rate away from the feed
tCond = 0;        // conductor (plane) thickness; 0 = PEC planes, no conductor volume
condH1 = 0.0012;  // largest thickness of the conductor layer next to the dielectric
condGrowth = 1.3; // layer thickness ratio inside the conductor (> 1)
portFull = 0;     // 1: parallel-plate line, port = the whole end face y = 0 (feedX = planeX/2,
                  //    portW = planeX, feedY = 0); 0: the feed geometry below

If (portFull)
// ---------------------------------------------------------------------------
// Geometry (portFull): one rectangle; its edge y = 0 extrudes to the port face
// ---------------------------------------------------------------------------
Point(1) = {0, 0, 0};
Point(2) = {planeX, 0, 0};
Point(7) = {planeX, planeY, 0};
Point(8) = {0, planeY, 0};
Line(1) = {1, 2};   // port segment
Line(2) = {2, 7};
Line(3) = {7, 8};
Line(4) = {8, 1};
Curve Loop(1) = {1, 2, 3, 4};
Plane Surface(1) = {1};
sBot[] = {1};
portCurve = 1;
Else
// ---------------------------------------------------------------------------
// Geometry: bottom face split along y = feedY
// ---------------------------------------------------------------------------
Point(1) = {0, 0, 0};
Point(2) = {planeX, 0, 0};
Point(3) = {planeX, feedY, 0};
Point(4) = {feedX + portW/2, feedY, 0};
Point(5) = {feedX - portW/2, feedY, 0};
Point(6) = {0, feedY, 0};
Point(7) = {planeX, planeY, 0};
Point(8) = {0, planeY, 0};

Line(1) = {1, 2};
Line(2) = {2, 3};
Line(3) = {3, 4};
Line(4) = {4, 5};   // port segment
Line(5) = {5, 6};
Line(6) = {6, 1};
Line(7) = {3, 7};
Line(8) = {7, 8};
Line(9) = {8, 6};

Curve Loop(1) = {1, 2, 3, 4, 5, 6};
Plane Surface(1) = {1};
Curve Loop(2) = {-5, -4, -3, 7, 8, 9};
Plane Surface(2) = {2};
sBot[] = {1, 2};
portCurve = 4;
EndIf

ex[] = Extrude {0, 0, gap} { Surface{sBot[]}; Layers{nLayers}; };

eps = 1e-4 * gap;
vDiel() = Volume{:};
zLo = 0;
zHi = gap;
If (tCond > 0)
  // graded layers: thickness condH1' * condGrowth^(k-1), k = 1..nCond, summing to
  // tCond, with condH1' <= condH1 (cumulative heights for Layers{})
  nCond = Ceil(Log(1 + tCond * (condGrowth - 1) / condH1) / Log(condGrowth));
  one[] = {};
  cum[] = {};
  For k In {1:nCond}
    one[] += 1;
    cum[] += (condGrowth^k - 1) / (condGrowth^nCond - 1);
  EndFor
  sTop() = Surface In BoundingBox{-eps, -eps, gap - eps, planeX + eps, planeY + eps, gap + eps};
  exG[] = Extrude {0, 0, -tCond} { Surface{sBot[]}; Layers{one[], cum[]}; };
  exP[] = Extrude {0, 0, tCond} { Surface{sTop()}; Layers{one[], cum[]}; };
  zLo = -tCond;
  zHi = gap + tCond;
  Printf("conductor slabs: tCond = %g, %g layers, first layer %g", tCond, nCond,
         tCond * (condGrowth - 1) / (condGrowth^nCond - 1));
EndIf

// ---------------------------------------------------------------------------
// Physical groups (identified by bounding boxes)
// ---------------------------------------------------------------------------
sGnd() = Surface In BoundingBox{-eps, -eps, zLo - eps, planeX + eps, planeY + eps, zLo + eps};
sPwr() = Surface In BoundingBox{-eps, -eps, zHi - eps, planeX + eps, planeY + eps, zHi + eps};
sPort1() = Surface In BoundingBox{feedX - portW/2 - eps, feedY - eps, -eps, feedX + portW/2 + eps, feedY + eps, gap + eps};
sEdge() = Surface In BoundingBox{-eps, -eps, zLo - eps, eps, planeY + eps, zHi + eps};
sEdge() += Surface In BoundingBox{planeX - eps, -eps, zLo - eps, planeX + eps, planeY + eps, zHi + eps};
sEdge() += Surface In BoundingBox{-eps, -eps, zLo - eps, planeX + eps, eps, zHi + eps};
sEdge() += Surface In BoundingBox{-eps, planeY - eps, zLo - eps, planeX + eps, planeY + eps, zHi + eps};
sEdge() -= sPort1();   // portFull: the port is an outer face

Physical Volume("Substrate", 2) = {vDiel()};
If (tCond > 0)
  vCond() = Volume In BoundingBox{-eps, -eps, zLo - eps, planeX + eps, planeY + eps, eps};
  vCond() += Volume In BoundingBox{-eps, -eps, gap - eps, planeX + eps, planeY + eps, zHi + eps};
  Physical Volume("Conductor", 9) = {vCond()};
EndIf
Physical Surface("PEC_Ground", 11) = {sGnd()};
Physical Surface("PEC_Power", 14) = {sPwr()};
Physical Surface("PMC_Edge", 18) = {sEdge()};
Physical Surface("Port1", 21) = {sPort1()};

// ---------------------------------------------------------------------------
// Mesh size (in-plane; the gap direction is set by the layers)
// ---------------------------------------------------------------------------
Mesh.MeshSizeExtendFromBoundary = 0;
Mesh.MeshSizeFromPoints = 0;
Mesh.MeshSizeFromCurvature = 0;
Mesh.MeshSizeMin = lcFeed;
Mesh.MeshSizeMax = lcPlane;

Field[1] = Distance;
Field[1].CurvesList = {portCurve};
Field[1].Sampling = 20;
Field[2] = Threshold;
Field[2].InField = 1;
Field[2].SizeMin = lcFeed;
Field[2].SizeMax = lcPlane;
Field[2].DistMin = portW;
Field[2].DistMax = portW + (lcPlane - lcFeed) / (growth - 1);
Background Field = 2;

Mesh.Optimize = 1;
Mesh.MshFileVersion = 2.2;
