#!/usr/bin/env python3
"""
Encrypt HTML slide decks for GitHub Pages deployment.

Algorithm: AES-256-GCM with PBKDF2-HMAC-SHA256 key derivation (100k iterations).
Each run generates a fresh random salt and IV — matching parameters are embedded
in the output JSON so the browser can derive the same key and decrypt.

Usage:
    DECKPASSWORD=yatkernel python encrypt.py
"""
import os
import sys
import json
import base64
from pathlib import Path

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
except ImportError:
    print("Error: 'cryptography' package required.  Run: pip install cryptography")
    sys.exit(1)

ROOT = Path(__file__).parent
SRC  = ROOT / "src"
OUT  = ROOT / "docs" / "encrypted"

DECKS = {
    "client": SRC / "CLIENT_DECK.html",
    "pitch": SRC / "PITCH_DECK.html",
}


def encrypt(plaintext: bytes, password: str) -> dict:
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100_000
    )
    key = kdf.derive(password.encode("utf-8"))
    iv = os.urandom(12)
    ct = AESGCM(key).encrypt(iv, plaintext, None)
    return {
        "salt": base64.b64encode(salt).decode(),
        "iv": base64.b64encode(iv).decode(),
        "ciphertext": base64.b64encode(ct).decode(),
    }


def main():
    password = os.environ.get("DECKPASSWORD", "").strip()
    if not password:
        print("Error: DECKPASSWORD environment variable is not set.")
        sys.exit(1)

    OUT.mkdir(exist_ok=True)

    for name, src_path in DECKS.items():
        if not src_path.exists():
            print(f"  skip  {src_path.name} — not found")
            continue
        data = encrypt(src_path.read_bytes(), password)
        out = OUT / f"{name}.enc.json"
        out.write_text(json.dumps(data))
        print(f"  encrypted  {src_path.name}  →  {out.relative_to(ROOT)}")

    print("Done.")


if __name__ == "__main__":
    main()
