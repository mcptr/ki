CREATE OR REPLACE FUNCTION posts.get_by_id(id_ INTEGER)
RETURNS SETOF RECORD
AS $$
DECLARE
	R RECORD;
BEGIN
	RETURN QUERY
	SELECT
		p.id,
		p.title,
		p.description,
		p.content,
		p.url,
		p.thumbnail_id,
		EXTRACT('EPOCH' FROM p.ctime)::INTEGER,
		EXTRACT('EPOCH' FROM p.mtime)::INTEGER,
		u.name,
		u.id,
		array_remove(array_agg(t.tag), NULL),
		(SELECT
			COUNT(pc.id)::INTEGER
			FROM posts.comments pc
			WHERE pc.post_id = p.id
		) as total_comments,
		mi.thumbnail_path
	FROM posts.posts p
	LEFT JOIN auth.users u ON p.user_id = u.id
	LEFT JOIN posts.tags pt ON pt.post_id = p.id
	LEFT JOIN common.tags t ON t.id = pt.tag_id
	LEFT JOIN media.images mi ON mi.id = p.thumbnail_id
	WHERE p.id = id_
	GROUP BY p.id, u.name, u.id, mi.thumbnail_path;
END
$$
LANGUAGE plpgsql STRICT;


CREATE OR REPLACE FUNCTION posts.get_by_tag(tag_ VARCHAR)
RETURNS SETOF RECORD
AS $$
DECLARE
	R RECORD;
BEGIN
	RETURN QUERY
	SELECT
		p.id,
		p.title,
		p.description,
		p.content,
		p.url,
		p.thumbnail_id,
		EXTRACT('EPOCH' FROM p.ctime)::INTEGER,
		EXTRACT('EPOCH' FROM p.mtime)::INTEGER,
		u.name,
		u.id,
		array_remove(array_agg(t.tag), NULL) as tags,
		(SELECT
			COUNT(pc.id)::INTEGER
			FROM posts.comments pc
			WHERE pc.post_id = p.id
		) as total_comments,
		mi.thumbnail_path
	FROM posts.posts p
	LEFT JOIN auth.users u ON p.user_id = u.id
	LEFT JOIN posts.tags pt ON pt.post_id = p.id
	LEFT JOIN common.tags t ON t.id = pt.tag_id
	LEFT JOIN media.images mi ON mi.id = p.thumbnail_id
	GROUP BY p.id, u.name, u.id, mi.thumbnail_path
	HAVING array_agg(t.tag) @> ARRAY[tag_]::VARCHAR[]
	ORDER BY p.ctime DESC;
END
$$
LANGUAGE plpgsql STRICT;


CREATE OR REPLACE FUNCTION posts.get_by_user(username_ VARCHAR)
RETURNS SETOF RECORD
AS $$
DECLARE
	R RECORD;
BEGIN
	RETURN QUERY
	SELECT
		p.id,
		p.title,
		p.description,
		p.content,
		p.url,
		p.thumbnail_id,
		EXTRACT('EPOCH' FROM p.ctime)::INTEGER,
		EXTRACT('EPOCH' FROM p.mtime)::INTEGER,
		u.name,
		u.id,
		array_remove(array_agg(t.tag), NULL),
		(SELECT
			COUNT(pc.id)::INTEGER
			FROM posts.comments pc
			WHERE pc.post_id = p.id
		) as total_comments,
		mi.thumbnail_path
	FROM posts.posts p
	LEFT JOIN auth.users u ON p.user_id = u.id
	LEFT JOIN posts.tags pt ON pt.post_id = p.id
	LEFT JOIN common.tags t ON t.id = pt.tag_id
	LEFT JOIN media.images mi ON mi.id = p.thumbnail_id
 	WHERE u.name = username_
	GROUP BY p.id, u.name, u.id, mi.thumbnail_path
	ORDER BY p.ctime DESC;
END
$$
LANGUAGE plpgsql STRICT;


CREATE OR REPLACE FUNCTION posts.get_recent()
RETURNS SETOF RECORD
AS $$
DECLARE
	R RECORD;
