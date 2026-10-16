// Case 2C: Ultra-narrow slit benchmark
SetFactory("OpenCASCADE");

lambda0 = 1.0;
L = 2.0 * lambda0;
tPlate = 0.05 * lambda0;
g = lambda0 / 50.0; // lambda0/100 to lambda0/20
hSlit = 0.4 * lambda0;

lcFar = 0.13 * lambda0; // 2026-09-28: mean edge ~ lambda0/6 (PPW >= 6), 10-min budget
lcNear = g / 2.0;
Mesh.CharacteristicLengthMin = lcNear;
Mesh.CharacteristicLengthMax = lcFar;

// Two air chambers separated by slit throat
Box(1) = {-L, -L/2, -L/2, L - tPlate/2, L, L};
Box(2) = {tPlate/2, -L/2, -L/2, L - tPlate/2, L, L};
Box(3) = {-tPlate/2, -g/2, -hSlit/2, tPlate, g, hSlit};

air[] = BooleanUnion{ Volume{1,2}; Delete; }{ Volume{3}; Delete; };
Coherence;

Physical Volume("Air") = {air[]};
Physical Surface("PEC") = {Boundary{Volume{air[]};}};
