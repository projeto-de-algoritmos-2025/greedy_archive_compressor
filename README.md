# Greedy Archive Compressor (Huffman + QR)

Projeto que comprime arquivos usando o algoritmo de Huffman e gera um QR code com o link para baixar o arquivo comprimido pelo celular.

Funcionalidades iniciais:
- Compressor/descompressor Huffman (arquivo em `src/huffman.py`).
- Servidor Flask para upload e geração de QR (em progresso).

Como usar (RÁPIDO):

Pré-requisitos: Python 3.8+ e virtualenv (recomendado).

1. Criar e ativar um ambiente virtual (Windows PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Instalar dependências:

```powershell
pip install -r requirements.txt
```

3. Executar o servidor (desenvolvimento):

```powershell
python -m src.app
```

4. No navegador, abra `http://127.0.0.1:5000/` e envie um arquivo. Após a compressão você verá um QR code e um link direto para baixar o arquivo `.huff`.

5. Escanear o QR com o celular — ele apontará para o link de download e você poderá baixar o arquivo comprimido diretamente no celular.

Observações e próximos passos:
- A implementação atual serve os arquivos a partir da pasta `uploads/` para desenvolvimento. Em produção, servir via CDN ou S3 é recomendado.
- O formato do arquivo `.huff` usado aqui inclui um cabeçalho simples com as tabelas de código; não é compatível com ferramentas externas.