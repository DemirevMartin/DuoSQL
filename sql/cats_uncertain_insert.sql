INSERT INTO _dict(name,dict) VALUES ('cats_short',dictionary('
w1=1:0.5;     w1=2:0.5;
w2=1:0.7;     w2=2:0.3;
w3=1:1.0;
w4=1:1.0;
w5=1:0.5;     w5=2:0.5;

p1=1:0.5;     p1=2:0.5;
p2=1:0.4;     p2=2:0.6;
p3=1:1.0;
p4=1:1.0;
p5=1:0.7;     p5=2:0.3;

c1=1:0.6;     c1=2:0.4;
c2=1:0.5;     c2=2:0.5;
c3=1:1.0;
c4=1:1.0;
c5=1:0.8;     c5=2:0.2;

o1=1:0.5;     o1=2:0.5;
o2=1:0.3;     o2=2:0.7;
o3=1:1.0;
o4=1:1.0;
o5=1:0.7;     o5=2:0.3;
'));


INSERT INTO witnessed VALUES
(1,'alice','luna','siamese','white',5,Bdd('w1=1')),
(1,'alice','luna','tabby','gray',6,Bdd('w1=2')),
(2,'ben','max','mainecoon','black',2,Bdd('w2=1')),
(2,'ben','max','mainecoon','gray',4,Bdd('w2=2')),
(3,'cathy','bella','persian','white',13,Bdd('w3=1'));

INSERT INTO plays VALUES
(1,'frank','luna','siamese','white',6,Bdd('p1=1')),
(1,'frank','luna','tabby','gray',7,Bdd('p1=2')),
(2,'grace','max','mainecoon','black',2,Bdd('p2=1')),
(2,'grace','max','mainecoon','gray',3,Bdd('p2=2')),
(3,'henry','bella','persian','white',12,Bdd('p3=1'));

INSERT INTO cares VALUES
(1,'karen','bella','persian','white',13,Bdd('c1=1')),
(1,'karen','bella','persian','black',14,Bdd('c1=2')),
(2,'leo','oreo','mainecoon','black',7,Bdd('c2=1')),
(2,'leo','oreo','mainecoon','gray',9,Bdd('c2=2')),
(3,'mia','max','persian','white',2,Bdd('c3=1'));

INSERT INTO owns VALUES
(1,'paul','luna','siamese','white',6,Bdd('o1=1')),
(1,'paul','luna','tabby','gray',7,Bdd('o1=2')),
(2,'quinn','max','mainecoon','black',3,Bdd('o2=1')),
(2,'quinn','max','mainecoon','gray',4,Bdd('o2=2')),
(3,'rachel','bella','persian','white',15,Bdd('o3=1'));
