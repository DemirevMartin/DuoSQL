-- This is a count on drives table with a group by on car

SELECT car, count, agg_or(_sentence) AS _sentence -- Combine the sentences
FROM ( -- count the number of colors
    SELECT car, prob_Bdd_count(arr,mask) AS count, prob_Bdd(arr_sentence,mask) AS _sentence, arr, arr_sentence, mask
    FROM ( -- Create a mask for each car with all possible colors and sentences in all worlds
        SELECT car, arr, arr_sentence, generate_series(0,(pow(2,array_length(arr_sentence,1))-1)::int)::bit(32) AS mask
        FROM ( -- Combine all colors and sentences for each car
            SELECT car, array_agg(color) arr, array_agg(_sentence) arr_sentence
            FROM ( -- Select all single rows
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
