#!/usr/bin/env python3
"""
ANÁLISE DE QUALIDADE DAS IMAGENS EXTRAÍDAS
==========================================

Compara dimensões, tamanhos e qualidade das imagens extraídas pelos métodos:
- Azure Figures (HTTP API)
- Manual PDF (coordenadas)
"""

import os
import json
from PIL import Image
import hashlib
from pathlib import Path

def analyze_image_quality():
    """Analisa a qualidade das imagens extraídas pelos dois métodos"""
    
    base_path = Path("tests/images/by_provider")
    
    # Caminhos das imagens do teste mais recente
    azure_path = base_path / "comparison" / "test@example.com_test.pdf" / "azure_figures"
    manual_path = base_path / "comparison" / "test@example.com_test.pdf" / "manual_pdf"
    
    print("🔍 ANÁLISE DE QUALIDADE DAS IMAGENS EXTRAÍDAS")
    print("=" * 60)
    print(f"📁 Azure Figures: {azure_path}")
    print(f"📁 Manual PDF: {manual_path}")
    print()
    
    # Verificar se os diretórios existem
    if not azure_path.exists():
        print(f"❌ Diretório Azure não encontrado: {azure_path}")
        return
    
    if not manual_path.exists():
        print(f"❌ Diretório Manual não encontrado: {manual_path}")
        return
    
    # Listar arquivos de imagem
    azure_images = sorted([f for f in azure_path.iterdir() if f.suffix.lower() == '.jpg'])
    manual_images = sorted([f for f in manual_path.iterdir() if f.suffix.lower() == '.jpg'])
    
    print(f"📸 Imagens Azure: {len(azure_images)}")
    print(f"📸 Imagens Manual: {len(manual_images)}")
    print()
    
    # Análise detalhada
    comparison_results = []
    
    for i, (azure_img, manual_img) in enumerate(zip(azure_images, manual_images), 1):
        print(f"🖼️  IMAGEM {i}")
        print("-" * 40)
        
        # Analisar imagem Azure
        azure_analysis = analyze_single_image(azure_img, "Azure Figures")
        
        # Analisar imagem Manual
        manual_analysis = analyze_single_image(manual_img, "Manual PDF")
        
        # Comparar
        comparison = compare_images(azure_analysis, manual_analysis)
        comparison_results.append({
            'image_pair': i,
            'azure_file': azure_img.name,
            'manual_file': manual_img.name,
            'azure_analysis': azure_analysis,
            'manual_analysis': manual_analysis,
            'comparison': comparison
        })
        
        # Exibir comparação
        print(f"📊 COMPARAÇÃO:")
        print(f"   Dimensões: Azure {azure_analysis['dimensions']} vs Manual {manual_analysis['dimensions']}")
        print(f"   Tamanhos: Azure {azure_analysis['file_size_mb']:.2f}MB vs Manual {manual_analysis['file_size_mb']:.2f}MB")
        print(f"   Pixels: Azure {azure_analysis['total_pixels']:,} vs Manual {manual_analysis['total_pixels']:,}")
        print(f"   Qualidade: {comparison['quality_assessment']}")
        print()
    
    # Relatório final
    generate_quality_report(comparison_results)
    
    # Salvar análise detalhada
    save_analysis_results(comparison_results)

