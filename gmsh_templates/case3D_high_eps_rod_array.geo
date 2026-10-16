// Case 3D: High-epsilon (eps_r = 50) rod array in a PEC box
//
// 2026-09-28 redesign (32 GB / 10 min per solve budget, PPW >= 6):
//  * MESH BUG FIXED: rod/air sizes were set with MeshSize{PointsOf{...}} while
//    Mesh.CharacteristicLengthFromPoints = 0 (ignored -> uniform lcAir mesh,
//    PPW ~0.8 inside the rods). Sizes are now imposed with a Constant field.
//  * The whole geometry is scaled by 0.16 (R, p, Hz, margin), which keeps the
//    5x5 / 10x10 array topology and eps = 50 within ~0.12M DOF.
SetFactory("OpenCASCADE");

lambda0 = 1.0;
R = 0.032 * lambda0;
p = 0.08 * lambda0;
Nx = 5; // 5 or 10
Ny = 5; // 5 or 10
Hz = 0.16 * lambda0;
margin = 0.08 * lambda0;

Lx = (Nx - 1) * p + 2 * (R + margin);
Ly = (Ny - 1) * p + 2 * (R + margin);
Lz = Hz;

lcRod = 0.0177; // lambda0/sqrt(50)/8
lcAir = 0.125;  // lambda0/8

Mesh.CharacteristicLengthMin = lcRod;
Mesh.CharacteristicLengthMax = lcAir;
Mesh.CharacteristicLengthExtendFromBoundary = 0;
Mesh.CharacteristicLengthFromPoints = 0;
Mesh.CharacteristicLengthFromCurvature = 0;

Box(1) = {-Lx/2, -Ly/2, -Lz/2, Lx, Ly, Lz};
rid = 2;
rods[] = {};
For i In {0:Nx-1}
  For j In {0:Ny-1}
    cx = -((Nx - 1) * p)/2 + i * p;
    cy = -((Ny - 1) * p)/2 + j * p;
    Cylinder(rid) = {cx, cy, -Lz/2, 0, 0, Lz, R, 2*Pi};
    rods[] += {rid};
    rid += 1;
  EndFor
EndFor
air[] = BooleanDifference{ Volume{1}; Delete; }{ Volume{rods[]}; };
Coherence;

Field[1] = Constant;
Field[1].VIn = lcRod;
Field[1].VOut = lcAir;
Field[1].VolumesList = {rods[]};
Field[1].IncludeBoundary = 1;
Background Field = 1;

Physical Volume("Air") = {air[]};
Physical Volume("RodsHighEps") = {rods[]};
Physical Surface("PEC") = {CombinedBoundary{Volume{air[], rods[]};}};
