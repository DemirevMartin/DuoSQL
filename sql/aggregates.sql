-- Two PL/SQL helper functions

CREATE or REPLACE FUNCTION prob_Bdd(a_s Bdd[], mask bit)
    RETURNS Bdd
    LANGUAGE plpgsql
    AS
$$
DECLARE
    result     Bdd = Bdd('1');
    mask_len   integer = array_length(a_s, 1);
    mask_start integer = length(mask) - mask_len - 1;
    n_bdd      Bdd;
BEGIN
    FOR i IN 1 .. mask_len
    LOOP
        IF get_bit(mask,mask_start+i) = 1 THEN
            n_bdd = a_s[i];
        ELSE
            n_bdd = !a_s[i];
        END IF;
        result := result & n_bdd;
    END LOOP;
    RETURN result;
END;
$$;

CREATE or REPLACE FUNCTION prob_Bdd_count(a_b anyarray, mask bit)
    RETURNS int
    LANGUAGE plpgsql
    AS
$$
DECLARE
    result     integer = 0;
    mask_len   integer = array_length(a_b, 1);
    mask_start integer = length(mask) - mask_len - 1;
BEGIN
    FOR i IN 1 .. mask_len
    LOOP
        IF get_bit(mask,mask_start+i) = 1 THEN
            result := result + 1;
        END IF;
    END LOOP;
    RETURN result;
END;
$$;

-- This is a count on drives table with a group by on car

SELECT car, count, agg_or(_sentence) AS _sentence
FROM (
    SELECT car, prob_Bdd_count(arr,mask) AS count, prob_Bdd(arr_sentence,mask) AS _sentence, arr, arr_sentence, mask
    FROM (
        SELECT car, arr, arr_sentence, generate_series(0,(pow(2,array_length(arr_sentence,1))-1)::int)::bit(32) AS mask
        FROM (
            SELECT car, array_agg(color) arr, array_agg(_sentence) arr_sentence
            FROM (
                SELECT car, color, agg_or(_sentence) AS _sentence
                FROM drives
                GROUP BY car,color
            ) AS car_color
            GROUP BY car
        ) AS car_colors
    ) AS car_colors_mask
) AS car_prob_aggr
GROUP BY car, count

-- How many suspicions are there?
SELECT count, round(prob(dict,_sentence)::numeric,4) as prob, _sentence
FROM (
    SELECT count, agg_or(_sentence) AS _sentence
    FROM (
        SELECT prob_Bdd_count(arr,mask) AS count, prob_Bdd(arr_sentence,mask) AS _sentence, arr, arr_sentence, mask
        FROM (
            SELECT arr, arr_sentence, generate_series(0,(pow(2,array_length(arr_sentence,1))-1)::int)::bit(32) AS mask
            FROM (
                SELECT array_agg(person) arr, array_agg(_sentence) arr_sentence
                FROM (
                    SELECT witness, person, s.car, s.color, d._sentence & s._sentence AS _sentence
                    FROM drives d, saw s
                    WHERE d.car=s.car and d.color=s.color
                ) AS suspicions
                GROUP BY TRUE
            ) AS suspicions_agg
        ) AS suspicions_agg_mask
    ) AS suspicions_prob_agg
    GROUP BY count
) AS answer, _dict
ORDER BY prob DESC


-- See how far we can go
DROP TABLE IF EXISTS T;

CREATE TABLE T (
    a     TEXT,
    b     INTEGER,
    s     Bdd
);

INSERT INTO T VALUES ('A', 1);
INSERT INTO T VALUES ('A', 2);
INSERT INTO T VALUES ('A', 3);
INSERT INTO T VALUES ('A', 4);
INSERT INTO T VALUES ('A', 5);
INSERT INTO T VALUES ('A', 6);
INSERT INTO T VALUES ('A', 7);
INSERT INTO T VALUES ('A', 8);
INSERT INTO T VALUES ('A', 9);
INSERT INTO T VALUES ('A', 10);
INSERT INTO T VALUES ('A', 11);
INSERT INTO T VALUES ('A', 12);
INSERT INTO T VALUES ('A', 13);
INSERT INTO T VALUES ('A', 14);
INSERT INTO T VALUES ('A', 15);
INSERT INTO T VALUES ('A', 16);
INSERT INTO T VALUES ('A', 17);
INSERT INTO T VALUES ('A', 18);
INSERT INTO T VALUES ('A', 19);
INSERT INTO T VALUES ('A', 20);

UPDATE T
SET s=Bdd('x' || b || '=1');


-- How many rows are there?
SELECT count, round(prob(dict,_sentence)::numeric,6) as prob, _sentence
FROM (
    SELECT count, agg_or(_sentence) AS _sentence
    FROM (
        SELECT prob_Bdd_count(arr,mask) AS count, prob_Bdd(arr_sentence,mask) AS _sentence, arr, arr_sentence, mask
        FROM (
            SELECT arr, arr_sentence, generate_series(0,(pow(2,array_length(arr_sentence,1))-1)::int)::bit(32) AS mask
            FROM (
                SELECT array_agg(b) arr, array_agg(s) arr_sentence
                FROM T
                GROUP BY TRUE
            ) AS s_agg
        ) AS s_agg_mask
    ) AS s_prob_agg
    GROUP BY count
) AS answer,
(
    SELECT dictionary(string_agg(s,';')) AS dict
    FROM (SELECT 'x' || b || '=1:0.5; x' || b || '=2:0.5' AS s FROM T) AS vars
) AS _dict
ORDER BY prob DESC
