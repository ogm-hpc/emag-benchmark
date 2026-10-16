// Case 1A: PEC sphere scattering with 6-directional PML layers
SetFactory("OpenCASCADE");

// Geometry scale
lambda0 = 1.0;
L = 10.0;
R = 1.0;
tPML = 1.0; // 0.5, 1.0, 2.0

// Mesh size
lc = 0.125;
Mesh.CharacteristicLengthMin = lc;
Mesh.CharacteristicLengthMax = lc;

// Inner computational box (air region with PEC sphere)
Box(1) = {-L/2, -L/2, -L/2, L, L, L};
Sphere(2) = {0, 0, 0, R};

// Remove PEC sphere from air region
air[] = BooleanDifference{ Volume{1}; Delete; }{ Volume{2}; Delete; };

// Create 6 PML layers (slab-based, axis-aligned)
// PML_X_Plus: x in [L/2, L/2 + tPML]
Box(10) = {L/2, -L/2-tPML, -L/2-tPML, tPML, L+2*tPML, L+2*tPML};
// PML_X_Minus: x in [-L/2-tPML, -L/2]
Box(11) = {-L/2-tPML, -L/2-tPML, -L/2-tPML, tPML, L+2*tPML, L+2*tPML};
// PML_Y_Plus: y in [L/2, L/2 + tPML]
Box(12) = {-L/2, L/2, -L/2-tPML, L, tPML, L+2*tPML};
// PML_Y_Minus: y in [-L/2-tPML, -L/2]
Box(13) = {-L/2, -L/2-tPML, -L/2-tPML, L, tPML, L+2*tPML};
// PML_Z_Plus: z in [L/2, L/2 + tPML]
Box(14) = {-L/2, -L/2, L/2, L, L, tPML};
// PML_Z_Minus: z in [-L/2-tPML, -L/2]
Box(15) = {-L/2, -L/2, -L/2-tPML, L, L, tPML};

Coherence;

Physical Volume("CoreAir") = {air[]};
Physical Volume("PML_X_Plus") = {10};
Physical Volume("PML_X_Minus") = {11};
Physical Volume("PML_Y_Plus") = {12};
Physical Volume("PML_Y_Minus") = {13};
Physical Volume("PML_Z_Plus") = {14};
Physical Volume("PML_Z_Minus") = {15};

// Boundaries
Physical Surface("PEC_Sphere") = {Boundary{Volume{air[]};}};
