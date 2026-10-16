// Case 3C: 3D checkerboard dielectric (eps_r = 1 / 100 cells) in a PEC cavity
//
// 2026-09-28 redesign (32 GB / 10 min per solve budget, PPW >= 6):
//  * MESH BUG FIXED: sizes used to be set with MeshSize{PointsOf{...}} while
//    Mesh.CharacteristicLengthFromPoints = 0, which makes gmsh ignore point
//    sizes -- the whole mesh came out uniform at lcCoarse (PPW ~0.5 in Eps100).
//    Sizes are now imposed per volume with Constant fields.
//  * Keeping eps = 100 at the old 2*lambda0 cavity would need ~10M DOF, so the
//    cavity is shrunk to 0.32*lambda0 (= lowering the frequency). In a
//    checkerboard every Eps1 face touches an Eps100 cell, so the mesh is nearly
//    uniformly fine; Nc = 4/6/8 and lcFine are set per parameter set.
SetFactory("OpenCASCADE");

lambda0 = 1.0;
L = 0.32 * lambda0;
Nc = 8; // 4, 6, 8

lcFine = 0.0125;   // Eps100: lambda0/sqrt(100)/8
lcCoarse = 0.125;  // Eps1: lambda0/8 (capped by the cell size below)

h = L / Nc;
lcC = Min(lcCoarse, h);

Mesh.CharacteristicLengthMin = lcFine;
Mesh.CharacteristicLengthMax = lcC;
Mesh.CharacteristicLengthExtendFromBoundary = 0;
Mesh.CharacteristicLengthFromPoints = 0;
Mesh.CharacteristicLengthFromCurvature = 0;

id = 1;
matA[] = {};
matB[] = {};
For i In {0:Nc-1}
  For j In {0:Nc-1}
    For k In {0:Nc-1}
      x = -L/2 + i * h;
      y = -L/2 + j * h;
      z = -L/2 + k * h;
      Box(id) = {x, y, z, h, h, h};
      If ((i + j + k) % 2 == 0)
        matA[] += {id};
      Else
        matB[] += {id};
      EndIf
      id += 1;
    EndFor
  EndFor
EndFor
Coherence;

Field[1] = Constant;
Field[1].VIn = lcFine;
Field[1].VOut = lcC;
Field[1].VolumesList = {matB[]};
Field[1].IncludeBoundary = 1;
Background Field = 1;

Physical Volume("Eps1") = {matA[]};
Physical Volume("Eps100") = {matB[]};
Physical Surface("PEC") = {CombinedBoundary{Volume{1:id-1};}};
