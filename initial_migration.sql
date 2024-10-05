BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> c5952166191c

CREATE TABLE games (
    id SERIAL NOT NULL, 
    status VARCHAR, 
    player1_token VARCHAR, 
    player2_token VARCHAR, 
    game_state JSON, 
    PRIMARY KEY (id)
);

CREATE INDEX ix_games_id ON games (id);

CREATE TYPE lobby_status AS ENUM ('Waiting', 'Full');

CREATE TABLE lobby_tables (
    id SERIAL NOT NULL, 
    name VARCHAR, 
    status lobby_status, 
    player1_token VARCHAR, 
    player2_token VARCHAR, 
    PRIMARY KEY (id)
);

CREATE INDEX ix_lobby_tables_id ON lobby_tables (id);

CREATE INDEX ix_lobby_tables_name ON lobby_tables (name);

INSERT INTO alembic_version (version_num) VALUES ('c5952166191c') RETURNING alembic_version.version_num;

COMMIT;

