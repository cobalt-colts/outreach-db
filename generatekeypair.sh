#!/usr/bin/env bash

set -euo pipefail

KEY_DIR="${HOME}/.ssh"
PRIVATE_KEY="${KEY_DIR}/id_rsa_jwt"
PUBLIC_KEY="${KEY_DIR}/id_rsa_jwt.pub"

echo "Creating SSH directory if it doesn't exist..."
mkdir -p "${KEY_DIR}"
chmod 700 "${KEY_DIR}"

if [[ -f "${PRIVATE_KEY}" ]]; then
  echo "Key already exists at ${PRIVATE_KEY}"
  exit 0
fi

echo "Generating RSA keypair for JWT..."

ssh-keygen \
  -t rsa \
  -b 4096 \
  -m PEM \
  -f "${PRIVATE_KEY}" \
  -N "" \
  -C "jwt-key"

echo "Setting secure permissions..."
chmod 600 "${PRIVATE_KEY}"
chmod 644 "${PUBLIC_KEY}"

echo "Done."
echo "Private key: ${PRIVATE_KEY}"
echo "Public key:  ${PUBLIC_KEY}"
