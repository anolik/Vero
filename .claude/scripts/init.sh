#!/bin/bash
# Environment setup for Vero

echo "Setting up Vero..."

# Check Python version
python --version 2>/dev/null || python3 --version 2>/dev/null || {
  echo "ERROR: Python 3.11+ required"
  exit 1
}

# Install uv if not present
if ! command -v uv &> /dev/null; then
  echo "Installing uv..."
  pip install uv
fi

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null

uv pip install -r requirements.txt

# Create .env if not exists
if [ ! -f .env ]; then
  cat > .env << 'EOF'
# Vero Configuration
ADMIN_USERNAME=admin
ADMIN_PASSWORD=changeme
TOKEN_EXPIRY_DAYS=30
DATABASE_URL=sqlite:///vero.db
SECRET_KEY=change-this-secret-key
EOF
  echo "Created .env — CHANGE DEFAULT VALUES before use"
fi

# Create uploads directory
mkdir -p uploads

echo ""
echo "Setup complete!"
echo "Run: uvicorn main:app --reload"
