# 0Bug_Report

Plug-in para QGIS que registra erros python.

* Registra em um banco Postgres todos os erros python retornados pelo QGIS
* Dentre as informações coletadas estão: mac adress, usuario, data, hora, tipo do erro, descrição, versão do QGIS, sistema operacional, versão dos plugins instalados.
* Permite abrir um registro centralizado dos erros, possibilitando uma busca por data e hora.
* Permite marcar se o erro foi ou não corrigido.