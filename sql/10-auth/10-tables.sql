CREATE TABLE auth.users(
       id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
       name VARCHAR(32) NOT NULL UNIQUE,
       password VARCHAR(256) NOT NULL,
       email VARCHAR(512) DEFAULT NULL UNIQUE,
       is_closed BOOLEAN NOT NULL DEFAULT FALSE,
       is_active BOOLEAN NOT NULL DEFAULT TRUE,
       email_verified_on TIMESTAMP WITHOUT TIME ZONE DEFAULT NULL,
       is_admin BOOLEAN NOT NULL DEFAULT FALSE,
       is_moderator BOOLEAN NOT NULL DEFAULT FALSE,
       locale VARCHAR(16) DEFAULT NULL,
       ctime TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
       mtime TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
);


CREATE INDEX IF NOT EXISTS active_user_idx ON auth.users(is_active);


CREATE TABLE auth.recovery (
       id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
       user_id UUID NOT NULL REFERENCES auth.users(id) ON UPDATE CASCADE ON DELETE CASCADE,
       max_age_sec INTEGER NOT NULL DEFAULT 3600 * 4,
       ctime TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
       mtime TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
);


CREATE TABLE auth.verifications (
       id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
       user_id UUID NOT NULL REFERENCES auth.users(id) ON UPDATE CASCADE ON DELETE CASCADE,
       max_age_sec INTEGER NOT NULL DEFAULT 3600,
       topic VARCHAR(128) DEFAULT NULL,
       verification_data TEXT DEFAULT NULL,
       ctime TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
);


CREATE TABLE auth.sessions (
       id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
       user_id UUID DEFAULT NULL REFERENCES auth.users(id) ON UPDATE CASCADE ON DELETE CASCADE,
       user_agent VARCHAR(1024) DEFAULT NULL,
       max_age_sec INTEGER NOT NULL DEFAULT 0,
       storage JSONB DEFAULT NULL,
       ctime TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
       mtime TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
);