BEGIN
	RETURN QUERY
	SELECT
		p.id,
		p.title,
		p.description,
		p.content,
		p.url,
		p.thumbnail_id,
		EXTRACT('EPOCH' FROM p.ctime)::INTEGER,
		EXTRACT('EPOCH' FROM p.mtime)::INTEGER,
		u.name,
		u.id,
		array_remove(array_agg(t.tag), NULL),
		(SELECT
			COUNT(pc.id)::INTEGER
			FROM posts.comments pc
			WHERE pc.post_id = p.id
		) as total_comments,
		mi.thumbnail_path
	FROM posts.posts p
	LEFT JOIN auth.users u ON p.user_id = u.id
	LEFT JOIN posts.tags pt ON pt.post_id = p.id
	LEFT JOIN common.tags t ON t.id = pt.tag_id
	LEFT JOIN media.images mi ON mi.id = p.thumbnail_id
	GROUP BY p.id, u.name, u.id, mi.thumbnail_path
	ORDER BY p.ctime DESC;
END
$$
LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION posts.create_post(
       title_ VARCHAR,
       user_id_ UUID DEFAULT NULL,
       description_ VARCHAR DEFAULT NULL,
       content_ TEXT DEFAULT NULL,
       url_ VARCHAR DEFAULT NULL
)
RETURNS INTEGER
AS $$
DECLARE
	_result_id INTEGER;
BEGIN
	INSERT INTO posts.posts(
	       title, user_id, description,
	       content, url
	) VALUES(
	       title_, user_id_, description_,
	       content_, url_
	) RETURNING id INTO _result_id;

	RETURN _result_id;
END
$$
LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION posts.add_tags(
       post_id_ INTEGER,
       tags_ VARCHAR[]
)
RETURNS INTEGER[]
AS $$
DECLARE
	_i INTEGER;
	_id INTEGER;
	_tag_ids INTEGER[];
BEGIN
	WITH stmt AS(
		INSERT INTO posts.tags(post_id, tag_id, assigned_on)
		SELECT post_id_ post_id, TAG_ID, NOW() FROM
		       UNNEST(common.create_tags(tags_)) TAG_ID
		ON CONFLICT(post_id, tag_id) DO NOTHING
		RETURNING id
	)
	SELECT array_agg(id) FROM stmt INTO _tag_ids;

	RETURN _tag_ids;
END
$$
LANGUAGE plpgsql STRICT;


CREATE OR REPLACE FUNCTION posts.remove_tags(
       post_id_ INTEGER,
       tags_ VARCHAR[]
)
RETURNS INTEGER[]
AS $$
DECLARE
	_i INTEGER;
	_ids INTEGER[];
BEGIN
	WITH stmt AS(
	     DELETE FROM posts.tags pt
		WHERE pt.post_id = post_id_
		AND tag_id IN (
		    SELECT ct.id FROM common.tags ct
			WHERE ct.tag = ANY(tags_)
		)
		RETURNING pt.id
	)
	SELECT array_agg(id) FROM stmt INTO _ids;

	RETURN _ids;
END
$$
LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION posts.get_comments_tree(_post_id integer)
RETURNS SETOF RECORD
AS $$
DECLARE
	R record;
BEGIN
	RETURN QUERY
	WITH RECURSIVE comments_tree(
	     id, username, parent_id, post_id, content,
	     deleted, user_id,
	     ctime, mtime,
	     depth, path
	) AS (
	  	SELECT c.id, u.name, c.parent_id, c.post_id, c.content,
		       c.deleted, u.id as user_id,
		       EXTRACT('EPOCH' FROM c.ctime)::integer,
		       EXTRACT('EPOCH' FROM c.mtime)::integer,
		       0, ARRAY[]::integer[] AS path
		       FROM posts.comments c
		       LEFT JOIN auth.users u ON u.id = c.user_id
		       WHERE c.parent_id IS NULL AND c.post_id = _post_id
		UNION
		SELECT c.id, u.name, c.parent_id, c.post_id, c.content,
		       c.deleted, u.id as user_id,
		       EXTRACT('EPOCH' FROM c.ctime)::integer,
		       EXTRACT('EPOCH' FROM c.mtime)::integer,
	       	       ct.depth + 1, ct.path || c.parent_id
		       FROM comments_tree ct
		       JOIN posts.comments c ON c.parent_id = ct.id
		       LEFT JOIN auth.users u ON u.id = c.user_id
		)
		SELECT * FROM comments_tree ORDER BY path, ctime asc NULLS FIRST;

END;
$$
LANGUAGE plpgsql STRICT;


-- EXAMPLE:
-- SELECT * FROM posts.get_comments_tree(1) AS (
-- 	id integer, username varchar, parent_id integer, post_id integer,
-- 	content text, deleted boolean, user_id uuid, ctime integer, mtime integer, depth integer, path integer[]
-- );


