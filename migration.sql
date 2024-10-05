BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 9cbd0eb7f234

INSERT INTO alembic_version (version_num) VALUES ('9cbd0eb7f234') RETURNING alembic_version.version_num;

-- Running upgrade 9cbd0eb7f234 -> ad9f71786956

UPDATE alembic_version SET version_num='ad9f71786956' WHERE alembic_version.version_num = '9cbd0eb7f234';

-- Running upgrade ad9f71786956 -> cf09db0a3441

CREATE TABLE lobby_tables (
    id SERIAL NOT NULL, 
    name VARCHAR, 
    status VARCHAR, 
    PRIMARY KEY (id)
);

CREATE INDEX ix_lobby_tables_id ON lobby_tables (id);

CREATE INDEX ix_lobby_tables_name ON lobby_tables (name);

CREATE INDEX ix_lobby_tables_status ON lobby_tables (status);

DROP INDEX ix_lobby_games_id;

DROP INDEX ix_lobby_games_name;

DROP INDEX ix_lobby_games_status;

DROP TABLE lobby_games;

ALTER TABLE players ADD COLUMN lobby_table_id INTEGER;

ALTER TABLE players ADD FOREIGN KEY(lobby_table_id) REFERENCES lobby_tables (id);

UPDATE alembic_version SET version_num='cf09db0a3441' WHERE alembic_version.version_num = 'ad9f71786956';

-- Running upgrade cf09db0a3441 -> 5228358e16f9

CREATE TYPE lobby_status AS ENUM ('Waiting', 'Full');

DROP INDEX ix_players_id;

DROP INDEX ix_players_name;

DROP TABLE players;

ALTER TABLE games ADD COLUMN player1_token VARCHAR;

ALTER TABLE games ADD COLUMN player2_token VARCHAR;

ALTER TABLE games ADD COLUMN game_state JSON;

DROP INDEX ix_games_name;

DROP INDEX ix_games_status;

ALTER TABLE games DROP COLUMN name;

ALTER TABLE lobby_tables ADD COLUMN player1_token VARCHAR;

ALTER TABLE lobby_tables ADD COLUMN player2_token VARCHAR;

ALTER TABLE lobby_tables ALTER COLUMN status TYPE lobby_status USING status::text::lobby_status;

DROP INDEX ix_lobby_tables_status;

UPDATE alembic_version SET version_num='5228358e16f9' WHERE alembic_version.version_num = 'cf09db0a3441';

COMMIT;