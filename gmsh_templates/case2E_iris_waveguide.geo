// Case 2E: Iris-loaded rectangular waveguide
SetFactory("OpenCASCADE");

lambda0 = 1.0;
a = 1.0 * lambda0;
b = 0.5 * lambda0;
L = 10.0 * lambda0;
p = 1.0 * lambda0; // 0.5 to 2.0
N = 10; // 5, 10, 20
tI = 0.03 * lambda0;
bI = 0.2 * b; // iris window height

lc = 0.13 * lambda0; // 2026-09-28: mean edge ~ lambda0/6 (PPW >= 6), 10-min budget
Mesh.CharacteristicLengthMin = lc;
Mesh.CharacteristicLengthMax = lc;

Box(1) = {0, -a/2, -b/2, L, a, b};

nextId = 2;
blk[] = {};
For k In {1:N}
  xk = k * p;
  If (xk > tI && xk < L - tI)
    // Bottom metal part
    Box(nextId) = {xk - tI/2, -a/2, -b/2, tI, a, (b - bI)/2};
    blk[] += {nextId};
    nextId += 1;
    // Top metal part
    Box(nextId) = {xk - tI/2, -a/2, b/2 - (b - bI)/2, tI, a, (b - bI)/2};
    blk[] += {nextId};
    nextId += 1;
  EndIf
EndFor

air[] = BooleanDifference{ Volume{1}; Delete; }{ Volume{blk[]}; Delete; };
Coherence;

Physical Volume("Air") = {air[]};
Physical Surface("PECWall") = {Boundary{Volume{air[]};}};

// Port faces (x=0 and x=L)
sIn[] = Surface In BoundingBox{-1e-6, -a/2-1e-6, -b/2-1e-6, 1e-6, a/2+1e-6, b/2+1e-6};
sOut[] = Surface In BoundingBox{L-1e-6, -a/2-1e-6, -b/2-1e-6, L+1e-6, a/2+1e-6, b/2+1e-6};
Physical Surface("PortIn") = {sIn[]};
Physical Surface("PortOut") = {sOut[]};
