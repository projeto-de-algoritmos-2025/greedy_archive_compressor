import os
import socket
from flask import Flask, request, render_template, send_from_directory, url_for
from werkzeug.utils import secure_filename
from src import huffman
import qrcode

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, 'templates'))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
    out_name = filename + '.huff'
    out_path = os.path.join(app.config['UPLOAD_FOLDER'], out_name)
    huffman.compress_file(in_path, out_path)

    # build download url for .huff. If running on localhost, prefer LAN IP so mobile devices can reach it
    download_url = url_for('download_file', filename=out_name, _external=True)

    # if url contains 127.0.0.1 or localhost, try to replace with LAN IP
    if '127.0.0.1' in download_url or 'localhost' in download_url:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
            s.close()
            download_url = download_url.replace('127.0.0.1', local_ip).replace('localhost', local_ip)
        except Exception:
            pass

    # generate QR pointing to the .huff download
    qr = qrcode.make(download_url)
    qr_path = os.path.join(app.config['UPLOAD_FOLDER'], filename + '.png')
    qr.save(qr_path)

    return render_template('result.html', download_url=download_url, qr_image=os.path.basename(qr_path))


@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


if __name__ == '__main__':
    # bind to 0.0.0.0 so the server is reachable from other devices on the LAN
    app.run(host=os.environ.get('FLASK_RUN_HOST', '0.0.0.0'), debug=True)
