CREATE OR REPLACE FUNCTION common.create_tags(tags_ VARCHAR[])
RETURNS INTEGER[]
AS $$
DECLARE
	_i INTEGER;
	_id INTEGER;
	_ids INTEGER[];
BEGIN
	tags_ = ARRAY(SELECT DISTINCT(unnest(tags_)));
	FOR _i IN 1 .. array_upper(tags_, 1) LOOP
		INSERT INTO common.tags AS ct(tag)
	    	    VALUES(tags_[_i])
		ON CONFLICT(tag) DO UPDATE SET mtime = NOW()
		RETURNING ct.id INTO _id;

		_ids = array_append(_ids, _id);
	END LOOP;

	RETURN _ids;
END;
$$
LANGUAGE plpgsql STRICT;
