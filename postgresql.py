import os, sys, psycopg2

class Postgresql(object):

    config_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 
        'config.json'
    )

    def __init__(self):
        super(Postgresql, self).__init__()
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        conn = psycopg2.connect(
            u"dbname='{0}' user='{1}' host='{2}' port='{3}' password='{4}'".format(
                config['DB_NAME'],
                config['DB_USER'],
                config['DB_IP'],
                config['DB_PORT'],
                config['DB_PASSWORD']
            )
        )
        conn.set_session(autocommit=True)
        self.cursor = conn.cursor()

    def save_erro(self, mac, user, current_timestamp, erro_type, description, qgis_version, operational_system, plugins_versions):
        self.cursor.execute(
            '''
                INSERT INTO "erros"."erros_qgis" 
                (mac, usuario, data_hora, tipo, descricao, versao_qgis, sistema_operacional, versao_plugins, corrigido) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, FALSE)
            ''', 
            (
                str(mac), str(user), current_timestamp, 
                str(erro_type), str(description), str(qgis_version), 
                str(operational_system), str(plugins_versions)
            )
        )

    def getErrorsByDate(self, startDate, endDate):
        self.cursor.execute(
            '''
                SELECT * FROM "erros"."erros_qgis" 
                WHERE 
                    date(data_hora) >= date(to_timestamp(%s)) AND date(data_hora) <= date(to_timestamp(%s))
                ORDER BY data_hora DESC;
            ''',
            (startDate, endDate)
        )
        return self.cursor.fetchall()

    def setFixedError(self, errorId, fixed):
        self.cursor.execute(
            '''
                UPDATE "erros"."erros_qgis" 
                SET corrigido = %s
                WHERE id = %s;
            ''',
            (fixed, errorId)
        )
