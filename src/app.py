import os
import socket
from flask import Flask, request, render_template, send_from_directory, url_for, send_file
from werkzeug.utils import secure_filename
import huffman
import qrcode
import threading
import time
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, 'templates'))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def delete_file_later(path, delay=300):
    """Deleta o arquivo após um certo tempo (em segundos)."""
    def _delete():
        time.sleep(delay)
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"Arquivo {path} deletado após {delay} segundos.")
            except Exception as e:
                print(f"Erro ao deletar {path}: {e}")
    threading.Thread(target=_delete, daemon=True).start()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('file')
    if not f:
        return 'No file', 400
    filename = secure_filename(f.filename)
    in_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    f.save(in_path)

    # Comprime o arquivo
    out_name = filename + '.huff'
    out_path = os.path.join(app.config['UPLOAD_FOLDER'], out_name)
    huffman.compress_file(in_path, out_path)

    # Gera também a versão descomprimida do .huff
    decompressed_name = filename  # mesmo nome original
    decompressed_path = os.path.join(app.config['UPLOAD_FOLDER'], decompressed_name)
    huffman.decompress_file(out_path, decompressed_path)

    # URL da página de resultados
    result_page_url = url_for('result_page', filename=filename, _external=True)

    # QR code apontando para a página de resultados
    qr = qrcode.make(result_page_url)
    qr_path = os.path.join(app.config['UPLOAD_FOLDER'], filename + '.png')
    qr.save(qr_path)

    # Agenda exclusão do QR code após 30 minutos
    delete_file_later(qr_path, delay=300)

    # Opcional: também deletar o arquivo .huff e o descomprimido após 30min
    delete_file_later(out_path, delay=300)
    delete_file_later(decompressed_path, delay=300)

    return render_template(
        'result.html',
        download_url=url_for('download_file', filename=out_name, _external=True),
        download_url_decompressed=url_for('download_file', filename=decompressed_name, _external=True),
        qr_image=os.path.basename(qr_path)
    )


# Nova rota para a página de resultados
@app.route('/result/<filename>')
def result_page(filename):
    out_name = filename + '.huff'
    decompressed_name = filename
    return render_template(
        'result.html',
        download_url=url_for('download_file', filename=out_name, _external=True),
        download_url_decompressed=url_for('download_file', filename=decompressed_name, _external=True),
        qr_image=None  # não precisamos mostrar QR aqui
    )


@app.route('/decompress', methods=['POST'])
def decompress():
    f = request.files.get('file')
    if not f:
        return 'No file', 400

    filename = secure_filename(f.filename)
    in_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    f.save(in_path)

    # Nome do arquivo descomprimido
    if filename.endswith('.huff'):
        out_name = filename[:-5]  # remove '.huff'
    else:
        out_name = filename + '.decompressed'
    out_path = os.path.join(app.config['UPLOAD_FOLDER'], out_name)

    try:
        huffman.decompress_file(in_path, out_path)
    except Exception as e:
        return f'Erro ao descomprimir: {str(e)}', 500

    # Retorna o arquivo descomprimido como download imediato
    return send_file(out_path, as_attachment=True, download_name=out_name)


@app.route('/download_decompressed/<filename>', methods=['GET'])
def download_decompressed(filename):
    in_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if not os.path.exists(in_path):
        return "Arquivo não encontrado", 404

    # Nome do arquivo descomprimido
    if filename.endswith('.huff'):
        out_name = filename[:-5]  # remove ".huff"
    else:
        out_name = filename + '.decompressed'

    out_path = os.path.join(app.config['UPLOAD_FOLDER'], out_name)

    try:
        huffman.decompress_file(in_path, out_path)
    except Exception as e:
        return f"Erro ao descomprimir: {str(e)}", 500

    # Retorna o arquivo descomprimido como download
    return send_file(out_path, as_attachment=True, download_name=out_name)


@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    # bind to 0.0.0.0 so the server is reachable from other devices on the LAN
    app.run(host=os.environ.get('FLASK_RUN_HOST', '0.0.0.0'), debug=True)
