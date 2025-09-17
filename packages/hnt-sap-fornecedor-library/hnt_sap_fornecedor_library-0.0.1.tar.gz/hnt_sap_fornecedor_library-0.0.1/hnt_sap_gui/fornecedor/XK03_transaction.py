import logging
from hnt_sap_gui.hnt_sap_exception import HntSapException
import re

logger = logging.getLogger(__name__)
MSG_SAP_CODIGO_DOCUMENTO = "^Documento ([0-9]*) HFNT foi pré-editado$"
MSG_SAP_JA_FOI_CRIADO = "^Verificar se o documento já foi criado com o nº HFNT ([0-9]*) ([0-9]{4})$"
MSG_SAP_CONTA_BLOQUEADA = "^Conta ([0-9]+) HFNT bloqueada para contabilização$"
MSG_SAP_COND_PGTO_MODIFICADAS = "Condições de pagamento foram modificadas, verificar"

class XK03Transaction:
    def __init__(self) -> None:
        pass

    def execute(self, sapGuiLib, cod_fornecedor):
        logger.info(f"Enter execute cod_fornecedor:{cod_fornecedor}")
        sapGuiLib.run_transaction('/nXK03')
        sapGuiLib.session.findById("wnd[0]/usr/ctxtRF02K-LIFNR").Text = cod_fornecedor  #cod_fornecedor
        sapGuiLib.session.findById("wnd[0]/usr/ctxtRF02K-BUKRS").Text = "HFNT"  #Empresa
        sapGuiLib.session.findById("wnd[0]/usr/chkRF02K-D0110").Selected = True  #Endereço
        sapGuiLib.session.findById("wnd[0]/usr/chkRF02K-D0120").Selected = True  #Controle
        sapGuiLib.session.findById("wnd[0]/usr/chkRF02K-D0130").Selected = False  #Pagamentos
        sapGuiLib.session.findById("wnd[0]/usr/chkWRF02K-D0380").Selected = False  #Pessoa de contato
        sapGuiLib.session.findById("wnd[0]/usr/chkRF02K-D0210").Selected = False  #Administração conta
        sapGuiLib.session.findById("wnd[0]/usr/chkRF02K-D0215").Selected = True  #Pagamentos
        sapGuiLib.session.findById("wnd[0]/usr/chkRF02K-D0220").Selected = False  #Correspondência
        sapGuiLib.session.findById("wnd[0]/usr/chkRF02K-D0610").Selected = True  #Imposto ret.na fonte
        sapGuiLib.session.findById("wnd[0]/usr/chkRF02K-D0310").Selected = False  #Dados de compras
        sapGuiLib.session.findById("wnd[0]/usr/chkWRF02K-D0320").Selected = False  #Funções do parceiro
        sapGuiLib.send_vkey(0)
        sbar = sapGuiLib.session.findById("wnd[0]/sbar").Text
        pattern = r"^O fornecedor \d+ está marcado para eliminação$"
        if re.match(pattern, sbar):
            return {
                "error": sbar
            }
        #Tela Endereço
        razao_social_1 = sapGuiLib.session.findById("wnd[0]/usr/subADDRESS:SAPLSZA1:0300/subCOUNTRY_SCREEN:SAPLSZA1:0301/txtADDR1_DATA-NAME1").Text
        razao_social_2 = None
        razao_social = None
        if sapGuiLib.session.findById("wnd[0]/usr/subADDRESS:SAPLSZA1:0300/subCOUNTRY_SCREEN:SAPLSZA1:0301/txtADDR1_DATA-NAME2", False) is not None:
            razao_social_2 = sapGuiLib.session.findById("wnd[0]/usr/subADDRESS:SAPLSZA1:0300/subCOUNTRY_SCREEN:SAPLSZA1:0301/txtADDR1_DATA-NAME2").Text
        if str(razao_social_2).strip() != None and len(razao_social_2) > 0:
            razao_social = f"{razao_social_1} {razao_social_2}"
        else:
            razao_social = razao_social_1
        rua = sapGuiLib.session.findById("wnd[0]/usr/subADDRESS:SAPLSZA1:0300/subCOUNTRY_SCREEN:SAPLSZA1:0301/txtADDR1_DATA-STREET").Text
        numero = sapGuiLib.session.findById("wnd[0]/usr/subADDRESS:SAPLSZA1:0300/subCOUNTRY_SCREEN:SAPLSZA1:0301/txtADDR1_DATA-HOUSE_NUM1").Text
        bairro = None
        if sapGuiLib.session.findById("wnd[0]/usr/subADDRESS:SAPLSZA1:0300/subCOUNTRY_SCREEN:SAPLSZA1:0301/txtADDR1_DATA-CITY2", False) is not None:
            bairro = sapGuiLib.session.findById("wnd[0]/usr/subADDRESS:SAPLSZA1:0300/subCOUNTRY_SCREEN:SAPLSZA1:0301/txtADDR1_DATA-CITY2").Text
        cep = sapGuiLib.session.findById("wnd[0]/usr/subADDRESS:SAPLSZA1:0300/subCOUNTRY_SCREEN:SAPLSZA1:0301/txtADDR1_DATA-POST_CODE1").Text
        municipio = sapGuiLib.session.findById("wnd[0]/usr/subADDRESS:SAPLSZA1:0300/subCOUNTRY_SCREEN:SAPLSZA1:0301/txtADDR1_DATA-CITY1").Text
        uf = sapGuiLib.session.findById("wnd[0]/usr/subADDRESS:SAPLSZA1:0300/subCOUNTRY_SCREEN:SAPLSZA1:0301/ctxtADDR1_DATA-REGION").Text
        Email = sapGuiLib.session.findById("wnd[0]/usr/subADDRESS:SAPLSZA1:0300/subCOUNTRY_SCREEN:SAPLSZA1:0301/txtSZA1_D0100-SMTP_ADDR").Text
        #Botão Tela seguinte
        sapGuiLib.session.findById("wnd[0]/tbar[1]/btn[8]").press()
        #Tela Controle
        cnpj = sapGuiLib.session.findById("wnd[0]/usr/txtLFA1-STCD1").Text
        sapGuiLib.session.findById("wnd[0]/tbar[1]/btn[8]").press()
        cond_pgto = sapGuiLib.session.findById("wnd[0]/usr/ctxtLFB1-ZTERM").Text
        forma_pgto = sapGuiLib.session.findById("wnd[0]/usr/ctxtLFB1-ZWELS").Text
        sapGuiLib.session.findById("wnd[0]/tbar[1]/btn[8]").press()
        table = sapGuiLib.session.findById("wnd[0]/usr/subWT_WITS:SAPMFWTV:0610/tblSAPMFWTVTCTRL_QUELLENSTEUER")
        irf_contabilidade = []
        for row in range(table.RowCount):
            try:
                if table.GetCell(row, 2).Selected and len(table.GetCell(row, 1).Text) > 0:# Sujeito
                    ctg_irf = table.GetCell(row, 0).Text  # Ctg.IRF
                    codigo_irf = table.GetCell(row, 1).Text  # Código IRF
                    irf_contabilidade.append({"ctg_irf": ctg_irf, "codigo_irf": codigo_irf})
            except Exception as e:
                logger.info(f"Linha {row} está vazia, termina iteração no grid.")
                break

        return {
            "razao_social": razao_social,
            "rua": rua,
            "numero": numero,
            "bairro": bairro,
            "cep": cep,
            "municipio": municipio,
            "uf": uf,
            "cnpj": cnpj,
            "email": Email,
            "cond_pgto":cond_pgto,
            "forma_pgto": forma_pgto,
            "irf_contabilidade": irf_contabilidade
        }
