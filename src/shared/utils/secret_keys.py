import logging
from typing import Literal, Union
from pathlib import Path

import aiofiles
from pydantic import SecretStr

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

logger = logging.getLogger("app")

async def generate_rsa_keys(path: Path, key_size: int = 2048) -> None:
    if key_size < 2048:
        raise ValueError("RSA key size must be at least 2048 bits for security.")
    
    private_key = rsa.generate_private_key(
        public_exponent=65537, 
        key_size=key_size,
    )

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    private_path = path / "rsa_private.pem"
    public_path = path / "rsa_public.pem"

    async with aiofiles.open(private_path, "wb") as f:
        await f.write(private_pem)
    async with aiofiles.open(public_path, "wb") as f:
        await f.write(public_pem)
    private_path.chmod(0o600)
    public_path.chmod(0o644)
    logger.info(f"RSA keys generated and saved to {path}")


async def open_rsa_key(key_type: Literal["private", "public"], secret_dir: Path, autogenerate: bool = False) -> Union[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    if not secret_dir.is_dir():
        raise ValueError(f"This is not a directory: {secret_dir}")
    match key_type:
        case "private":
            path = secret_dir / "rsa_private"
        case "public":
            path = secret_dir / "rsa_public"
        case _:
            raise ValueError(f"Key type is not correct: {key_type}")

    if path.is_file():
        async with aiofiles.open(path, "rb") as f:
            key_data = await f.read()
            try:
                if key_type == "private":
                    key = serialization.load_pem_private_key(key_data, password=None)
                    if not isinstance(key, rsa.RSAPrivateKey):
                        raise ValueError("Loaded key is not an RSA private key")
                else:
                    key = serialization.load_pem_public_key(key_data)
                    if not isinstance(key, rsa.RSAPublicKey):
                        raise ValueError("Loaded key is not an RSA public key")
                return key
            except ValueError as e:
                raise ValueError(f"Error reading file from {path}: {e}")
            
    else:
        if not autogenerate:
            raise FileNotFoundError(f"RSA {key_type} key file not found: {path}.")
        
        logger.info(f"RSA {key_type} key not found. Generating new key pair...")
        await generate_rsa_keys(secret_dir)
        return await open_rsa_key(key_type=key_type, secret_dir=secret_dir, autogenerate=False) 


def private_key_to_secret_str(key) -> SecretStr:
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    return SecretStr(pem.decode())


def public_key_to_secret_str(key) -> SecretStr:
    pem = key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return SecretStr(pem.decode())
