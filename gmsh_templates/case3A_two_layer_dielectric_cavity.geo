// Case 3A: Two-layer dielectric cavity
//
// 2026-09-28 redesign (32 GB / 10 min per solve budget, PPW >= 6): keeping the
// contrast kappa = 100 at the old 2*lambda0 cavity would need ~10M DOF, so the
// cavity is shrunk to 0.4*lambda0 (= lowering the frequency; the kappa=100
// layer is still ~2 local wavelengths thick). All parameter sets share ONE
// mesh sized for kappa = 100 (lcLayer2 = lambda0/sqrt(100)/8), so the sets
// differ only in the material coefficient.
SetFactory("OpenCASCADE");

lambda0 = 1.0;
Lx = 0.4 * lambda0;
Ly = 0.4 * lambda0;
Lz = 0.4 * lambda0;

lcLayer2 = 0.0125;  // high-contrast (z > 0) layer
lcLayer1 = 0.125;   // air layer (z < 0)

Mesh.CharacteristicLengthMin = lcLayer2;
Mesh.CharacteristicLengthMax = lcLayer1;
Mesh.CharacteristicLengthExtendFromBoundary = 0;
Mesh.CharacteristicLengthFromPoints = 0;
Mesh.CharacteristicLengthFromCurvature = 0;

Box(1) = {-Lx/2, -Ly/2, -Lz/2, Lx, Ly, Lz/2};
Box(2) = {-Lx/2, -Ly/2, 0,     Lx, Ly, Lz/2};
Coherence;

// lcLayer2 inside Layer2 (interface included), lcLayer1 elsewhere.
Field[1] = Constant;
Field[1].VIn = lcLayer2;
Field[1].VOut = lcLayer1;
Field[1].VolumesList = {2};
Field[1].IncludeBoundary = 1;
Background Field = 1;

Physical Volume("Layer1_AirOrPTFE") = {1};
Physical Volume("Layer2_CeramicOrHighK") = {2};
Physical Surface("PEC") = {CombinedBoundary{Volume{1,2};}};
