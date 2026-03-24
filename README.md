# 0Bug_Report

Plug-in para QGIS que registra erros python.

## Funcionalidades

* Registra em um banco Postgres todos os erros python retornados pelo QGIS
* Dentre as informações coletadas estão: mac adress, usuario, data, hora, tipo do erro, descrição, versão do QGIS, sistema operacional, versão dos plugins instalados.
* Permite abrir um registro centralizado dos erros, possibilitando uma busca por data e hora.
* Permite marcar se o erro foi ou não corrigido.

## Configuração do Banco de Dados

### 1. Criar o banco de dados PostgreSQL

Execute o script `new_db.sql` no seu banco PostgreSQL para criar a estrutura necessária:

```bash
psql -U seu_usuario -d nome_do_banco -f new_db.sql
```

Ou execute manualmente no pgAdmin/psql:
```sql
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
```

### 2. Configurar a conexão

Edite o arquivo `config.json` com as credenciais do seu banco PostgreSQL:

```json
{
    "DB_NAME": "nome_do_seu_banco",
    "DB_USER": "seu_usuario_postgres",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_PASSWORD": "sua_senha"
}
```

**Parâmetros:**
- `DB_NAME`: Nome do banco de dados PostgreSQL
- `DB_USER`: Usuário do PostgreSQL com permissões de INSERT/UPDATE/SELECT
- `DB_HOST`: Endereço do servidor PostgreSQL (localhost para servidor local)
- `DB_PORT`: Porta do PostgreSQL (padrão: 5432)
- `DB_PASSWORD`: Senha do usuário do PostgreSQL

### 3. Testar a conexão

Após configurar, reinicie o QGIS e o plugin estará pronto para registrar erros automaticamente no banco de dados.