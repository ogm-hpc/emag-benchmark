// P08: multi-port network of parallel microstrips (pcb_problem_benchmark_settings.md 5.12)
//
// Length unit: mm. The cross-section of P01 (p01_microstrip.geo) with nLines
// parallel traces:
//   substrate  [-subW/2, subW/2] x [-L/2, L/2] x [0, h], subW = nLines*(w + s) + subMargin
//   air        box around the substrate: lateral margin airSide, up to z = h + airH
//   ground     z = 0 under the substrate (PEC_Ground)
//   traces     zero-thickness PEC sheets at z = h, width w, edge-to-edge spacing s,
//              over the full length; line k = 1..nLines centred at
//              x_k = (k - (nLines + 1)/2) * (w + s)   (PEC_Trace, internal surfaces)
//   ports      lumped-port rectangles |x - x_k| <= w/2, 0 <= z <= h joining the
//              trace ends to the ground: Port(2k-1) at y = -L/2 (near end) and
//              Port(2k) at y = +L/2 (far end) of line k; internal surfaces
//              (substrate end face / lateral air), airSide > 0
//   every other outer face: OuterBoundary (ABC, Silver-Mueller)
// Propagation along y.
//
// Mesh (rules of P01, settings 5.5): element size <= lambda0/(Nlambda*sqrt(eps))
// in each material at the mesh frequency, capped at lcCap; lcFine =
// min(w/nW, h/nH) within a distance h of the traces and the ports, graded
// outwards with ratio growth. meshFreqGHz > 0 sets the frequency of the size
// rule (frequency sweeps on the mesh of the highest frequency); 0: freqGHz.
//
// Physical tags (settings 6.1):
//   volumes : Air = 1, Substrate = 2
//   surfaces: PEC_Ground = 11, PEC_Trace = 12, OuterBoundary = 13,
//             Port1..Port(2*nLines) = 21..(20 + 2*nLines)   (nLines <= 8)
//
// Parameters below are overwritten per parameter set from
// freefem/pcb/pcb_case_parameters.json (one "name = value;" per line).

SetFactory("OpenCASCADE");

freqGHz = 5.0;      // solve frequency [GHz] (mesh-size rule if meshFreqGHz = 0)
meshFreqGHz = 10.0; // frequency of the mesh-size rule [GHz] (0: freqGHz)
epsSub = 4.4;       // substrate relative permittivity (real part)
h = 1.6;            // substrate thickness
w = 3.07;           // trace width
s = 3.07;           // edge-to-edge spacing of the traces
nLines = 2;         // number of traces (<= 8: 16 port slots)
subMargin = 20.0;   // substrate width = nLines*(w + s) + subMargin
L = 40.0;           // substrate length = trace length (y)
airH = 20.0;        // air height above the substrate
airSide = 5.0;      // lateral air margin around the substrate (> 0)
Nlambda = 10;       // elements per wavelength
nW = 4;             // elements across the trace width
nH = 3;             // elements through the substrate thickness under the traces
lcCap = 4.0;        // upper bound of the element size
growth = 1.3;       // size growth rate away from the traces

c0 = 299.792458;    // speed of light [mm GHz]
fMesh = (meshFreqGHz > 0) ? meshFreqGHz : freqGHz;
lambda0 = c0 / fMesh;
lcAir = Min(lambda0 / Nlambda, lcCap);
lcSub = Min(lambda0 / (Nlambda * Sqrt(epsSub)), lcCap);
lcFine = Min(Min(w / nW, h / nH), lcSub);
subW = nLines * (w + s) + subMargin;