def analyze_single_image(image_path, method_name):
    """Analisa uma única imagem"""
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            file_size = os.path.getsize(image_path)
            
            # Calcular hash para verificar se são idênticas
            with open(image_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            
            return {
                'method': method_name,
                'filename': image_path.name,
                'dimensions': f"{width}x{height}",
                'width': width,
                'height': height,
                'total_pixels': width * height,
                'file_size_bytes': file_size,
                'file_size_mb': file_size / (1024 * 1024),
                'format': img.format,
                'mode': img.mode,
                'file_hash': file_hash
            }
    except Exception as e:
        return {
            'method': method_name,
            'error': str(e),
            'filename': image_path.name
        }

def compare_images(azure_analysis, manual_analysis):
    """Compara duas análises de imagem"""
    
    if 'error' in azure_analysis or 'error' in manual_analysis:
        return {'quality_assessment': 'Erro na análise'}
    
    # Verificar se são idênticas
    if azure_analysis['file_hash'] == manual_analysis['file_hash']:
        return {
            'identical_files': True,
            'quality_assessment': '✅ Imagens idênticas (mesmo hash)',
            'size_comparison': 'Iguais',
            'resolution_comparison': 'Iguais'
        }
    
    # Comparar dimensões
    azure_pixels = azure_analysis['total_pixels']
    manual_pixels = manual_analysis['total_pixels']
    
    if azure_pixels == manual_pixels:
        resolution_comparison = "✅ Mesma resolução"
    elif azure_pixels > manual_pixels:
        diff_percent = ((azure_pixels - manual_pixels) / manual_pixels) * 100
        resolution_comparison = f"📈 Azure {diff_percent:.1f}% maior"
    else:
        diff_percent = ((manual_pixels - azure_pixels) / azure_pixels) * 100
        resolution_comparison = f"📈 Manual {diff_percent:.1f}% maior"
    
    # Comparar tamanhos de arquivo
    azure_size = azure_analysis['file_size_mb']
    manual_size = manual_analysis['file_size_mb']
    
    if abs(azure_size - manual_size) < 0.01:
        size_comparison = "✅ Mesmo tamanho"
    elif azure_size > manual_size:
        diff_percent = ((azure_size - manual_size) / manual_size) * 100
        size_comparison = f"📊 Azure {diff_percent:.1f}% maior"
    else:
        diff_percent = ((manual_size - azure_size) / azure_size) * 100
        size_comparison = f"📊 Manual {diff_percent:.1f}% maior"
    
    # Avaliação geral
    if azure_pixels == manual_pixels:
        quality_assessment = "✅ Mesma qualidade de resolução"
    else:
        quality_assessment = f"⚠️ Resoluções diferentes: {resolution_comparison}"
    
    return {
        'identical_files': False,
        'quality_assessment': quality_assessment,
        'resolution_comparison': resolution_comparison,
        'size_comparison': size_comparison
    }

def generate_quality_report(comparison_results):
    """Gera relatório final de qualidade"""
    
    print("📋 RELATÓRIO DE QUALIDADE FINAL")
    print("=" * 60)
    
    total_images = len(comparison_results)
    identical_count = sum(1 for r in comparison_results if r['comparison'].get('identical_files', False))
    
    print(f"📊 Total de imagens analisadas: {total_images}")
    print(f"🔗 Imagens idênticas: {identical_count}")
    print(f"🔄 Imagens diferentes: {total_images - identical_count}")
    print()
    
    if identical_count == total_images:
        print("🎉 RESULTADO: Todos os métodos produzem imagens IDÊNTICAS!")
        print("✅ A extração manual mantém 100% da qualidade da extração Azure")
    elif identical_count > 0:
        percentage = (identical_count / total_images) * 100
        print(f"📈 RESULTADO: {percentage:.1f}% das imagens são idênticas")
        print("⚠️ Algumas diferenças detectadas entre os métodos")
    else:
        print("❌ RESULTADO: Nenhuma imagem idêntica encontrada")
        print("🔍 Diferenças significativas entre os métodos")
    
    print()
    
    # Análise de performance vs qualidade
    print("🏆 ANÁLISE PERFORMANCE vs QUALIDADE:")
    print("-" * 40)
    
    # Dados do diagnóstico anterior
    azure_time = 49.26  # segundos
    manual_time = 0.13  # segundos
    speed_improvement = azure_time / manual_time
    
    print(f"⚡ Manual é {speed_improvement:.0f}x mais rápido que Azure")
    print(f"🎯 Qualidade mantida: {(identical_count/total_images)*100:.1f}%")
    
    if identical_count == total_images:
        print("🏅 RECOMENDAÇÃO: Use método Manual (mesma qualidade, muito mais rápido)")
    else:
        print("🤔 RECOMENDAÇÃO: Analise diferenças antes de escolher o método")

def save_analysis_results(comparison_results):
    """Salva os resultados da análise em arquivo JSON"""
    
    output_file = "image_quality_analysis.json"
    
    analysis_summary = {
        'analysis_date': '2025-08-28',
        'total_images_analyzed': len(comparison_results),
        'methods_compared': ['Azure Figures', 'Manual PDF'],
        'comparison_results': comparison_results,
        'summary': {
            'identical_images': sum(1 for r in comparison_results if r['comparison'].get('identical_files', False)),
            'different_images': sum(1 for r in comparison_results if not r['comparison'].get('identical_files', False)),
            'quality_assessment': 'All images identical' if all(r['comparison'].get('identical_files', False) for r in comparison_results) else 'Some differences detected'
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_summary, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Análise detalhada salva em: {output_file}")

if __name__ == "__main__":
    analyze_image_quality()
