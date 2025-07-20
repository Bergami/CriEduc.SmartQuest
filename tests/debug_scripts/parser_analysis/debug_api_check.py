from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
import inspect

# Cria um cliente com credenciais temporárias para verificar a API
client = DocumentIntelligenceClient(endpoint="https://example.com", credential=AzureKeyCredential("dummy"))

# Inspeciona os parâmetros da função begin_analyze_document
signature = inspect.signature(client.begin_analyze_document)
print("Parâmetros de begin_analyze_document:")
for name, param in signature.parameters.items():
    print(f"{name}: {param.default}")
