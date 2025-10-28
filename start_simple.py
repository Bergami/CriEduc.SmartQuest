"""
Script simples para executar o SmartQuest API
"""
import sys
import os
import argparse
from pathlib import Path

def load_env_file():
    """Carrega variáveis dos arquivos .env e .env-local manualmente"""
    project_root = Path(__file__).parent
    env_path = project_root / ".env"
    env_local_path = project_root / ".env-local"
    
    # Carregar primeiro o .env (configurações públicas)
    if env_path.exists():
        print(f"📄 Carregando {env_path}")
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
                    print(f"  ✅ {key.strip()}")
    
    # Carregar depois o .env-local (configurações sensíveis - sobrescreve o .env)
    if env_local_path.exists():
        print(f"📄 Carregando {env_local_path}")
        with open(env_local_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
                    print(f"  ✅ {key.strip()}")
    
    if not env_path.exists() and not env_local_path.exists():
        print(f"⚠️  Nenhum arquivo .env encontrado")
        return False
    
    return True

def main():
    """Função principal"""
    # Processar argumentos de linha de comando
    parser = argparse.ArgumentParser(description="SmartQuest API Server")
    parser.add_argument("--use-mock", action="store_true", help="Use mock services instead of Azure AI")
    args = parser.parse_args()
    
    print("🚀 SmartQuest API - Debug Simples")
    print("=" * 40)
    
    # Configurar Python path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    os.environ["PYTHONPATH"] = str(project_root)
    
    # Configurar modo mock se solicitado
    if args.use_mock:
        os.environ["USE_AZURE_AI"] = "false"
        print("🎭 Modo MOCK ativado - usando serviços simulados")
    else:
        # Carregar .env apenas se não estiver em modo mock
        load_env_file()
    
    # Mostrar configurações
    print(f"\n🔧 Configurações:")
    endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
    use_azure = os.getenv("USE_AZURE_AI", "true").lower() == "true"
    
    print(f"  📍 Endpoint: {endpoint[:50] + '...' if endpoint and len(endpoint) > 50 else endpoint or '❌ Não configurado'}")
    print(f"  🔑 Key: {'✅ Configurada' if key else '❌ Não configurada'}")
    print(f"  🤖 Azure AI: {'✅ Habilitado' if use_azure else '❌ Desabilitado (MOCK)'}")
    
    print(f"\n📁 Diretório: {project_root}")
    print("=" * 40)
    
    try:
        # Importar e executar a aplicação
        print("🔄 Importando aplicação...")
        
        # Tentar importar uvicorn
        try:
            import uvicorn
            print("✅ Uvicorn importado")
        except ImportError as e:
            print(f"❌ Erro ao importar uvicorn: {e}")
            print("💡 Execute: pip install uvicorn[standard]")
            return
            
        # Tentar importar a aplicação
        try:
            from app.main import app
            print("✅ Aplicação importada")
        except ImportError as e:
            print(f"❌ Erro ao importar app: {e}")
            print("💡 Verifique se todos os módulos estão instalados")
            return
        
        print("\n🌐 Iniciando servidor...")
        print("📍 URL: http://127.0.0.1:8000")
        print("📚 Docs: http://127.0.0.1:8000/docs")
        print("💚 Health: http://127.0.0.1:8000/health")
        print("\n🛑 CTRL+C para parar\n")
        
        # Executar servidor
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
