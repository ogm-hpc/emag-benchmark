// Case 3F: Mosaic-material cavity (Air / PTFE / Alumina / HighK / Lossy cells)
//
// 2026-09-28 redesign (32 GB / 10 min per solve budget, PPW >= 6):
//  * MESH BUG FIXED: sizes used to be set with MeshSize{PointsOf{...}} while
//    Mesh.CharacteristicLengthFromPoints = 0 (ignored -> the three parameter
//    sets produced the same uniform lcCoarse mesh, PPW ~0.5 in HighK).
//    Sizes are now imposed per cell group with Constant fields.
//  * Cavity 0.32*lambda0 (was 2): keeps kappa up to 150 within ~0.1M DOF.
//  * ONE sizing layout for all parameter sets: cells are sized from the vloss=0
//    layout with the largest kappa (kappaMesh), and every cell that is lossy in
//    any set gets the lossy-material size too. The meshes of all sets are
//    therefore generated with identical geometry and size fields; only the
//    physical (material) tags differ.
//  * The lossy cells' loss tangent is the tanDelta parameter (the solver used to
//    take vloss -- the lossy VOLUME FRACTION -- as the loss tangent).
SetFactory("OpenCASCADE");

lambda0 = 1.0;
L = 0.32 * lambda0;
Nx = 6;
Ny = 6;
Nz = 6;

kappa = 100.0;  // 10, 100, 150 (material; used by the solver)
vloss = 0.10;   // lossy volume fraction: 0, 0.10, 0.20

// Sizing (common to all sets): lambda_local/8, capped by the cell size.
lcHighK = 0.0108;   // ~lambda0/sqrt(kappaMesh=150)/8 (measured PPW 6.1 at kappa=150)
lcAlumina = 0.0399; // lambda0/sqrt(9.8)/8
lcLossy = 0.0395;   // lambda0/sqrt(10)/8
lcPTFE = 0.0863;    // lambda0/sqrt(2.1)/8
lcAir = 0.125;      // lambda0/8
vlossMesh = 0.20;   // largest lossy fraction over the parameter sets

hx = L / Nx;
hy = L / Ny;
hz = L / Nz;
hc = Min(hx, Min(hy, hz));

Mesh.CharacteristicLengthMin = lcHighK;
Mesh.CharacteristicLengthMax = Min(lcAir, hc);
Mesh.CharacteristicLengthExtendFromBoundary = 0;
Mesh.CharacteristicLengthFromPoints = 0;
Mesh.CharacteristicLengthFromCurvature = 0;

matAir[] = {};
matPTFE[] = {};
matAlumina[] = {};
matHighK[] = {};
matLossy[] = {};
szHighK[] = {};    // sizing groups (layout-independent)
szAlumina[] = {};
szLossy[] = {};
szPTFE[] = {};

id = 1;
numCell = Nx * Ny * Nz;
numLossy = Floor(vloss * numCell);
numLossyMesh = Floor(vlossMesh * numCell);
count = 0;
For i In {0:Nx-1}
  For j In {0:Ny-1}
    For k In {0:Nz-1}
      Box(id) = {-L/2 + i * hx, -L/2 + j * hy, -L/2 + k * hz, hx, hy, hz};
      m = (2*i + 3*j + 5*k) % 4;
      // material layout of THIS parameter set: the first numLossy cells are lossy
      If (count < numLossy)
        matLossy[] += {id};
      ElseIf (m == 0)
        matAir[] += {id};
      ElseIf (m == 1)
        matPTFE[] += {id};
      ElseIf (m == 2)
        matAlumina[] += {id};
      Else
        matHighK[] += {id};
      EndIf
      // sizing groups: union over all parameter sets
      If (m == 3)
        szHighK[] += {id};
      ElseIf (m == 2)
        szAlumina[] += {id};
      ElseIf (count < numLossyMesh)
        szLossy[] += {id};
      ElseIf (m == 1)
        szPTFE[] += {id};
      EndIf
      id += 1;
      count += 1;
    EndFor
  EndFor
EndFor
Coherence;

lcMax = Min(lcAir, hc);
Field[1] = Constant; Field[1].VIn = lcHighK; Field[1].VOut = lcMax;
Field[1].VolumesList = {szHighK[]}; Field[1].IncludeBoundary = 1;
Field[2] = Constant; Field[2].VIn = Min(lcAlumina, hc); Field[2].VOut = lcMax;
Field[2].VolumesList = {szAlumina[]}; Field[2].IncludeBoundary = 1;
Field[3] = Constant; Field[3].VIn = Min(lcLossy, hc); Field[3].VOut = lcMax;
Field[3].VolumesList = {szLossy[]}; Field[3].IncludeBoundary = 1;
Field[4] = Constant; Field[4].VIn = Min(lcPTFE, hc); Field[4].VOut = lcMax;
Field[4].VolumesList = {szPTFE[]}; Field[4].IncludeBoundary = 1;
Field[5] = Min; Field[5].FieldsList = {1, 2, 3, 4};
Background Field = 5;

If (#matAir[] > 0)
  Physical Volume("Air") = {matAir[]};
EndIf
Physical Volume("PTFE") = {matPTFE[]};
Physical Volume("Alumina") = {matAlumina[]};
Physical Volume("HighK") = {matHighK[]};
If (#matLossy[] > 0)
  Physical Volume("Lossy") = {matLossy[]};
EndIf
Physical Surface("PEC") = {CombinedBoundary{Volume{1:id-1};}};
