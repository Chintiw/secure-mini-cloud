Features

Upload: Select any file → Encrypts with a fixed key → Stores as .enc in uploads/.
List & Download: View uploaded files → Click to decrypt and download the original.
Crypto: Uses Python's cryptography library (Fernet for symmetric encryption).
Local-Only: Runs on localhost:5000—no cloud deps.

Tech Stack

Backend: Flask (Python)
Crypto: cryptography (Fernet)
Package Manager: UV (fast alternative to pip)
Frontend: Plain HTML

Quick Start

Clone/Setup:
bashgit clone <your-repo-url>
cd secure-mini-cloud
uv venv  # Create virtual env
source .venv/bin/activate  # Activate (Mac/Linux; use .venv\Scripts\activate on Windows)

Install Deps:
bashuv pip install flask cryptography

Generate Key (one-time):
bashpython -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

Copy the output (e.g., XC6Lx9WkUaAOPS66vqZkWxz8Hom4iEKF_HFcMfK1CC4=) and paste into app.py as KEY = b'YOUR_KEY_HERE'.


Run:
bashmkdir uploads templates  # Create dirs if needed
uv run python app.py

Open http://127.0.0.1:5000 in your browser.



Usage

Upload: Choose a file (e.g., test.txt) → Click "Encrypt & Upload" → Refreshes to show list.
Download: Click the file name (or button) → Browser prompts to save the decrypted original.
Test: Upload a text file, check uploads/test.txt.enc (gibberish binary), download to verify.

Example: Upload "hello.txt" with content "Secret data!" → Downloads back as readable "hello.txt".