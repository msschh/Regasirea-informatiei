tetrahedra d 50 image size n 1200 number of images n 40 landmarks generate n unit quaternions q randn 4 n skew to 1 q randn 4 n 1 q 1 q 1 2 q q 1 0 0 0 q q repmat sqrt sum q 2 1 4 1 create basic tetrahedron as four faces ti with normals ni tvert 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 qtvert qmult q tvert t1 qtvert 5 3 2 n1 qtvert 1 t1 1 1 1 1 1 1 1 1 1 n1 1 1 1 t2 qtvert 8 2 3 n2 qtvert 4 t2 diag 1 1 1 t1 n2 diag 1 1 1 n1 t3 qtvert 2 8 5 n3 qtvert 6 t3 diag 1 1 1 t1 n3 diag 1 1 1 n1 t4 qtvert 3 5 8 n4 qtvert 7 t4 diag 1 1 1 t1 n4 diag 1 1 1 n1 xx yy meshgrid linspace 2 2 d xx xx yy yy p zeros d 2 n uint8 for a 1 n for b 1 4 p 64 8 2 b brightness of b th face eval sprintf t t d a b t tb a face xx t 1 1 yy t 2 2 xx t 1 2 yy t 2 1 & xx t 1 2 yy t 2 3 xx t 1 3 yy t 2 2 & xx t 1 3 yy t 2 1 xx t 1 1 yy t 2 3 p face a p face a p p face a p end if mod a 25 disp a end end next step find landmarks and compute dl l 1 dl zeros n n dl 1 sqrt sum repmat p 1 1 n p 1 dlmin dl 1 while length l n foo i max dlmin lnew i 1 l l lnew dlnew sqrt sum repmat p lnew 1 n p 1 dl length l dlnew dlmin min dlmin dlnew end saveyn input save as tetrasave2 y n s if saveyn 1 y save tetrasave2 pl dl dlmin qn nd end next step build complex and compute local cohomology see tetrahedra2