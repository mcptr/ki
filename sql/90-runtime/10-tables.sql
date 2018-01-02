CREATE TABLE runtime.actions(
       id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
       name VARCHAR(256) DEFAULT NULL,
       status BOOLEAN DEFAULT FALSE,
       input_data JSONB DEFAULT NULL,
       result JSONB DEFAULT NULL,
       session_id VARCHAR(64) DEFAULT NULL,
       debug_data JSONB DEFAULT NULL,
       ctime TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
       mtime TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
);

CREATE INDEX IF NOT EXISTS action_result_idx ON runtime.actions(name);


CREATE TABLE runtime.emails(
       id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
       user_id UUID NOT NULL REFERENCES auth.users(id) ON UPDATE CASCADE ON DELETE CASCADE,
       text_content TEXT NOT NULL,
       html_content TEXT DEFAULT NULL,
       retries SMALLINT NOT NULL DEFAULT 0,
       max_age_sec INTEGER NOT NULL DEFAULT 0,
       status runtime.operation_status_t NOT NULL DEFAULT 'NEW',
       ctime TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
       mtime TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC')
);

CREATE INDEX IF NOT EXISTS email_recipient_idx ON runtime.emails(user_id);
CREATE INDEX IF NOT EXISTS email_status_idx ON runtime.emails(status);
CREATE INDEX IF NOT EXISTS email_retries_idx ON runtime.emails(retries);
CREATE INDEX IF NOT EXISTS email_max_age_sec_idx ON runtime.emails(max_age_sec);
