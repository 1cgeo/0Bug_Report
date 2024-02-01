CREATE SCHEMA IF NOT EXISTS erros;

CREATE TABLE IF NOT EXISTS erros.erros_qgis (
    id SERIAL PRIMARY KEY,
    mac VARCHAR(255),
    usuario VARCHAR(255),
    data_hora TIMESTAMP,
    tipo VARCHAR(255),
    descricao TEXT,
    versao_qgis VARCHAR(20),
    sistema_operacional VARCHAR(255),
    versao_plugins VARCHAR(255),
    corrigido BOOLEAN DEFAULT FALSE
);