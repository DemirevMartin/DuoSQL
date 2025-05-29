CREATE TABLE witnessed (
    id integer,
    witness text,
    cat_name text,
    breed text,
    color text,
    age text,
    _sentence Bdd
);

CREATE TABLE plays (
    id integer,
    companion text,
    cat_name text,
    breed text,
    color text,
    age text,
    _sentence Bdd
);

CREATE TABLE cares (
    id integer,
    caretaker text,
    cat_name text,
    breed text,
    color text,
    age text,
    _sentence Bdd
);

CREATE TABLE owns (
    id integer,
    owner text,
    cat_name text,
    breed text,
    color text,
    age text,
    _sentence Bdd
);
