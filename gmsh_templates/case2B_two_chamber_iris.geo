// Case 2B: Two-chamber cavity with iris connection
//
// 2026-09-28 fixes:
//  * GEOMETRY BUG FIXED: the chambers used to span x in [-2Lch,-Lch] and
//    [0,Lch] while the iris duct spanned only x in [-th/2,th/2], so the left
//    chamber (where the source is) was a separate, isolated closed box -- the
//    iris coupled nothing. The chambers now sit on either side of a PEC wall of
//    thickness th, bridged by the w x w iris duct (same gap+duct pattern as
//    case1C/case2C).
//  * lc = 0.13*lambda0 (mean edge ~ lambda0/6, PPW >= 6) for the 10-min budget.
SetFactory("OpenCASCADE");

lambda0 = 1.0;
Lch = 2.0 * lambda0;
w = 0.1 * lambda0; // 0.02, 0.1, 0.5
th = 0.1 * lambda0;

lc = 0.13 * lambda0;
Mesh.CharacteristicLengthMin = lc;
Mesh.CharacteristicLengthMax = lc;

// Left and right chambers, separated by the wall |x| < th/2
Box(1) = {-Lch - th/2, -Lch/2, -Lch/2, Lch, Lch, Lch};
Box(2) = {th/2, -Lch/2, -Lch/2, Lch, Lch, Lch};
// Iris duct through the wall
Box(3) = {-th/2, -w/2, -w/2, th, w, w};

air[] = BooleanUnion{ Volume{1,2}; Delete; }{ Volume{3}; Delete; };
Coherence;

Physical Volume("Air") = {air[]};
Physical Surface("PEC") = {Boundary{Volume{air[]};}};
