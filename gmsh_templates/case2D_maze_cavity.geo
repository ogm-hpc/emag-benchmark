// Case 2D: Maze-like cavity via internal PEC wall slabs
SetFactory("OpenCASCADE");

lambda0 = 1.0;
Lx = 8.0 * lambda0;
Ly = 2.0 * lambda0;
Lz = 2.0 * lambda0;
Nwall = 10; // 5, 10, 20, 40
ropen = 0.1; // 0.05, 0.10, 0.20
th = 0.03 * lambda0;

lc = 0.13 * lambda0; // 2026-09-28: mean edge ~ lambda0/6 (PPW >= 6), 10-min budget
Mesh.CharacteristicLengthMin = lc;
Mesh.CharacteristicLengthMax = lc;

Box(1) = {-Lx/2, -Ly/2, -Lz/2, Lx, Ly, Lz};

openH = ropen * Lz;
If (openH > 0.9 * Lz)
  openH = 0.9 * Lz;
EndIf
hz = (Lz - openH) / 2.0;

nextId = 2;
wallVols[] = {};
For i In {1:Nwall}
  xi = -Lx/2 + i * Lx / (Nwall + 1) - th/2;
  // Lower slab
  Box(nextId) = {xi, -Ly/2, -Lz/2, th, Ly, hz};
  wallVols[] += {nextId};
  nextId += 1;
  // Upper slab
  Box(nextId) = {xi, -Ly/2, Lz/2 - hz, th, Ly, hz};
  wallVols[] += {nextId};
  nextId += 1;
EndFor

air[] = BooleanDifference{ Volume{1}; Delete; }{ Volume{wallVols[]}; Delete; };
Coherence;

Physical Volume("Air") = {air[]};
Physical Surface("PEC") = {Boundary{Volume{air[]};}};
