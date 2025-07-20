# Azure Document Intelligence - Coordenadas de Figuras em PDF

Este documento explica como interpretar e utilizar as coordenadas de figuras (imagens) retornadas pelo Azure Document Intelligence quando processando documentos PDF.

## Sistema de Coordenadas

O Azure Document Intelligence retorna coordenadas de figuras em um sistema de pontos PDF, onde:
- **72 pontos = 1 polegada**
- O formato do polígono é `[x1, y1, x2, y2, x3, y3, x4, y4]` representando:
  - Superior-esquerdo (x1, y1)
  - Superior-direito (x2, y2)
  - Inferior-direito (x3, y3)
  - Inferior-esquerdo (x4, y4)

## Implementação Atual

O SmartQuest utiliza a classe `PDFImageExtractor` localizada em `app/services/utils/pdf_image_extractor.py` para extrair imagens usando essas coordenadas.

## Convertendo Coordenadas

Para utilizar essas coordenadas com PyMuPDF (fitz), a implementação atual:

1. **Multiplica cada coordenada por 72** para converter de pontos PDF para o sistema PyMuPDF
2. **Extrai valores X e Y separadamente** do polígono
3. **Calcula os limites min/max** para criar um retângulo delimitador
4. **Aplica validação** para garantir dimensões mínimas
5. **Usa matriz de escala 3x** para melhor resolução

## Exemplo de Uso Atual

```python
from app.services.utils.pdf_image_extractor import PDFImageExtractor

# Extrair uma figura específica
image_bytes = PDFImageExtractor.extract_figure_from_pdf(
    pdf_path="documento.pdf",
    page_number=1,  # 1-indexed
    coordinates=[4.783, 0.7453, 7.5413, 0.7457, 7.5403, 2.8879, 4.782, 2.8874]
)

# Converter para base64
base64_image = PDFImageExtractor.get_base64_image(image_bytes)

# Extrair todas as figuras de um resultado do Azure
extracted_figures = PDFImageExtractor.extract_figures_from_azure_result(
    pdf_path="documento.pdf",
    azure_result=azure_response_dict
)
```

## Processo de Transformação

Para as coordenadas `[4.783, 0.7453, 7.5413, 0.7457, 7.5403, 2.8879, 4.782, 2.8874]`:

### 1. Separação de Coordenadas
```python
x_values = [4.783, 7.5413, 7.5403, 4.782]
y_values = [0.7453, 0.7457, 2.8879, 2.8874]
```

### 2. Aplicação do Fator de Escala (72 pontos)
```python
scale_factor = 72
x_values = [344.376, 542.974, 542.902, 344.304]
y_values = [53.662, 53.690, 207.929, 207.893]
```

### 3. Cálculo do Retângulo Delimitador
```python
x0 = min(x_values)  # 344.304
y0 = min(y_values)  # 53.662
x1 = max(x_values)  # 542.974
y1 = max(y_values)  # 207.929

rect = fitz.Rect(344.304, 53.662, 542.974, 207.929)
```

### 4. Validação e Ajustes
```python
# Verifica se o retângulo tem tamanho suficiente
if x1 - x0 < 10 or y1 - y0 < 10:
    # Ampliar para pelo menos dimensões mínimas
    # (implementação completa na classe PDFImageExtractor)
```

## Integração com o Sistema

### Categorização de Imagens

O sistema categoriza automaticamente as imagens extraídas:

```python
# Em AnalyzeService
if AnalyzeService._is_header_image(figure, azure_result):
    header_images.append({"content": base64_image})
else:
    content_images[figure_id] = base64_image
```

### Resposta da API

As imagens do header são incluídas na resposta:

```json
{
  "document_metadata": {
    "network": "...",
    "school": "...",
    "images": [
      {
        "content": "base64_encoded_image_data...",
        "page": 1,
        "position": {
          "x": 344.304,
          "y": 53.662,
          "width": 198.67,
          "height": 154.267
        }
      }
    ]
  }
}
```

## Troubleshooting

### Problemas Comuns

1. **Imagem muito pequena**: O sistema automaticamente amplia retângulos menores que 10x10 pixels
2. **Coordenadas fora dos limites**: O sistema aplica clipping automático às dimensões da página
3. **Página não encontrada**: Verifica se o `page_number` está no intervalo válido

### Logs de Debug

Para depuração, o sistema registra:
- Coordenadas originais e escaladas
- Dimensões da página
- Retângulo de recorte final
- Tamanho da imagem extraída

```python
logger.info(f"Coordenadas originais: {coordinates}")
logger.info(f"Coordenadas escaladas: X={x_values}, Y={y_values}")
logger.info(f"Retângulo de recorte final: {rect}")
logger.info(f"Imagem extraída: {pix.width}x{pix.height}")
```

## Referências Técnicas

- **Azure Document Intelligence**: [Documentação oficial](https://docs.microsoft.com/azure/cognitive-services/document-intelligence/)
- **PyMuPDF**: [Documentação do fitz](https://pymupdf.readthedocs.io/)
- **Implementação**: `app/services/utils/pdf_image_extractor.py`
- **Uso**: `app/services/analyze_service.py` (método `_is_header_image`)

Este documento serve como referência para interpretar e utilizar as coordenadas de figuras retornadas pelo Azure Document Intelligence no contexto do SmartQuest.
        coordinates: Lista de coordenadas [x1, y1, x2, y2, x3, y3, x4, y4]
    
    Returns:
        bytes da imagem extraída
    """
    doc = fitz.open(pdf_path)
    page = doc[page_number - 1]  # Ajuste para 0-indexed
    
    # Extrair valores X e Y
    x_values = [coordinates[i] for i in range(0, len(coordinates), 2)]
    y_values = [coordinates[i+1] for i in range(0, len(coordinates), 2)]
    
    # Aplicar fator de escala de 72 pontos
    scale_factor = 72
    x_values = [x * scale_factor for x in x_values]
    y_values = [y * scale_factor for y in y_values]
    
    # Criar retângulo delimitador
    x0 = min(x_values)
    y0 = min(y_values)
    x1 = max(x_values)
    y1 = max(y_values)
    
    rect = fitz.Rect(x0, y0, x1, y1)
    
    # Extrair a imagem
    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), clip=rect)
    
    # Converter para bytes e retornar
    ...
```

## Exemplo Prático

Para as coordenadas `[4.783, 0.7453, 7.5413, 0.7457, 7.5403, 2.8879, 4.782, 2.8874]`:

1. Após aplicar o fator de escala de 72:
   - X: `[344.376, 542.974, 542.902, 344.304]`
   - Y: `[53.662, 53.690, 207.929, 207.893]`

2. O retângulo de recorte:
   - `Rect(344.304, 53.6616, 542.9736, 207.9288)`

Este documento serve como referência para interpretar corretamente as coordenadas de figuras retornadas pelo Azure Document Intelligence e usá-las para extrair imagens de documentos PDF.
