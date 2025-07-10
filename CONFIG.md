# 🔧 Configuração do Ambiente

## 📋 Arquivos de Configuração

### `.env` (Público - pode ser commitado)
Contém configurações não sensíveis:
- Configurações gerais da aplicação
- Modelos e versões de API
- Flags de funcionalidades

### `.env-local` (Privado - NÃO commitado)
Contém configurações sensíveis:
- Chaves de API
- Endpoints de serviços
- Credenciais de acesso

## 🚀 Setup Inicial

1. **Copie o template de configurações sensíveis:**
   ```bash
   cp .env-local.example .env-local
   ```

2. **Configure suas credenciais no `.env-local`:**
   ```properties
   AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://seu-endpoint.cognitiveservices.azure.com/
   AZURE_DOCUMENT_INTELLIGENCE_KEY=sua-chave-secreta-aqui
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute o projeto:**
   ```bash
   python start_simple.py
   ```

## ⚠️ Importante

- **NUNCA** commite o arquivo `.env-local`
- O arquivo `.env-local` tem prioridade sobre o `.env`
- Mantenha suas chaves sempre seguras
- Use o `.env-local.example` como referência

## 🔄 Ordem de Carregamento

1. Primeiro carrega `.env` (configurações públicas)
2. Depois carrega `.env-local` (sobrescreve com configurações sensíveis)
3. Por último, variáveis de ambiente do sistema
