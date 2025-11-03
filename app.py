from flask import Flask, request, render_template, send_file, redirect, url_for
import os
from cryptography.fernet import Fernet
import io

app = Flask(__name__)

KEY = b'xQslvTPBF-IKGg4AoIGRT1wSPf89fODkAV0Wmv37zcM='

os.makedirs('uploads', exist_ok=True)
fernet = Fernet(KEY)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file selected!')
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error='No file selected!')
        
        # Encrypt
        file_content = file.read()
        encrypted_content = fernet.encrypt(file_content)
        
        # Save
        filename = os.path.join('uploads', file.filename + '.enc')
        with open(filename, 'wb') as f:
            f.write(encrypted_content)
        
        return redirect(url_for('index'))
        
        return render_template('index.html', message=f'Uploaded {file.filename} (encrypted)!')
    
    # List files
    files = [f[:-4] for f in os.listdir('uploads') if f.endswith('.enc')]
    return render_template('index.html', files=files)

@app.route('/download/<filename>')
def download(filename):
    enc_path = os.path.join('uploads', filename + '.enc')
    
    if not os.path.exists(enc_path):
        return 'File not found!', 404
    
    # Decrypt
    with open(enc_path, 'rb') as f:
        encrypted_content = f.read()
    
    decrypted_content = fernet.decrypt(encrypted_content)
    return send_file(io.BytesIO(decrypted_content), as_attachment=True, download_name=filename)

if __name__ == '__main__':
    app.run(debug=True)