// Case 1B: High-permittivity sphere Mie scattering with 6-directional PML
//
// 2026-09-28 redesign (32 GB / 10 min per solve budget, PPW >= 6):
// lambda0 = 1 (k0 = 2*pi), R = 0.3*lambda0 (k0R = 1.885, k0R*sqrt(eps) = 3.8 ..
// 9.4 for eps = 4 .. 25: the sphere supports internal Mie modes), core box
// L = 1.6, PML 0.5. Sphere interior sized for its own wavelength
// lambda0/sqrt(eps), air for lambda0 (lc = local wavelength / 8).
SetFactory("OpenCASCADE");

lambda0 = 1.0;
L = 1.6 * lambda0;
R = 0.3 * lambda0;
tPML = 0.5 * lambda0;
epsSphere = 10.0; // 4, 10, 15, 25

lcSphere = 0.0395;
lcAir = 0.125;

Mesh.CharacteristicLengthMin = lcSphere;
Mesh.CharacteristicLengthMax = lcAir;
Mesh.CharacteristicLengthExtendFromBoundary = 0;
Mesh.CharacteristicLengthFromPoints = 0;
Mesh.CharacteristicLengthFromCurvature = 0;

// Core region: air box with embedded dielectric sphere
Box(1) = {-L/2, -L/2, -L/2, L, L, L};
Sphere(2) = {0, 0, 0, R};
core_air[] = BooleanDifference{ Volume{1}; Delete; }{ Volume{2}; };

Box(10) = {L/2, -L/2-tPML, -L/2-tPML, tPML, L+2*tPML, L+2*tPML};
Box(11) = {-L/2-tPML, -L/2-tPML, -L/2-tPML, tPML, L+2*tPML, L+2*tPML};
Box(12) = {-L/2, L/2, -L/2-tPML, L, tPML, L+2*tPML};
Box(13) = {-L/2, -L/2-tPML, -L/2-tPML, L, tPML, L+2*tPML};
Box(14) = {-L/2, -L/2, L/2, L, L, tPML};
Box(15) = {-L/2, -L/2, -L/2-tPML, L, L, tPML};

Coherence;

// Sphere interior at lcSphere (boundary included), lcAir elsewhere.
Field[1] = Constant;
Field[1].VIn = lcSphere;
Field[1].VOut = lcAir;
Field[1].VolumesList = {2};
Field[1].IncludeBoundary = 1;
Background Field = 1;

Physical Volume("CoreAir") = {core_air[]};
Physical Volume("SphereDielectric") = {2};
Physical Volume("PML_X_Plus") = {10};
Physical Volume("PML_X_Minus") = {11};
Physical Volume("PML_Y_Plus") = {12};
Physical Volume("PML_Y_Minus") = {13};
Physical Volume("PML_Z_Plus") = {14};
Physical Volume("PML_Z_Minus") = {15};

// Outer face of the PML shell only (PEC-backed in the solver).
H = L/2 + tPML;
sOut[] = Surface In BoundingBox{-H-1e-6, -H-1e-6, -H-1e-6, H+1e-6, H+1e-6, -H+1e-6};
sOut[] += Surface In BoundingBox{-H-1e-6, -H-1e-6, H-1e-6, H+1e-6, H+1e-6, H+1e-6};
sOut[] += Surface In BoundingBox{-H-1e-6, -H-1e-6, -H-1e-6, H+1e-6, -H+1e-6, H+1e-6};
sOut[] += Surface In BoundingBox{-H-1e-6, H-1e-6, -H-1e-6, H+1e-6, H+1e-6, H+1e-6};
sOut[] += Surface In BoundingBox{-H-1e-6, -H-1e-6, -H-1e-6, -H+1e-6, H+1e-6, H+1e-6};
sOut[] += Surface In BoundingBox{H-1e-6, -H-1e-6, -H-1e-6, H+1e-6, H+1e-6, H+1e-6};
Physical Surface("OuterBoundary") = {sOut[]};
