// Case 2A: Empty PEC cavity
SetFactory("OpenCASCADE");

lambda0 = 1.0;
Lx = 4.0 * lambda0;
Ly = 2.0 * lambda0;
Lz = 2.0 * lambda0;

lc = lambda0 / 10.0;
Mesh.CharacteristicLengthMin = lc;
Mesh.CharacteristicLengthMax = lc;

Box(1) = {-Lx/2, -Ly/2, -Lz/2, Lx, Ly, Lz};

Physical Volume("Air") = {1};
Physical Surface("PEC") = {Boundary{Volume{1};}};
