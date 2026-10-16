// Case 3B: Multilayer dielectric cavity
//
// 2026-09-28 redesign (32 GB / 10 min per solve budget, PPW >= 6): cavity
// 1.2*lambda0 (was 2), 6 / 18 layers (was 10 / 50), each layer meshed for its
// own local wavelength (lc = lambda0/sqrt(eps)/8) but never coarser than the
// layer thickness (avoids flat elements between closely spaced interfaces).
SetFactory("OpenCASCADE");

lambda0 = 1.0;
Lx = 1.2 * lambda0;
Ly = 1.2 * lambda0;
Lz = 1.2 * lambda0;
Nlayer = 6; // 6, 18

lcAir = 0.125;       // lambda0/8
lcPTFE = 0.0863;     // lambda0/sqrt(2.1)/8
lcAlumina = 0.0399;  // lambda0/sqrt(9.8)/8

hz = Lz / Nlayer;
lcA = Min(lcAir, hz);
lcP = Min(lcPTFE, hz);
lcL = Min(lcAlumina, hz);

Mesh.CharacteristicLengthMin = lcL;
Mesh.CharacteristicLengthMax = lcA;
Mesh.CharacteristicLengthExtendFromBoundary = 0;
Mesh.CharacteristicLengthFromPoints = 0;
Mesh.CharacteristicLengthFromCurvature = 0;

matAir[] = {};
matPTFE[] = {};
matAlumina[] = {};
For i In {0:Nlayer-1}
  id = i + 1;
  zi = -Lz/2 + i * hz;
  Box(id) = {-Lx/2, -Ly/2, zi, Lx, Ly, hz};
  // Alternating material assignment: 0->Air, 1->PTFE, 2->Alumina
  If (i % 3 == 0)
    matAir[] += {id};
  ElseIf (i % 3 == 1)
    matPTFE[] += {id};
  Else
    matAlumina[] += {id};
  EndIf
EndFor
Coherence;

// Per-material sizes (interfaces take the finer size via Min).
Field[1] = Constant; Field[1].VIn = lcP; Field[1].VOut = lcA;
Field[1].VolumesList = {matPTFE[]}; Field[1].IncludeBoundary = 1;
Field[2] = Constant; Field[2].VIn = lcL; Field[2].VOut = lcA;
Field[2].VolumesList = {matAlumina[]}; Field[2].IncludeBoundary = 1;
Field[3] = Min; Field[3].FieldsList = {1, 2};
Background Field = 3;

Physical Volume("Air") = {matAir[]};
Physical Volume("PTFE") = {matPTFE[]};
Physical Volume("Alumina") = {matAlumina[]};
Physical Surface("PEC") = {CombinedBoundary{Volume{1:Nlayer};}};
