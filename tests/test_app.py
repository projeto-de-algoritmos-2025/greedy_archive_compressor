import io
import os
from src import app as flask_app


def test_upload_creates_compressed_and_qr(tmp_path, monkeypatch):
    client = flask_app.app.test_client()
    data = {
        'file': (io.BytesIO(b'hello huffman world'), 'hello.txt')
    }
    resp = client.post('/upload', data=data, content_type='multipart/form-data')
    assert resp.status_code == 200
    text = resp.get_data(as_text=True)
    assert 'Link para download' in text

    
    uploads = os.path.join(os.path.dirname(os.path.dirname(flask_app.__file__)), 'uploads')
    assert os.path.isdir(uploads)
    
    found_huff = any(f.endswith('.huff') and 'hello.txt' in f for f in os.listdir(uploads))
    found_png = any(f.endswith('.png') and 'hello.txt' in f for f in os.listdir(uploads))
    assert found_huff
    assert found_png