// ---------------------------------------------------------------------------
// Geometry
// ---------------------------------------------------------------------------
Box(1) = {-subW/2, -L/2, 0, subW, L, h};
Box(2) = {-subW/2 - airSide, -L/2 - airSide, 0, subW + 2*airSide, L + 2*airSide, h + airH};
sCut() = {};
For k In {1 : nLines}
  xk = (k - (nLines + 1)/2) * (w + s);
  Rectangle(100 + 10*k) = {xk - w/2, -L/2, h, w, L};
  // Port rectangles: drawn in the xy plane, rotated into the xz plane.
  Rectangle(101 + 10*k) = {xk - w/2, 0, 0, w, h};
  Rotate {{1, 0, 0}, {0, 0, 0}, Pi/2} { Surface{101 + 10*k}; }
  Translate {0, -L/2, 0} { Surface{101 + 10*k}; }
  Rectangle(102 + 10*k) = {xk - w/2, 0, 0, w, h};
  Rotate {{1, 0, 0}, {0, 0, 0}, Pi/2} { Surface{102 + 10*k}; }
  Translate {0, L/2, 0} { Surface{102 + 10*k}; }
  sCut() += {100 + 10*k, 101 + 10*k, 102 + 10*k};
EndFor

BooleanFragments{ Volume{2}; Delete; }{ Volume{1}; Surface{sCut()}; Delete; }

// ---------------------------------------------------------------------------
// Physical groups (identified by bounding boxes)
// ---------------------------------------------------------------------------
eps = 1e-4 * h;
vAll() = Volume{:};
vSub() = Volume In BoundingBox{-subW/2 - eps, -L/2 - eps, -eps, subW/2 + eps, L/2 + eps, h + eps};
vAir() = vAll();
vAir() -= vSub();

sGnd() = Surface In BoundingBox{-subW/2 - eps, -L/2 - eps, -eps, subW/2 + eps, L/2 + eps, eps};
sOuter() = CombinedBoundary{ Volume{vAll()}; };
sOuter() -= sGnd();
sTrace() = {};
sPorts() = {};
For k In {1 : nLines}
  xk = (k - (nLines + 1)/2) * (w + s);
  sTrace() += Surface In BoundingBox{xk - w/2 - eps, -L/2 - eps, h - eps, xk + w/2 + eps, L/2 + eps, h + eps};
  sNear() = Surface In BoundingBox{xk - w/2 - eps, -L/2 - eps, -eps, xk + w/2 + eps, -L/2 + eps, h + eps};
  sFar() = Surface In BoundingBox{xk - w/2 - eps, L/2 - eps, -eps, xk + w/2 + eps, L/2 + eps, h + eps};
  Physical Surface(Sprintf("Port%g", 2*k - 1), 20 + 2*k - 1) = {sNear()};
  Physical Surface(Sprintf("Port%g", 2*k), 20 + 2*k) = {sFar()};
  sPorts() += {sNear(), sFar()};
  sOuter() -= sNear();
  sOuter() -= sFar();
EndFor

Physical Volume("Air", 1) = {vAir()};
Physical Volume("Substrate", 2) = {vSub()};
Physical Surface("PEC_Ground", 11) = {sGnd()};
Physical Surface("PEC_Trace", 12) = {sTrace()};
Physical Surface("OuterBoundary", 13) = {sOuter()};

// ---------------------------------------------------------------------------
// Mesh size
// ---------------------------------------------------------------------------
Mesh.MeshSizeExtendFromBoundary = 0;
Mesh.MeshSizeFromPoints = 0;
Mesh.MeshSizeFromCurvature = 0;
Mesh.MeshSizeMin = lcFine;
Mesh.MeshSizeMax = lcAir;

// Refinement around the traces and the ports: lcFine up to a distance h, then
// linear growth (slope growth - 1) up to lcAir.
Field[1] = Distance;
Field[1].SurfacesList = {sTrace(), sPorts()};
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
Field[4] = Min;
Field[4].FieldsList = {2, 3};
Background Field = 4;

Mesh.Algorithm3D = 1;   // Delaunay
Mesh.Optimize = 1;
Mesh.OptimizeNetgen = 1;
Mesh.MshFileVersion = 2.2;
