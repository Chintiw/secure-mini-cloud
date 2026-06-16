from flask import Flask, request, render_template, send_file, redirect, url_for, flash
import os
from cryptography.fernet import Fernet
import io
import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32) # NFR-03: Session Security
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///secure_cloud.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB limit

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

KEY = b'xQslvTPBF-IKGg4AoIGRT1wSPf89fODkAV0Wmv37zcM='

os.makedirs('uploads', exist_ok=True)
fernet = Fernet(KEY)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'xlsx', 'jpg', 'png', 'zip'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.template_filter('filesizeformat')
def filesizeformat(value):
    if value < 1024:
        return f"{value} B"
    elif value < 1024 * 1024:
        return f"{value / 1024:.1f} KB"
    else:
        return f"{value / (1024 * 1024):.1f} MB"

@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File too large! Maximum size is 50 MB.', 'danger')
    return redirect(url_for('index'))

# --- Models ---
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    encryption_key = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Setup DB ---
with app.app_context():
    db.create_all()

# --- Auth Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            flash('Email or username already exists', 'danger')
            return redirect(url_for('register'))
            
        # bcrypt with work factor >= 12
        hashed_pw = bcrypt.generate_password_hash(password, 12).decode('utf-8')
        # generate per-user Fernet key (ISO-01)
        user_key = Fernet.generate_key().decode('utf-8')
        
        new_user = User(username=username, email=email, password_hash=hashed_pw, encryption_key=user_key)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

# --- Existing App Routes (M1 keeps existing behavior mostly) ---
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected!', 'danger')
            return redirect(url_for('index'))
        file = request.files['file']
        if file.filename == '':
            flash('No file selected!', 'danger')
            return redirect(url_for('index'))
            
        if not allowed_file(file.filename):
            flash('File type not allowed!', 'danger')
            return redirect(url_for('index'))
        
        # ISO-02: Encrypt with per-user key
        user_fernet = Fernet(current_user.encryption_key.encode('utf-8'))
        file_content = file.read()
        encrypted_content = user_fernet.encrypt(file_content)
        
        # ISO-05: UUIDs for files
        file_uuid = str(uuid.uuid4())
        stored_filename = f"{file_uuid}.enc"
        
        # ISO-03: Per-user upload directories
        user_dir = os.path.join('uploads', str(current_user.id))
        os.makedirs(user_dir, exist_ok=True)
        
        file_path = os.path.join(user_dir, stored_filename)
        with open(file_path, 'wb') as f:
            f.write(encrypted_content)
            
        # Store in DB
        new_file = File(
            id=file_uuid,
            owner_id=current_user.id,
            original_filename=file.filename,
            stored_filename=stored_filename,
            file_size=len(file_content)
        )
        db.session.add(new_file)
        db.session.commit()
        
        flash(f'Uploaded {file.filename} (encrypted)!', 'success')
        return redirect(url_for('index'))
    
    # List user's files from DB
    files = File.query.filter_by(owner_id=current_user.id).all()
    return render_template('index.html', files=files)

@app.route('/download/<file_uuid>')
@login_required
def download(file_uuid):
    file_record = File.query.get_or_404(file_uuid)
    
    # ISO-04: Ownership check
    if file_record.owner_id != current_user.id:
        from werkzeug.exceptions import Forbidden
        return Forbidden("You do not have permission to access this file.")
        
    user_dir = os.path.join('uploads', str(current_user.id))
    enc_path = os.path.join(user_dir, file_record.stored_filename)
    
    if not os.path.exists(enc_path):
        return 'File not found on disk!', 404
    
    # Decrypt
    with open(enc_path, 'rb') as f:
        encrypted_content = f.read()
    
    user_fernet = Fernet(current_user.encryption_key.encode('utf-8'))
    decrypted_content = user_fernet.decrypt(encrypted_content)
    
    return send_file(
        io.BytesIO(decrypted_content), 
        as_attachment=True, 
        download_name=file_record.original_filename
    )

@app.route('/delete/<file_uuid>', methods=['POST'])
@login_required
def delete_file(file_uuid):
    file_record = File.query.get_or_404(file_uuid)
    
    if file_record.owner_id != current_user.id:
        from werkzeug.exceptions import Forbidden
        return Forbidden("You do not have permission to delete this file.")
        
    user_dir = os.path.join('uploads', str(current_user.id))
    enc_path = os.path.join(user_dir, file_record.stored_filename)
    
    if os.path.exists(enc_path):
        os.remove(enc_path)
        
    db.session.delete(file_record)
    db.session.commit()
    
    flash('File deleted successfully.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)