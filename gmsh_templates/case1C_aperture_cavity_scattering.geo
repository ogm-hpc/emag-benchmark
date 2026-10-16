// Case 1C: Aperture cavity scattering with PML exterior shell
//
// 2026-09-28 redesign (32 GB / 10 min per solve budget, PPW >= 6):
// chambers Lc = 1.5*lambda0 (was 2), PML 0.5*lambda0 (was 1), lc = lambda0/8.
// The PML is an anisotropic UPML in the solver, PEC-backed on its outer face.
SetFactory("OpenCASCADE");

lambda0 = 1.0;
Lc = 1.5 * lambda0;    // chamber length (x) and cross-section edge (y, z)
w = 0.2 * lambda0;     // 0.1, 0.2, 0.5 aperture width
tSep = 0.1 * lambda0;  // septum (dividing wall) thickness
tPML = 0.5 * lambda0;  // PML thickness

lc = lambda0 / 8.0;
Mesh.CharacteristicLengthMin = lc;
Mesh.CharacteristicLengthMax = lc;

// Two chambers separated by a septum of thickness tSep and connected only
// through a w x w aperture duct bridging the gap.
Box(1) = {-Lc, -Lc/2, -Lc/2, Lc - tSep/2, Lc, Lc};
Box(2) = {tSep/2, -Lc/2, -Lc/2, Lc - tSep/2, Lc, Lc};
Box(3) = {-tSep/2, -w/2, -w/2, tSep, w, w};
air_core[] = BooleanUnion{ Volume{1,2}; Delete; }{ Volume{3}; Delete; };

// 6 PML slabs, telescoping (same pattern as case1A/1B).
Box(10) = {Lc, -Lc/2-tPML, -Lc/2-tPML, tPML, Lc+2*tPML, Lc+2*tPML};
Box(11) = {-Lc-tPML, -Lc/2-tPML, -Lc/2-tPML, tPML, Lc+2*tPML, Lc+2*tPML};
Box(12) = {-Lc, Lc/2, -Lc/2-tPML, 2*Lc, tPML, Lc+2*tPML};
Box(13) = {-Lc, -Lc/2-tPML, -Lc/2-tPML, 2*Lc, tPML, Lc+2*tPML};
Box(14) = {-Lc, -Lc/2, Lc/2, 2*Lc, Lc, tPML};
Box(15) = {-Lc, -Lc/2, -Lc/2-tPML, 2*Lc, Lc, tPML};

Coherence;

Physical Volume("CoreAir") = {air_core[]};
Physical Volume("PML_X_Plus") = {10};
Physical Volume("PML_X_Minus") = {11};
Physical Volume("PML_Y_Plus") = {12};
Physical Volume("PML_Y_Minus") = {13};
Physical Volume("PML_Z_Plus") = {14};
Physical Volume("PML_Z_Minus") = {15};

// The only true PEC surface inside is the septum (its two Lc x Lc faces minus
// the aperture hole, plus the duct walls). Faces of the core touching the PML
// stay untagged (the wave transmits into the PML).
Physical Surface("PEC_Cavity") = Surface In BoundingBox{-tSep/2-1e-6, -Lc/2-1e-6, -Lc/2-1e-6, tSep/2+1e-6, Lc/2+1e-6, Lc/2+1e-6};

// Outer face of the PML shell (PEC-backed in the solver).
X = Lc + tPML; Y = Lc/2 + tPML;
sOut[] = Surface In BoundingBox{-X-1e-6, -Y-1e-6, -Y-1e-6, X+1e-6, Y+1e-6, -Y+1e-6};
sOut[] += Surface In BoundingBox{-X-1e-6, -Y-1e-6, Y-1e-6, X+1e-6, Y+1e-6, Y+1e-6};
sOut[] += Surface In BoundingBox{-X-1e-6, -Y-1e-6, -Y-1e-6, X+1e-6, -Y+1e-6, Y+1e-6};
sOut[] += Surface In BoundingBox{-X-1e-6, Y-1e-6, -Y-1e-6, X+1e-6, Y+1e-6, Y+1e-6};
sOut[] += Surface In BoundingBox{-X-1e-6, -Y-1e-6, -Y-1e-6, -X+1e-6, Y+1e-6, Y+1e-6};
sOut[] += Surface In BoundingBox{X-1e-6, -Y-1e-6, -Y-1e-6, X+1e-6, Y+1e-6, Y+1e-6};
Physical Surface("OuterBoundary") = {sOut[]};
