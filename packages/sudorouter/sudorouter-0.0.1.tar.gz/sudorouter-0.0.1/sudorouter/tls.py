import base64
import hashlib
from datetime import datetime, timezone, timedelta
from ssl import SSLCertVerificationError, VerifyMode

from OpenSSL.SSL import Connection, X509VerificationCodes
from OpenSSL.crypto import X509
from cryptography import x509
from cryptography.hazmat.bindings._rust import ObjectIdentifier
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from urllib3.contrib.pyopenssl import PyOpenSSLContext, _stdlib_to_openssl_verify, inject_into_urllib3
from urllib3.util import create_urllib3_context

from .quoter import get_tee_quoter, TeeType


class TeeOID:
    TYPE = ObjectIdentifier("2.23.133.5.4.8")
    QUOTE = ObjectIdentifier("2.23.133.5.4.9")
    NONCE = ObjectIdentifier("2.23.133.5.4.10")
    USER = ObjectIdentifier("2.23.133.5.4.11")


def verify_callback(connection: Connection, x509: X509, error_number: int, error_depth: int, ok: int) -> bool:
    if error_number != X509VerificationCodes.ERR_DEPTH_ZERO_SELF_SIGNED_CERT:
        return error_number == 0
    cert = x509.to_cryptography()

    now = datetime.now(tz=timezone.utc)
    if now < cert.not_valid_before_utc:
        raise SSLCertVerificationError(f"current time {now} is before {cert.not_valid_before}")
    if now > cert.not_valid_after_utc:
        raise SSLCertVerificationError(f"current time {now} is after {cert.not_valid_after}")

    public_key = cert.public_key()
    try:
        public_key.verify(cert.signature, cert.tbs_certificate_bytes, ec.ECDSA(cert.signature_hash_algorithm))
    except Exception as e:
        raise SSLCertVerificationError("verify certificate failed", e)

    quoter = get_tee_quoter(
        TeeType(cert.extensions.get_extension_for_oid(TeeOID.TYPE).value.public_bytes().decode())
    )
    report = quoter.verify(
        cert.extensions.get_extension_for_oid(TeeOID.QUOTE).value.public_bytes(),
        cert.extensions.get_extension_for_oid(TeeOID.NONCE).value.public_bytes(),
    )
    cert_pubkey_hash = report.user_data[:32]
    pubkey_hash = hashlib.sha256(
        public_key.public_bytes(
            encoding=serialization.Encoding.DER, format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    ).digest()
    if cert_pubkey_hash != pubkey_hash:
        raise SSLCertVerificationError("public key mismatch")
    return True


def create_cert(
    user_id: int, private_key: ec.EllipticCurvePrivateKey, expires: timedelta
) -> x509.Certificate:
    now = datetime.now(tz=timezone.utc)
    name = x509.Name(
        [
            x509.NameAttribute(oid=x509.NameOID.COMMON_NAME, value="amanises"),
            x509.NameAttribute(oid=x509.NameOID.ORGANIZATION_NAME, value="amanises"),
        ]
    )
    return (
        x509.CertificateBuilder()
        .public_key(private_key.public_key())
        .serial_number(1014)
        .not_valid_before(now)
        .not_valid_after(now + expires)
        .subject_name(name)
        .issuer_name(name)
        .add_extension(extval=x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(extval=x509.ExtendedKeyUsage(usages=[x509.OID_CLIENT_AUTH]), critical=False)
        .add_extension(
            extval=x509.UnrecognizedExtension(oid=TeeOID.USER, value=str(user_id).encode()), critical=False
        )
        .sign(private_key, hashes.SHA256())
    )


def verify_mode_setter(self, value: VerifyMode) -> None:
    self._ctx.set_verify(_stdlib_to_openssl_verify[value], verify_callback)


def monkey_patch_urllib3():
    PyOpenSSLContext.verify_mode = property(
        PyOpenSSLContext.verify_mode.fget,
        verify_mode_setter,
    )

    inject_into_urllib3()


def mutual_ssl_context(user_id: int, private_key_der: str) -> PyOpenSSLContext:
    monkey_patch_urllib3()
    ctx: PyOpenSSLContext = create_urllib3_context()
    private_key = serialization.load_der_private_key(base64.b64decode(private_key_der), password=None)
    ctx._ctx.use_privatekey(private_key)
    ctx._ctx.use_certificate(create_cert(user_id, private_key, timedelta(minutes=10)))
    return ctx
