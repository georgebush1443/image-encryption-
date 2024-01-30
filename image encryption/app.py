from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

def pad(data):
    block_size = 16
    return data + (block_size - len(data) % block_size) * b'\0'

def encrypt_image(file_storage, key):
    temp_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_image.png')
    file_storage.save(temp_file_path)

    with open(temp_file_path, 'rb') as file:
        plaintext = file.read()

    plaintext = pad(plaintext)

    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)

    encrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], 'encrypted_image.png')
    with open(encrypted_path, 'wb') as file:
        file.write(cipher.nonce + tag + ciphertext)

    os.remove(temp_file_path)

    return encrypted_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return redirect(url_for('index'))

    image = request.files['image']

    if image.filename == '':
        return redirect(url_for('index'))

    key = get_random_bytes(16)
    encrypted_path = encrypt_image(image, key)

    return render_template('index.html', encrypted_image=encrypted_path)

@app.route('/decrypt', methods=['POST'])
def decrypt():
    encrypted_path = request.form.get('encrypted_image', '')

    if not encrypted_path:
        return redirect(url_for('index'))

    key = get_random_bytes(16)
    decrypted_path = decrypt_image(encrypted_path, key)

    return render_template('index.html', encrypted_image=encrypted_path, decrypted_image=decrypted_path)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    app.run(debug=True)
