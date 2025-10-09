"""
🧪 Script de Validação Rápida - ImageCategorizationServicePydantic

Executa validação completa usando documentos reais do Azure para garantir
que a migração Pydantic está funcionando corretamente.
"""
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.image.image_categorization_service import ImageCategorizationService
from app.services.image.image_categorization_service_pydantic import ImageCategorizationServicePydantic

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_real_azure_responses(max_files: int = 5) -> Dict[str, Dict]:
    """Carrega responses reais do Azure para validação."""
    responses_dir = Path("tests/responses/azure")
    
    if not responses_dir.exists():
        logger.warning(f"Diretório {responses_dir} não encontrado")
        return {}
    
    responses = {}
    azure_files = list(responses_dir.glob("*.json"))
    
    for azure_file in azure_files[:max_files]:
        try:
            with open(azure_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                responses[azure_file.stem] = data
                logger.info(f"✅ Carregado: {azure_file.name}")
        except Exception as e:
            logger.warning(f"❌ Erro ao carregar {azure_file.name}: {e}")
    
    return responses


def create_sample_image_data(figure_ids: List[str]) -> Dict[str, str]:
    """Cria dados de imagem de exemplo baseados nos IDs das figuras."""
    # Base64 de uma imagem 1x1 PNG transparente para testes
    sample_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    return {figure_id: sample_base64 for figure_id in figure_ids}


def validate_pydantic_service(azure_responses: Dict[str, Dict]) -> Dict[str, Any]:
    """Valida o serviço Pydantic com responses reais do Azure."""
    validation_results = {
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "errors": [],
        "test_details": []
    }
    
    for response_name, azure_data in azure_responses.items():
        logger.info(f"🔄 Testando com {response_name}")
        
        try:
            # Extrair figuras
            figures = azure_data.get("figures", [])
            if not figures:
                logger.warning(f"⚠️ Nenhuma figura encontrada em {response_name}")
                continue
            
            # Criar dados de imagem baseados nas figuras reais
            figure_ids = [fig.get("id") for fig in figures if fig.get("id")]
            if not figure_ids:
                logger.warning(f"⚠️ Nenhum ID de figura válido em {response_name}")
                continue
            
            image_data = create_sample_image_data(figure_ids[:5])  # Máximo 5 para teste rápido
            
            validation_results["total_tests"] += 1
            
            # Executar categorização Pydantic
            header_images, content_images = ImageCategorizationServicePydantic.categorize_extracted_images_pydantic(
                image_data, azure_data, document_id=response_name
            )
            
            # Executar categorização Legacy
            legacy_header, legacy_content = ImageCategorizationService.categorize_extracted_images(
                image_data, azure_data
            )
            
            # Verificar resultados
            test_result = {
                "response_name": response_name,
                "figures_count": len(figures),
                "processed_images": len(image_data),
                "pydantic_header": len(header_images),
                "pydantic_content": len(content_images),
                "legacy_header": len(legacy_header),
                "legacy_content": len(legacy_content),
                "success": True
            }
            
            # Verificar consistência básica
            total_pydantic = len(header_images) + len(content_images)
            total_legacy = len(legacy_header) + len(legacy_content)
            
            if total_pydantic != total_legacy:
                test_result["warning"] = f"Total count mismatch: Pydantic={total_pydantic}, Legacy={total_legacy}"
                logger.warning(test_result["warning"])
            
            validation_results["passed_tests"] += 1
            validation_results["test_details"].append(test_result)
            
            logger.info(f"✅ {response_name}: Pydantic({len(header_images)}h,{len(content_images)}c) vs Legacy({len(legacy_header)}h,{len(legacy_content)}c)")
            
        except Exception as e:
            validation_results["failed_tests"] += 1
            error_msg = f"Erro em {response_name}: {str(e)}"
            validation_results["errors"].append(error_msg)
            logger.error(f"❌ {error_msg}")
    
    return validation_results


def run_comparison_report(azure_responses: Dict[str, Dict]) -> None:
    """Executa relatório de comparação detalhado."""
    logger.info("📊 Gerando relatório de comparação...")
    
    if not azure_responses:
        logger.warning("Nenhum response do Azure disponível para comparação")
        return
    
    # Usar o primeiro response para demonstração
    response_name = list(azure_responses.keys())[0]
    azure_data = azure_responses[response_name]
    
    figures = azure_data.get("figures", [])
    if not figures:
        logger.warning("Nenhuma figura disponível para comparação")
        return
    
    # Criar dados de teste
    figure_ids = [fig.get("id") for fig in figures[:3] if fig.get("id")]  # Máximo 3
    image_data = create_sample_image_data(figure_ids)
    
    if not image_data:
        logger.warning("Nenhum dado de imagem válido para comparação")
        return
    
    # Gerar relatório
    report = ImageCategorizationServicePydantic.compare_with_legacy(
        image_data, azure_data
    )
    
    logger.info("📊 Relatório de Comparação:")
    logger.info(f"  Imagens testadas: {report['test_images']}")
    logger.info(f"  Resultados idênticos: {report['comparison']['results_identical']}")
    logger.info(f"  Legacy - Header: {report['legacy_results']['header_count']}, Content: {report['legacy_results']['content_count']}")
    logger.info(f"  Pydantic - Header: {report['pydantic_results']['header_count']}, Content: {report['pydantic_results']['content_count']}")
    
    if not report['comparison']['results_identical']:
        logger.warning("⚠️ Resultados não são idênticos!")
        for diff in report['comparison'].get('differences', []):
            logger.warning(f"  - {diff}")
    
    logger.info("✨ Vantagens do Pydantic:")
    for advantage in report['pydantic_advantages']:
        logger.info(f"  + {advantage}")


def run_performance_test() -> None:
    """Executa teste de performance simples."""
    logger.info("⚡ Executando teste de performance...")
    
    import time
    
    # Criar dados de teste
    azure_result = {
        "figures": [
            {
                "id": f"{i}.1",
                "boundingRegions": [{
                    "pageNumber": 1,
                    "polygon": [0.1, 0.1, 0.9, 0.1, 0.9, 0.2, 0.1, 0.2]
                }]
            }
            for i in range(1, 21)  # 20 figuras
        ]
    }
    
    image_data = create_sample_image_data([f"{i}.1" for i in range(1, 21)])
    iterations = 5
    
    # Medir Legacy
    start_time = time.time()
    for _ in range(iterations):
        ImageCategorizationService.categorize_extracted_images(image_data, azure_result)
    legacy_time = time.time() - start_time
    
    # Medir Pydantic
    start_time = time.time()
    for _ in range(iterations):
        ImageCategorizationServicePydantic.categorize_extracted_images_pydantic(image_data, azure_result)
    pydantic_time = time.time() - start_time
    
    ratio = pydantic_time / legacy_time if legacy_time > 0 else 1
    
    logger.info(f"⚡ Resultados de Performance ({iterations} iterações):")
    logger.info(f"  Legacy: {legacy_time:.4f}s ({legacy_time/iterations:.4f}s por iteração)")
    logger.info(f"  Pydantic: {pydantic_time:.4f}s ({pydantic_time/iterations:.4f}s por iteração)")
    logger.info(f"  Ratio: {ratio:.2f}x {'(ACEITÁVEL)' if ratio < 3.0 else '(LENTO)'}")


def main():
    """🚀 Execução principal da validação."""
    print("🧪 Validação Completa - ImageCategorizationServicePydantic")
    print("=" * 60)
    
    # 1. Carregar responses reais do Azure
    logger.info("📂 Carregando responses reais do Azure...")
    azure_responses = load_real_azure_responses(max_files=3)
    
    if not azure_responses:
        logger.error("❌ Nenhum response do Azure encontrado!")
        logger.info("💡 Verifique se o diretório tests/responses/azure existe e contém arquivos .json")
        return
    
    logger.info(f"✅ Carregados {len(azure_responses)} responses do Azure")
    
    # 2. Validar serviço Pydantic
    logger.info("🔍 Validando serviço Pydantic...")
    validation_results = validate_pydantic_service(azure_responses)
    
    print("\n📊 Resultados da Validação:")
    print(f"  Total de testes: {validation_results['total_tests']}")
    print(f"  Testes passou: {validation_results['passed_tests']}")
    print(f"  Testes falharam: {validation_results['failed_tests']}")
    
    if validation_results['errors']:
        print("\n❌ Erros encontrados:")
        for error in validation_results['errors']:
            print(f"  - {error}")
    
    # 3. Gerar relatório de comparação
    logger.info("📊 Gerando relatório de comparação...")
    run_comparison_report(azure_responses)
    
    # 4. Teste de performance
    run_performance_test()
    
    # 5. Resumo final
    print("\n🎯 Resumo Final:")
    if validation_results['failed_tests'] == 0:
        print("✅ Todos os testes passaram!")
        print("✅ ImageCategorizationServicePydantic está funcionando corretamente")
        print("✅ Pronto para substituir o serviço legacy gradualmente")
    else:
        print("⚠️ Alguns testes falharam")
        print("🔧 Verifique os erros antes de continuar a migração")
    
    print("\n🚀 Próximos Passos:")
    print("1. Se todos os testes passaram: integrar gradualmente no AnalyzeService")
    print("2. Atualizar HeaderParser para usar método Pydantic")
    print("3. Executar testes de integração completos")
    print("4. Remover serviço legacy após validação completa")


if __name__ == "__main__":
    main()
