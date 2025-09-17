from hnt_sap_gui import SapGui
import json
def test_hnt_get_fornecedors():
    with open("./tests/expected_json/input_fornecedores_9.json", "r", encoding="utf-8") as arquivo_json: fornecedores = json.load(arquivo_json)
    fornecedoresSAP = SapGui().hnt_get_fornecedor(fornecedores)
    with open(f"./tests/expected_json/fornecedoresSAP_9.json", "r", encoding="utf-8") as arquivo_json: expected = json.load(arquivo_json)
    assert fornecedoresSAP == expected 
