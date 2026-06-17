
from flask import Flask, request, render_template, send_file, redirect, url_for, flash, abort
import os
from cryptography.fernet import Fernet
import io
import uuid
from functools import wraps

from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate

from config import active_config
from models import db, User, File, BlockchainLedger   # single source of truth
from chain import add_block   # AUDIT: blockchain event recording

app = Flask(__name__)
app.config.from_object(active_config)

# --- Extensions ---
db.init_app(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)       # enables: flask db init / migrate / upgrade

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

os.makedirs('uploads', exist_ok=True)

ALLOWED_EXTENSIONS = app.config['ALLOWED_EXTENSIONS']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def admin_required(f):
    """
    ADMIN-01: Restrict access to is_admin=True users only.
    Returns HTTP 403 for any authenticated non-admin user.
    Unauthenticated users are handled upstream by @login_required.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- DB setup (dev convenience — production uses: flask db upgrade) ---
with app.app_context():
    db.create_all()
    # CHAIN-05: Auto-create genesis block on first run if ledger is empty
    if BlockchainLedger.query.count() == 0:
        try:
            from chain import add_block
            add_block(action="GENESIS", actor="system", detail="chain initialized")
        except ImportError:
            pass


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
        
        # ADMIN-05: First registered account becomes admin
        is_first_user = User.query.count() == 0
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_pw,
            encryption_key=user_key,
            is_admin=is_first_user
        )
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
            # AUDIT-05: Record successful login with username + client IP
            add_block(action="LOGIN", actor=user.username, detail=request.remote_addr)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        else:
            # AUDIT-04: Record failed login with email attempted + client IP
            add_block(action="LOGIN_FAIL", actor=email, detail=request.remote_addr)
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

        # AUDIT-01: Record upload event after successful encrypt + DB write
        add_block(action="UPLOAD", actor=current_user.username, detail=file.filename)
        
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

    # AUDIT-02: Record download event after successful decryption
    add_block(action="DOWNLOAD", actor=current_user.username, detail=file_record.original_filename)
    
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

    # AUDIT-03: Record delete event after successful disk + DB removal
    add_block(action="DELETE", actor=current_user.username, detail=file_record.original_filename)
    
    flash('File deleted successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """
    ADMIN-01: admin_required enforces is_admin=True; non-admins get 403.
    ADMIN-04: verify_chain() runs on every page load — no button needed.
    ADMIN-06: renders ledger only — no file download or user management.
    """
    from chain import verify_chain
    from models import BlockchainLedger

    # ADMIN-04: live integrity check on every load
    chain_ok, broken_at = verify_chain()

    # ADMIN-02: newest-first for quick recent-activity view
    blocks = BlockchainLedger.query.order_by(BlockchainLedger.id.desc()).all()
    total_blocks = BlockchainLedger.query.count()

    return render_template(
        'admin.html',
        chain_ok=chain_ok,
        broken_at=broken_at,
        blocks=blocks,
        total_blocks=total_blocks
    )

if __name__ == '__main__':
    app.run(debug=True)