CREATE TABLE p_witnessed (
    id integer,
    witness text,
    cat_name text,
    breed text,
    color text,
    age integer,
    _sentence Bdd
);

CREATE TABLE p_plays (
    id integer,
    companion text,
    cat_name text,
    breed text,
    color text,
    age integer,
    _sentence Bdd
);

CREATE TABLE p_cares (
    id integer,
    caretaker text,
    cat_name text,
    breed text,
    color text,
    age integer,
    _sentence Bdd
);

CREATE TABLE p_owns (
    id integer,
    owner text,
    cat_name text,
    breed text,
    color text,
    age integer,
    _sentence Bdd
);

CREATE TABLE p_likes (
    id integer,
    liker text,
    cat_name text,
    breed text,
    color text,
    age integer,
    _sentence Bdd
);

CREATE TABLE p_dislikes (
    id integer,
    disliker text,
    cat_name text,
    breed text,
    color text,
    age integer,
    _sentence Bdd
);


CREATE TABLE p_cat_likes (
    id integer,
    liked text,
    cat_name text,
    breed text,
    color text,
    age integer,
    _sentence Bdd
);

CREATE TABLE p_cat_dislikes (
    id integer,
    disliked text,
    cat_name text,
    breed text,
    color text,
    age integer,
    _sentence Bdd
);

------ CERTAIN ------
CREATE TABLE p_profile_certain (
    id integer,
    cat_name text
)
