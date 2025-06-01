-- Aggregate helper functions for DuBio
-- These functions must be executed ahead of using the abstraction layer

-- Computes a BDD by combining an array of BDDs according to a bit mask
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


-- COUNT
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


-- SUM
CREATE or REPLACE FUNCTION prob_Bdd_sum(a_b anyarray, mask bit)
    RETURNS numeric
    LANGUAGE plpgsql
    AS
$$
DECLARE
    result     numeric = 0;
    mask_len   integer = array_length(a_b, 1);
    mask_start integer = length(mask) - mask_len - 1;
BEGIN
    FOR i IN 1 .. mask_len
    LOOP
        IF get_bit(mask,mask_start+i) = 1 THEN
            result := result + a_b[i]::numeric;
        END IF;
    END LOOP;
    RETURN round(result, 4);
END;
$$;


-- AVG
CREATE or REPLACE FUNCTION prob_Bdd_avg(a_b anyarray, mask bit)
    RETURNS numeric
    LANGUAGE plpgsql
    AS
$$
DECLARE
    cnt int := prob_Bdd_count(a_b, mask);
BEGIN
    RETURN CASE
        WHEN cnt > 0 THEN round(prob_Bdd_sum(a_b, mask) / cnt, 4)
        ELSE NULL
    END;
END;
$$;


-- MIN
CREATE or REPLACE FUNCTION prob_Bdd_min(a_b anyarray, mask bit)
    RETURNS numeric
    LANGUAGE plpgsql
    AS
$$
DECLARE
    result     numeric = NULL;
    mask_len   integer = array_length(a_b, 1);
    mask_start integer = length(mask) - mask_len - 1;
BEGIN
    FOR i IN 1 .. mask_len
    LOOP
        IF get_bit(mask,mask_start+i) = 1 THEN
            IF result IS NULL OR a_b[i] < result THEN
                result := a_b[i];
            END IF;
        END IF;
    END LOOP;
    RETURN result;
END;
$$;


-- MAX
CREATE or REPLACE FUNCTION prob_Bdd_max(a_b anyarray, mask bit)
    RETURNS numeric
    LANGUAGE plpgsql
    AS
$$
DECLARE
    result     numeric = NULL;
    mask_len   integer = array_length(a_b, 1);
    mask_start integer = length(mask) - mask_len - 1;
BEGIN
    FOR i IN 1 .. mask_len
    LOOP
        IF get_bit(mask,mask_start+i) = 1 THEN
            IF result IS NULL OR a_b[i] > result THEN
                result := a_b[i];
            END IF;
        END IF;
    END LOOP;
    RETURN result;
END;
$$;
