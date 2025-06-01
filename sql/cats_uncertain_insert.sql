-- _dict
UPDATE _dict SET dict = add(dict, '
w1=1:0.5;     w1=2:0.5;
w2=1:0.7;     w2=2:0.2;     w2=3:0.1;
w3=1:0.25;    w3=2:0.25;    w3=3:0.25;    w3=4:0.25;
w4=1:0.6;     w4=2:0.4;
w5=1:0.5;     w5=2:0.5;

p1=1:0.5;     p1=2:0.5;
p2=1:0.4;     p2=2:0.3;     p2=3:0.3;
p3=1:0.25;    p3=2:0.25;    p3=3:0.25;    p3=4:0.25;
p4=1:0.6;     p4=2:0.4;
p5=1:0.7;     p5=2:0.3;

c1=1:0.6;     c1=2:0.4;
c2=1:0.5;     c2=2:0.5;
c3=1:0.25;    c3=2:0.25;    c3=3:0.25;    c3=4:0.25;
c4=1:0.3;     c4=2:0.3;     c4=3:0.4;
c5=1:0.8;     c5=2:0.2;

o1=1:0.5;     o1=2:0.5;
o2=1:0.3;     o2=2:0.3;     o2=3:0.4;
o3=1:0.25;    o3=2:0.25;    o3=3:0.25;    o3=4:0.25;
o4=1:0.6;     o4=2:0.4;
o5=1:0.7;     o5=2:0.3;
')
WHERE name = 'mydict';


INSERT INTO witnessed VALUES
(1,'alice','luna','siamese','white',5,Bdd('w1=1')),
(1,'alice','luna','tabby','gray',6,Bdd('w1=2')),
(2,'ben','max','mainecoon','black',2,Bdd('w2=1')),
(2,'ben','max','mainecoon','gray',4,Bdd('w2=2')),
(2,'ben','max','persian','gray',3,Bdd('w2=3')),
(3,'cathy','bella','persian','white',13,Bdd('w3=1')),
(3,'cathy','bella','persian','black',12,Bdd('w3=2')),
(3,'cathy','bella','tabby','white',15,Bdd('w3=3')),
(3,'cathy','bella','siamese','white',14,Bdd('w3=4')),
(4,'dan','oreo','mainecoon','black',7,Bdd('w4=1')),
(4,'dan','oreo','mainecoon','gray',8,Bdd('w4=2')),
(5,'erin','milo','tabby','orange',1,Bdd('w5=1')),
(5,'erin','milo','tabby','gray',3,Bdd('w5=2'));


INSERT INTO plays VALUES
(1,'frank','luna','siamese','white',6,Bdd('p1=1')),
(1,'frank','luna','tabby','gray',7,Bdd('p1=2')),
(2,'grace','max','mainecoon','black',2,Bdd('p2=1')),
(2,'grace','max','mainecoon','gray',3,Bdd('p2=2')),
(2,'grace','max','persian','gray',4,Bdd('p2=3')),
(3,'henry','bella','persian','white',12,Bdd('p3=1')),
(3,'henry','bella','persian','black',13,Bdd('p3=2')),
(3,'henry','bella','tabby','white',11,Bdd('p3=3')),
(3,'henry','bella','siamese','white',14,Bdd('p3=4')),
(4,'isla','oreo','mainecoon','black',9,Bdd('p4=1')),
(4,'isla','oreo','mainecoon','gray',10,Bdd('p4=2')),
(5,'jack','milo','tabby','orange',1,Bdd('p5=1')),
(5,'jack','milo','tabby','gray',2,Bdd('p5=2'));


INSERT INTO cares VALUES
(1,'karen','bella','persian','white',13,Bdd('c1=1')),
(1,'karen','bella','persian','black',14,Bdd('c1=2')),
(2,'leo','oreo','mainecoon','black',7,Bdd('c2=1')),
(2,'leo','oreo','mainecoon','gray',9,Bdd('c2=2')),
(3,'mia','max','persian','white',2,Bdd('c3=1')),
(3,'mia','max','tabby','white',4,Bdd('c3=2')),
(3,'mia','max','siamese','white',5,Bdd('c3=3')),
(3,'mia','max','siamese','gray',3,Bdd('c3=4')),
(4,'noah','luna','siamese','white',6,Bdd('c4=1')),
(4,'noah','luna','tabby','gray',8,Bdd('c4=2')),
(4,'noah','luna','mainecoon','gray',7,Bdd('c4=3')),
(5,'olivia','milo','tabby','orange',1,Bdd('c5=1')),
(5,'olivia','milo','tabby','gray',2,Bdd('c5=2'));


INSERT INTO owns VALUES
(1,'paul','luna','siamese','white',6,Bdd('o1=1')),
(1,'paul','luna','tabby','gray',7,Bdd('o1=2')),
(2,'quinn','max','mainecoon','black',3,Bdd('o2=1')),
(2,'quinn','max','mainecoon','gray',4,Bdd('o2=2')),
(2,'quinn','max','persian','gray',5,Bdd('o2=3')),
(3,'rachel','bella','persian','white',15,Bdd('o3=1')),
(3,'rachel','bella','persian','black',12,Bdd('o3=2')),
(3,'rachel','bella','tabby','white',13,Bdd('o3=3')),
(3,'rachel','bella','siamese','white',14,Bdd('o3=4')),
(4,'sam','oreo','mainecoon','black',8,Bdd('o4=1')),
(4,'sam','oreo','mainecoon','gray',9,Bdd('o4=2')),
(5,'tina','milo','tabby','orange',1,Bdd('o5=1')),
(5,'tina','milo','tabby','gray',2,Bdd('o5=2'));
