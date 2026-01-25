CREATE TABLE IF NOT EXISTS sample_documents(
    id UUID PRIMARY KEY,
    sample_id UUID NOT NULL,
    json_data jsonb NOT NULL,
    secondary_json_dict jsonb NOT NULL,
    created_datetime timestamptz NOT NULL
);

ALTER TABLE sample_documents
    ADD CONSTRAINT fk_sample_id FOREIGN KEY (sample_id) REFERENCES sample_table(id);

CREATE UNIQUE INDEX unique_index_json_id ON sample_documents using btree ((cast(json_data->>'id' as text)));
