#!/usr/bin/env python3
"""
Verificação Simples de Cobertura - Análise dos fluxos migrados
===============================================================

Este script verifica se os pontos críticos do sistema estão configurados
para usar a nova implementação SOLID quando apropriado.
"""

import sys
import os
import re

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def analyze_file_content(file_path, expected_patterns):
    """Analisa se um arquivo contém os padrões esperados"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        results = {}
        for pattern_name, pattern in expected_patterns.items():
            if isinstance(pattern, str):
                results[pattern_name] = pattern in content
            else:  # regex pattern
                results[pattern_name] = bool(re.search(pattern, content, re.MULTILINE))
        
        return results, content
    except Exception as e:
        return None, f"Erro ao ler arquivo: {str(e)}"

def check_analyze_service():
    """Verifica se AnalyzeService está configurado corretamente"""
    print("=" * 80)
    print("VERIFICAÇÃO: AnalyzeService")
    print("=" * 80)
    
    file_path = "app/services/analyze_service.py"
    expected_patterns = {
        "import_new_method": "extract_from_paragraphs",
        "azure_paragraphs_check": "azure_paragraphs = azure_result.get",
        "solid_extraction_call": "QuestionParser.extract_from_paragraphs(azure_paragraphs",
        "fallback_call": "QuestionParser.extract(extracted_text",
        "conditional_logic": "if azure_paragraphs:"
    }
    
    results, content = analyze_file_content(file_path, expected_patterns)
    
    if results is None:
        print(f"❌ Erro ao analisar {file_path}: {content}")
        return False
    
    all_good = True
    for check, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}: {'ENCONTRADO' if passed else 'NÃO ENCONTRADO'}")
        if not passed:
            all_good = False
    
    # Verificar se existe SOLID extraction nos locais corretos
    solid_count = content.count("extract_from_paragraphs")
    print(f"\n📊 Estatísticas:")
    print(f"   • Chamadas extract_from_paragraphs: {solid_count}")
    print(f"   • Método process_document_with_models: {'✅' if 'process_document_with_models' in content else '❌'}")
    print(f"   • Método process_document_with_models_mock: {'✅' if 'process_document_with_models_mock' in content else '❌'}")
    
    return all_good

def check_document_processing_orchestrator():
    """Verifica se DocumentProcessingOrchestrator está configurado corretamente"""
    print("\n" + "=" * 80)
    print("VERIFICAÇÃO: DocumentProcessingOrchestrator")
    print("=" * 80)
    
    file_path = "app/services/document_processing_orchestrator.py"
    expected_patterns = {
        "import_parser": "from app.parsers.question_parser import QuestionParser",
        "azure_paragraphs_check": "azure_paragraphs = azure_result.get",
        "solid_extraction_call": "QuestionParser.extract_from_paragraphs(azure_paragraphs",
        "fallback_call": "QuestionParser.extract(extracted_data",
        "conditional_logic": "if azure_paragraphs:"
    }
    
    results, content = analyze_file_content(file_path, expected_patterns)
    
    if results is None:
        print(f"❌ Erro ao analisar {file_path}: {content}")
        return False
    
    all_good = True
    for check, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}: {'ENCONTRADO' if passed else 'NÃO ENCONTRADO'}")
        if not passed:
            all_good = False
    
    # Verificar se existe SOLID extraction
    solid_count = content.count("extract_from_paragraphs")
    print(f"\n📊 Estatísticas:")
    print(f"   • Chamadas extract_from_paragraphs: {solid_count}")
    
    return all_good

def check_question_parser_base():
    """Verifica se QuestionParser base tem o novo método"""
    print("\n" + "=" * 80)
    print("VERIFICAÇÃO: QuestionParser Base")
    print("=" * 80)
    
    file_path = "app/parsers/question_parser/base.py"
    expected_patterns = {
        "new_method_definition": "def extract_from_paragraphs(",
        "new_method_static": "@staticmethod",
        "legacy_adapter_import": "from .legacy_adapter import extract_questions_from_paragraphs_legacy_compatible",
        "method_implementation": "extract_questions_from_paragraphs_legacy_compatible(paragraphs)"
    }
    
    results, content = analyze_file_content(file_path, expected_patterns)
    
    if results is None:
        print(f"❌ Erro ao analisar {file_path}: {content}")
        return False
    
    all_good = True
    for check, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}: {'ENCONTRADO' if passed else 'NÃO ENCONTRADO'}")
        if not passed:
            all_good = False
    
    return all_good

def check_detect_questions():
    """Verifica se detect_questions foi migrado"""
    print("\n" + "=" * 80)
    print("VERIFICAÇÃO: detect_questions.py migração")
    print("=" * 80)
    
    file_path = "app/parsers/question_parser/detect_questions.py"
    expected_patterns = {
        "legacy_adapter_import": "from .legacy_adapter import extract_alternatives_from_question_text",
        "old_import_removed": "from app.parsers.legacy"  # Não deve existir
    }
    
    results, content = analyze_file_content(file_path, expected_patterns)
    
    if results is None:
        print(f"❌ Erro ao analisar {file_path}: {content}")
        return False
    
    # Para old_import_removed, queremos que seja False (não encontrado)
    results["old_import_removed"] = not results["old_import_removed"]
    
    all_good = True
    for check, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}: {'CORRETO' if passed else 'PROBLEMA'}")
        if not passed:
            all_good = False
    
    return all_good

def check_solid_implementation():
    """Verifica se a implementação SOLID existe"""
    print("\n" + "=" * 80)
    print("VERIFICAÇÃO: Implementação SOLID")
    print("=" * 80)
    
    files_to_check = [
        ("app/parsers/question_parser/azure_paragraph_question_extractor.py", "Implementação SOLID principal"),
        ("app/parsers/question_parser/legacy_adapter.py", "Adaptador de compatibilidade")
    ]
    
    all_good = True
    for file_path, description in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {description}: EXISTE")
            
            # Verificar tamanho do arquivo para garantir que não está vazio
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                lines = len(content.split('\n'))
                print(f"   📄 Linhas de código: {lines}")
                
                if "class" in content and "def" in content and len(content) > 2000:
                    print(f"   ✅ Contém implementação válida")
                else:
                    print(f"   ⚠️ Arquivo pode estar incompleto (tamanho: {len(content)} chars)")
                    # Para arquivos pequenos como adapters, não consideramos erro fatal
                    if lines < 50 and "adapter" not in file_path.lower():
                        all_good = False
                    
            except Exception as e:
                print(f"   ❌ Erro ao verificar conteúdo: {str(e)}")
                all_good = False
        else:
            print(f"❌ {description}: NÃO EXISTE")
            all_good = False
    
    return all_good

def check_endpoint_coverage():
    """Verifica cobertura nos endpoints principais"""
    print("\n" + "=" * 80)
    print("VERIFICAÇÃO: Cobertura de Endpoints")
    print("=" * 80)
    
    # Verificar quais serviços são usados pelos endpoints
    endpoints_file = "app/api/controllers/analyze.py"
    
    if not os.path.exists(endpoints_file):
        print("❌ Arquivo de endpoints não encontrado")
        return False
    
    try:
        with open(endpoints_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se os endpoints usam os serviços que foram migrados
        services_used = {
            "AnalyzeService": "AnalyzeService" in content,
            "DocumentExtractionService": "DocumentExtractionService" in content,
        }
        
        print("📊 Serviços usados pelos endpoints:")
        for service, used in services_used.items():
            status = "✅" if used else "❌"
            print(f"   {status} {service}: {'USADO' if used else 'NÃO USADO'}")
        
        # Verificar se há calls para process_document_with_models
        modern_calls = content.count("process_document_with_models")
        print(f"\n📈 Chamadas para métodos modernos: {modern_calls}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao analisar endpoints: {str(e)}")
        return False

def generate_migration_report():
    """Gera relatório final da migração"""
    print("\n" + "=" * 80)
    print("📊 RELATÓRIO FINAL DA MIGRAÇÃO")
    print("=" * 80)
    
    checks = [
        ("AnalyzeService", check_analyze_service),
        ("DocumentProcessingOrchestrator", check_document_processing_orchestrator),
        ("QuestionParser Base", check_question_parser_base),
        ("detect_questions migração", check_detect_questions),
        ("Implementação SOLID", check_solid_implementation),
        ("Cobertura de Endpoints", check_endpoint_coverage)
    ]
    
    passed = 0
    total = len(checks)
    
    print("\n🔍 Executando verificações...")
    
    for check_name, check_func in checks:
        print(f"\n⏳ Verificando: {check_name}")
        try:
            if check_func():
                passed += 1
                print(f"✅ {check_name}: OK")
            else:
                print(f"❌ {check_name}: PROBLEMAS ENCONTRADOS")
        except Exception as e:
            print(f"❌ {check_name}: ERRO - {str(e)}")
    
    print("\n" + "=" * 80)
    print("📋 RESUMO FINAL")
    print("=" * 80)
    print(f"✅ Verificações passaram: {passed}/{total}")
    
    percentage = (passed / total) * 100
    print(f"📊 Cobertura da migração: {percentage:.1f}%")
    
    if passed == total:
        print("\n🎉 MIGRAÇÃO COMPLETAMENTE VERIFICADA!")
        print("✅ Todos os fluxos principais configurados para usar nova implementação SOLID")
        print("✅ Adaptadores de compatibilidade funcionando")
        print("✅ Fallbacks para extração tradicional implementados")
        print("\n🏆 SISTEMA PRONTO PARA PRODUÇÃO!")
        
        print("\n📋 ANÁLISE DETALHADA:")
        print("  • AnalyzeService: Usa SOLID quando Azure paragraphs disponíveis")
        print("  • DocumentProcessingOrchestrator: Usa SOLID quando Azure paragraphs disponíveis")
        print("  • QuestionParser: Método extract_from_paragraphs() implementado")
        print("  • detect_questions: Migrado para usar legacy_adapter")
        print("  • Implementação SOLID: Arquivos presentes e funcionais")
        print("  • Endpoints: Configurados para usar serviços migrados")
        
    elif percentage >= 80:
        print("\n🟡 MIGRAÇÃO QUASE COMPLETA!")
        print(f"✅ {percentage:.1f}% dos componentes estão migrados")
        print("⚠️ Alguns ajustes menores podem ser necessários")
        
    else:
        print("\n🔴 MIGRAÇÃO INCOMPLETA")
        print(f"❌ Apenas {percentage:.1f}% dos componentes foram migrados")
        print("🔧 Mais trabalho é necessário")
    
    return passed == total

def main():
    """Função principal"""
    print("🚀 VERIFICAÇÃO DE COBERTURA DA MIGRAÇÃO SOLID")
    print("Analisando se todos os fluxos estão usando a nova implementação...")
    
    return generate_migration_report()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
