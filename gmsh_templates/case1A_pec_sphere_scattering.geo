// Case 1A: PEC sphere scattering with 6-directional PML layers
//
// 2026-09-28 redesign (32 GB / 10 min per solve budget, PPW >= 6):
// lambda0 = 1 (k0 = 2*pi) for every parameter set; the electrical size of the
// scatterer is set by R (k0R = 2*pi*R) and the core box by L (air gap L/2-R).
// The PML is an anisotropic UPML in the solver (coordinate-based stretching
// outside the core box), backed by PEC on its outer face ("OuterBoundary").
SetFactory("OpenCASCADE");

// Geometry scale
lambda0 = 1.0;
L = 2.0 * lambda0;      // core (air) box edge
R = 0.5 * lambda0;      // PEC sphere radius
tPML = 0.5 * lambda0;   // PML thickness

// Mesh size: lc = lambda0/8 gives a mean edge ~ lambda0/6 (PPW >= 6)
lc = lambda0 / 8.0;
Mesh.CharacteristicLengthMin = lc;
Mesh.CharacteristicLengthMax = lc;

// Inner computational box (air region with PEC sphere)
Box(1) = {-L/2, -L/2, -L/2, L, L, L};
Sphere(2) = {0, 0, 0, R};
air[] = BooleanDifference{ Volume{1}; Delete; }{ Volume{2}; Delete; };

// 6 PML slabs, telescoping (non-overlapping): X-slabs span the full extended
// y,z; Y-slabs extend only in z; Z-slabs don't extend.
Box(10) = {L/2, -L/2-tPML, -L/2-tPML, tPML, L+2*tPML, L+2*tPML};
Box(11) = {-L/2-tPML, -L/2-tPML, -L/2-tPML, tPML, L+2*tPML, L+2*tPML};
Box(12) = {-L/2, L/2, -L/2-tPML, L, tPML, L+2*tPML};
Box(13) = {-L/2, -L/2-tPML, -L/2-tPML, L, tPML, L+2*tPML};
Box(14) = {-L/2, -L/2, L/2, L, L, tPML};
Box(15) = {-L/2, -L/2, -L/2-tPML, L, L, tPML};

Coherence;

Physical Volume("CoreAir") = {air[]};
Physical Volume("PML_X_Plus") = {10};
Physical Volume("PML_X_Minus") = {11};
Physical Volume("PML_Y_Plus") = {12};
Physical Volume("PML_Y_Minus") = {13};
Physical Volume("PML_Z_Plus") = {14};
Physical Volume("PML_Z_Minus") = {15};

// PEC sphere surface (selected by bounding box: R < L/2).
Physical Surface("PEC_Sphere") = Surface In BoundingBox{-R-1e-6, -R-1e-6, -R-1e-6, R+1e-6, R+1e-6, R+1e-6};
// Outer face of the PML shell only (interfaces between slabs/core excluded).
H = L/2 + tPML;
sOut[] = Surface In BoundingBox{-H-1e-6, -H-1e-6, -H-1e-6, H+1e-6, H+1e-6, -H+1e-6};
sOut[] += Surface In BoundingBox{-H-1e-6, -H-1e-6, H-1e-6, H+1e-6, H+1e-6, H+1e-6};
sOut[] += Surface In BoundingBox{-H-1e-6, -H-1e-6, -H-1e-6, H+1e-6, -H+1e-6, H+1e-6};
sOut[] += Surface In BoundingBox{-H-1e-6, H-1e-6, -H-1e-6, H+1e-6, H+1e-6, H+1e-6};
sOut[] += Surface In BoundingBox{-H-1e-6, -H-1e-6, -H-1e-6, -H+1e-6, H+1e-6, H+1e-6};
sOut[] += Surface In BoundingBox{H-1e-6, -H-1e-6, -H-1e-6, H+1e-6, H+1e-6, H+1e-6};
Physical Surface("OuterBoundary") = {sOut[]};
