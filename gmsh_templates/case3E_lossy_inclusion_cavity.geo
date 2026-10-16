// Case 3E: Lossy-material inclusion (eps_r = epsLossy*(1 - i tan(delta))) in a PEC cavity
//
// 2026-09-28: graded mesh -- the inclusion is meshed for its own wavelength
// lambda0/sqrt(epsLossy) (it used to share the air's uniform lc, PPW ~3.6
// inside), the air for lambda0 (lc = local wavelength / 8). The solver now
// also applies epsLossy to this region (it used to be left at eps_r = 1).
SetFactory("OpenCASCADE");

lambda0 = 1.0;
L = 2.0 * lambda0;
Lin = 0.8 * lambda0;

epsLossy = 10.0;
tanDelta = 0.1; // 0.01, 0.1, 1.0

lcIn = 0.0395;  // lambda0/sqrt(10)/8
lcAir = 0.125;  // lambda0/8
Mesh.CharacteristicLengthMin = lcIn;
Mesh.CharacteristicLengthMax = lcAir;
Mesh.CharacteristicLengthExtendFromBoundary = 0;
Mesh.CharacteristicLengthFromPoints = 0;
Mesh.CharacteristicLengthFromCurvature = 0;

Box(1) = {-L/2, -L/2, -L/2, L, L, L};
Box(2) = {-Lin/2, -Lin/2, -Lin/2, Lin, Lin, Lin};
air[] = BooleanDifference{ Volume{1}; Delete; }{ Volume{2}; };
Coherence;

Field[1] = Constant;
Field[1].VIn = lcIn;
Field[1].VOut = lcAir;
Field[1].VolumesList = {2};
Field[1].IncludeBoundary = 1;
Background Field = 1;

Physical Volume("BackgroundAir") = {air[]};
Physical Volume("LossyMaterial") = {2};
Physical Surface("PEC") = {CombinedBoundary{Volume{air[], 2};}};
