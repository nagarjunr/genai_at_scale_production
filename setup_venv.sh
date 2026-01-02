#!/bin/bash

# Script to setup Python virtual environment with custom SSL certificates
# This script activates the venv, installs certifi, appends custom certs, and sets environment variables

set -e  # Exit on error

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_PATH="${SCRIPT_DIR}/week2/workspace/twin/backend/.venv"
CERTS_DIR="/Users/ran1sgp/WorkSpace/BoschCACerts"

echo -e "${GREEN}==> Activating virtual environment...${NC}"
if [ ! -f "${VENV_PATH}/bin/activate" ]; then
    echo "Error: Virtual environment not found at ${VENV_PATH}"
    echo "Please create it first with: python3 -m venv .venv"
    exit 1
fi

source "${VENV_PATH}/bin/activate"

echo -e "${GREEN}==> Installing certifi package...${NC}"
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org certifi

echo -e "${GREEN}==> Finding certifi cacert.pem location...${NC}"
CACERT_PATH=$(python -c "import certifi; print(certifi.where())")
echo "Certifi location: ${CACERT_PATH}"

echo -e "${GREEN}==> Appending custom certificates to cacert.pem...${NC}"
# Append RB IssuingCA certificate (with spaces in filename)
if [ -f "${CERTS_DIR}/RB_IssuingCA_RSA_G21-pem.cer" ]; then
    cat "${CERTS_DIR}/RB_IssuingCA_RSA_G21-pem.cer" >> "${CACERT_PATH}"
    echo "✓ Appended RB_IssuingCA_RSA_G21-pem.cer"
else
    echo -e "${YELLOW}Warning: RB_IssuingCA_RSA_G21-pem.cer not found${NC}"
fi

# Append RB RootCA certificate
if [ -f "${CERTS_DIR}/RB_RootCA_RSA_G01-pem.cer" ]; then
    cat "${CERTS_DIR}/RB_RootCA_RSA_G01-pem.cer" >> "${CACERT_PATH}"
    echo "✓ Appended RB_RootCA_RSA_G01-pem.cer"
else
    echo -e "${YELLOW}Warning: RB_RootCA_RSA_G01-pem.cer not found${NC}"
fi

echo -e "${GREEN}==> Setting SSL environment variables...${NC}"
export SSL_CERT_FILE="${CACERT_PATH}"
export REQUESTS_CA_BUNDLE="${CACERT_PATH}"
export NODE_EXTRA_CA_CERTS="${CACERT_PATH}"
echo "✓ SSL_CERT_FILE=${SSL_CERT_FILE}"
echo "✓ REQUESTS_CA_BUNDLE=${REQUESTS_CA_BUNDLE}"
echo "✓ NODE_EXTRA_CA_CERTS=${NODE_EXTRA_CA_CERTS}"

echo -e "${GREEN}==> Upgrading pip...${NC}"
pip install --upgrade pip

echo -e "${GREEN}==> Setup complete!${NC}"
echo ""
echo "To use these settings in your current shell, run:"
echo -e "${YELLOW}source setup_venv.sh${NC}"
echo ""
echo "Or add these exports to your shell profile (~/.zshrc):"
echo "export SSL_CERT_FILE=${CACERT_PATH}"
echo "export REQUESTS_CA_BUNDLE=${CACERT_PATH}"
echo "export NODE_EXTRA_CA_CERTS=${CACERT_PATH}"