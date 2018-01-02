CREATE TABLE posts.posts(
       id SERIAL PRIMARY KEY,
       user_id UUID REFERENCES auth.users(id) ON UPDATE CASCADE ON DELETE SET NULL,
       title VARCHAR(256) NOT NULL,
       description TEXT DEFAULT NULL,
       content TEXT DEFAULT NULL,
       url VARCHAR(2048) DEFAULT NULL,
       thumbnail_id INTEGER DEFAULT NULL REFERENCES media.images(id) ON UPDATE CASCADE ON DELETE SET NULL,
       ctime TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
       mtime TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
);

CREATE INDEX IF NOT EXISTS post_url_idx ON posts.posts(url);


CREATE TABLE posts.tags(
       id SERIAL PRIMARY KEY,
       tag_id INTEGER DEFAULT NULL REFERENCES common.tags(id) ON UPDATE CASCADE ON DELETE CASCADE,
       post_id INTEGER DEFAULT NULL REFERENCES posts.posts(id) ON UPDATE CASCADE ON DELETE CASCADE,
       assigned_on TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
);

CREATE UNIQUE INDEX IF NOT EXISTS post_tag_uidx ON posts.tags(tag_id, post_id);


CREATE TABLE posts.comments(
       user_id UUID REFERENCES auth.users(id) ON UPDATE CASCADE ON DELETE SET NULL,
       post_id INTEGER REFERENCES posts.posts(id) ON UPDATE CASCADE ON DELETE SET NULL
) INHERITS(common.comments);


CREATE INDEX IF NOT EXISTS post_comment_post_id_idx ON posts.comments(post_id);
CREATE INDEX IF NOT EXISTS post_comment_user_id_idx ON posts.comments(user_id);

-- I just learnt about this. The parent table has not null, and here we alter
-- only the interiting table. The parent doesn't change.
ALTER TABLE posts.comments ALTER COLUMN content DROP NOT NULL ;
ALTER TABLE posts.comments ALTER COLUMN content SET DEFAULT NULL;
