CREATE TABLE sample_table (
    id UUID PRIMARY KEY,
    username TEXT NOT NULL,
    bool_field BOOLEAN,
    datetime_field timestamptz,
    int_field INTEGER,
    float_field float8,
    decimal_field numeric
);

CREATE UNIQUE INDEX unique_index_username ON sample_table (username);

ALTER TABLE sample_table ADD CONSTRAINT unique_index_username_constraint UNIQUE USING INDEX unique_index_username;

CREATE INDEX index_datetime_field ON sample_table (datetime_field);