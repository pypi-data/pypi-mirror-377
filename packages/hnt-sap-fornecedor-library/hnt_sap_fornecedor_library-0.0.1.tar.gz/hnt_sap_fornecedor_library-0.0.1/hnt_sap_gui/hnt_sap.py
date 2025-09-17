import logging
import locale
from SapGuiLibrary import SapGuiLibrary
from dotenv import load_dotenv
from .fornecedor.XK03_transaction import XK03Transaction
from .common.session import sessionable

logger = logging.getLogger(__name__)
class SapGui(SapGuiLibrary):
    def __init__(self) -> None:
        locale.setlocale(locale.LC_ALL, ('pt_BR.UTF-8'))
        load_dotenv()

    def format_float(self, value):
        return locale.format_string("%.2f", value)

    @sessionable
    def hnt_get_fornecedor(self, fornecedores):
        logger.info(f"enter execute hnt_get_fornecedor cod_fornecedores size:{len(fornecedores)}")
        result = []
        for i, fornecedor in enumerate(fornecedores):
            cod_fornecedor = str(fornecedor.get('cod_fornecedor', "")).strip()
            departamento = str(fornecedor.get('departamento', "")).upper().strip()
            if self.validar(cod_fornecedor, departamento) == False:
                result.append({
                    "cod_fornecedor": cod_fornecedor,
                    "departamento": departamento,
                    "error": "Código inválido ou Departamento não está no domínio permitido"
                })
                continue
            logger.info(f"{len(fornecedores)}/{i+1} - process cod_fornecedor:{cod_fornecedor}, departamento:{departamento}")
            try:
                dados = XK03Transaction().execute(self, cod_fornecedor)
                if 'error' in dados:
                    result.append({
                        "cod_fornecedor": cod_fornecedor,
                        "departamento": departamento,
                        "error": dados.get('error', '')
                    })
                    continue
                abrangencia = sorted(['RJ','MG','SP','ES'])
                result.append({
                    "cod_fornecedor": cod_fornecedor,
                    "departamento": departamento,
                    "dados": dados,
                    "abrangencia": abrangencia
                })
            except Exception as ex:
                logger.error(f"error in SAP {ex}")
                result.append({
                    "cod_fornecedor": cod_fornecedor,
                    "departamento": departamento,
                    "error": str(ex)
                })
        return result

    def validar(self, cod, dep, dominio=['PRODUCAO', 'EMBALAGENS', 'FLV', 'MERCEARIA', 'NAO_ALIMENTAR', 'OUTROS', 'PERECIVEIS', 'PERECIVEIS_IN_NATURA']):
        # valida se cod tem valor (não nulo e não vazio)
        if not cod or str(cod).strip() == "":
            return False
        # valida se dep está no domínio
        if dep not in dominio:
            return False
        
        return True



    