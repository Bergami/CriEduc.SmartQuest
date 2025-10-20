#!/usr/bin/env python3
"""
MongoDB Migration Runner - SmartQuest

Script para executar migrações do MongoDB de forma controlada.
Suporte para Docker e instalação local do MongoDB.
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env-local
env_local_path = Path(__file__).parent.parent / ".env-local"
load_dotenv(env_local_path)

# Configurações a partir do .env
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("MONGODB_DATABASE", "smartquest")
MIGRATIONS_DIR = Path(__file__).parent / "migrations"
DOCKER_CONTAINER = os.getenv("MONGODB_DOCKER_CONTAINER", "smartquest-mongodb")


def run_command(command, description):
    """Executa comando e retorna resultado."""
    print(f"[INFO] {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[SUCCESS] {description}")
            return True, result.stdout
        else:
            print(f"[ERROR] {description} - Erro: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"[ERROR] {description} - Excecao: {str(e)}")
        return False, str(e)


def check_mongodb_connection():
    """Verifica se MongoDB está acessível."""
    # Tentar via mongosh local primeiro
    success, output = run_command(
        f'mongosh "{MONGODB_URI}/{DATABASE_NAME}" --eval "db.runCommand({{ping: 1}})"',
        "Verificando conexao MongoDB local"
    )
    
    if success:
        return "local"
    
    # Tentar via Docker
    success, output = run_command(
        f"docker exec {DOCKER_CONTAINER} mongosh {DATABASE_NAME} --eval \"db.runCommand({{ping: 1}})\"",
        "Verificando conexao MongoDB via Docker"
    )
    
    if success:
        return "docker"
    
    return None


def get_applied_migrations(connection_type):
    """Lista migrações já aplicadas."""
    if connection_type == "local":
        cmd = f'mongosh "{MONGODB_URI}/{DATABASE_NAME}" --eval "JSON.stringify(db.migrations.find().toArray())" --quiet'
    else:
        cmd = f'docker exec {DOCKER_CONTAINER} mongosh {DATABASE_NAME} --eval "JSON.stringify(db.migrations.find().toArray())" --quiet'
    
    success, output = run_command(cmd, "Verificando migracoes aplicadas")
    
    if success:
        try:
            migrations = json.loads(output.strip())
            return [m["version"] for m in migrations]
        except:
            return []
    return []


def get_pending_migrations(applied_versions):
    """Lista migrações pendentes."""
    migration_files = sorted([
        f for f in os.listdir(MIGRATIONS_DIR)
        if f.endswith('.js') and not f.startswith('README')
    ])
    
    pending = []
    for file in migration_files:
        # Extrair versão do nome do arquivo
        version = file.split('_')[0] + "_" + file.split('_')[1]
        if version not in applied_versions:
            pending.append((version, file))
    
    return pending


def run_migration(migration_file, connection_type):
    """Executa uma migração específica."""
    migration_path = MIGRATIONS_DIR / migration_file
    
    if connection_type == "local":
        cmd = f'mongosh "{MONGODB_URI}/{DATABASE_NAME}" "{migration_path}"'
    else:
        # Para Docker no Windows, usar PowerShell com Get-Content
        if os.name == 'nt':  # Windows
            cmd = f'powershell -Command "Get-Content \'{migration_path}\' | docker exec -i {DOCKER_CONTAINER} mongosh {DATABASE_NAME}"'
        else:  # Linux/Mac
            cmd = f'cat "{migration_path}" | docker exec -i {DOCKER_CONTAINER} mongosh {DATABASE_NAME}'
    
    print(f"[INFO] Executando migracao: {migration_file}")
    success, output = run_command(cmd, f"Aplicando {migration_file}")
    
    if success:
        print(f"[SUCCESS] Migracao {migration_file} aplicada com sucesso")
        if output.strip():
            print(f"[OUTPUT] {output}")
        return True
    else:
        print(f"[ERROR] Falha ao aplicar migracao {migration_file}")
        return False


def main():
    print("MongoDB Migration Runner - SmartQuest")
    print("=" * 50)
    
    # Verificar conexão com MongoDB
    connection_type = check_mongodb_connection()
    if not connection_type:
        print("[ERROR] Nao foi possivel conectar ao MongoDB")
        print("[INFO] Certifique-se que o MongoDB esta rodando (local ou Docker)")
        sys.exit(1)
    
    print(f"[SUCCESS] Conectado ao MongoDB via: {connection_type}")
    
    # Listar migrações aplicadas
    applied_migrations = get_applied_migrations(connection_type)
    print(f"[INFO] Migracoes ja aplicadas: {len(applied_migrations)}")
    for migration in applied_migrations:
        print(f"  [APPLIED] {migration}")
    
    # Listar migrações pendentes
    pending_migrations = get_pending_migrations(applied_migrations)
    
    if not pending_migrations:
        print("[SUCCESS] Todas as migracoes estao atualizadas!")
        return
    
    print(f"[INFO] Migracoes pendentes: {len(pending_migrations)}")
    for version, file in pending_migrations:
        print(f"  [PENDING] {version} - {file}")
    
    # Perguntar se deve aplicar
    response = input("\n[QUESTION] Aplicar migracoes pendentes? (y/N): ").strip().lower()
    if response not in ['y', 'yes', 's', 'sim']:
        print("[INFO] Migracoes canceladas pelo usuario")
        return
    
    # Aplicar migrações
    print("\n[INFO] Aplicando migracoes...")
    for version, migration_file in pending_migrations:
        if not run_migration(migration_file, connection_type):
            print(f"[ERROR] Parando execucao devido a erro na migracao {migration_file}")
            break
    
    print("\n[SUCCESS] Processo de migracao concluido!")


if __name__ == "__main__":
    main()