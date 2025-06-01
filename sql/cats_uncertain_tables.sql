-- Columns that could be added:
    -- location (the facilities in the clinic)

-- Tables that could be added:
    -- (person) 'likes' (cat)
    -- (person) 'dislikes' (cat)
    -- (cat) 'cat_likes' (person)
    -- (cat) 'cat_dislikes' (person)


CREATE TABLE witnessed (
    id integer,
    witness text,
    cat_name text,
    breed text,
    color text,
    age integer,
    _sentence Bdd
);

CREATE TABLE plays (
    id integer,
    companion text,
    cat_name text,
    breed text,
    color text,
    age integer,
    _sentence Bdd
);

CREATE TABLE cares (
    id integer,
    caretaker text,
    cat_name text,
    breed text,
    color text,
    age integer,
    _sentence Bdd
);

CREATE TABLE owns (
    id integer,
    owner text,
    cat_name text,
    breed text,
    color text,
    age integer,
    _sentence Bdd
);
