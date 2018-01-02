CREATE OR REPLACE FUNCTION auth.trg_adapt_user() RETURNS TRIGGER
AS $$
BEGIN
    IF LENGTH(COALESCE(NEW.password, '')) < 6 THEN
       RAISE EXCEPTION 'Password too short';
       RETURN NULL;
    END IF;

    IF substr(NEW.password, 1, 4) <> '$2a$' THEN
	NEW.password := crypt(NEW.password, gen_salt('bf'));
    END IF;

    NEW.name := LOWER(NEW.name);
    NEW.email := LOWER(NEW.email);

    RETURN NEW;
END;
$$
LANGUAGE 'plpgsql';


CREATE OR REPLACE FUNCTION auth.authenticate_user(name_ VARCHAR, password_ VARCHAR)
RETURNS RECORD
AS $$
DECLARE
	R RECORD;
BEGIN
	SELECT u.id, u.name,
	       EXTRACT('EPOCH' FROM u.ctime)::INTEGER,
	       EXTRACT('EPOCH' FROM u.mtime)::INTEGER
	       FROM auth.users u
	       INTO R
	       WHERE u.name = name_ AND crypt(password_, password) = password;
	IF FOUND THEN
	   RETURN R;
	END IF;
	RETURN NULL;
END;
$$
LANGUAGE 'plpgsql' STRICT IMMUTABLE;


CREATE OR REPLACE FUNCTION auth.get_user_info(name_ VARCHAR)
RETURNS RECORD
AS $$
DECLARE
	R RECORD;
BEGIN
	SELECT
		u.name,
		u.is_admin,
		u.is_moderator,
		u.is_active,
		u.is_closed,
		COALESCE(EXTRACT('EPOCH' FROM u.email_verified_on), 0)::INTEGER,
		EXTRACT('EPOCH' FROM u.ctime)::INTEGER,
		EXTRACT('EPOCH' FROM u.mtime)::INTEGER,
	        (SELECT COUNT(p.id) FROM posts.posts p WHERE p.user_id = u.id),
		(SELECT COUNT(pc.id) FROM posts.comments pc WHERE pc.user_id = u.id)
		FROM auth.users u
		INTO R
		WHERE u.name = name_;
	IF FOUND THEN
	   RETURN R;
	END IF;
	RETURN NULL;
END;
$$
LANGUAGE 'plpgsql' STRICT;
