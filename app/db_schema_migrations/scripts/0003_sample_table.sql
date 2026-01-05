CREATE TABLE sample_table (
    id UUID PRIMARY KEY,
    username TEXT NOT NULL,
    bool_field BOOLEAN,
    float_field float8,
    decimal_field numeric,
    version INTEGER NOT NULL,
    created_datetime timestamptz NOT NULL,
    updated_datetime timestamptz NOT NULL
);

CREATE UNIQUE INDEX unique_index_username ON sample_table (username);

ALTER TABLE sample_table ADD CONSTRAINT unique_index_username_constraint UNIQUE USING INDEX unique_index_username;

CREATE INDEX index_created_datetime ON sample_table (created_datetime);

CREATE INDEX index_updated_datetime ON sample_table (updated_datetime);