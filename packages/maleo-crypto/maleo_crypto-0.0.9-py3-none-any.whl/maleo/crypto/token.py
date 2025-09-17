import jwt
import secrets
from collections.abc import Iterable, Sequence
from Crypto.PublicKey.RSA import RsaKey
from datetime import timedelta
from enum import StrEnum
from typing import Literal, Union, overload
from maleo.types.dict import StringToAnyDict
from maleo.types.integer import OptionalInteger
from maleo.types.misc import BytesOrString
from maleo.types.string import OptionalString
from .key.rsa.enums import KeyType
from .key.rsa.loader import with_pycryptodome


class RandomFormat(StrEnum):
    BYTES = "bytes"
    HEX = "hex"
    STRING = "string"


@overload
def random(
    format: Literal[RandomFormat.BYTES],
    nbytes: OptionalInteger = None,
    /,
) -> bytes: ...
@overload
def random(
    format: Literal[RandomFormat.HEX, RandomFormat.STRING],
    nbytes: OptionalInteger = None,
    /,
) -> str: ...
def random(
    format: RandomFormat,
    nbytes: OptionalInteger = None,
    /,
) -> BytesOrString:
    if format is RandomFormat.BYTES:
        return secrets.token_bytes(nbytes)
    elif format is RandomFormat.HEX:
        return secrets.token_hex(nbytes)
    elif format is RandomFormat.STRING:
        return secrets.token_urlsafe(nbytes)


@overload
def encode(
    payload: StringToAnyDict,
    key: RsaKey,
) -> str: ...
@overload
def encode(
    payload: StringToAnyDict,
    key: BytesOrString,
    *,
    password: OptionalString = None,
) -> str: ...
def encode(
    payload: StringToAnyDict,
    key: Union[RsaKey, BytesOrString],
    *,
    password: OptionalString = None,
) -> str:
    if isinstance(key, RsaKey):
        private_key = key
    else:
        private_key = with_pycryptodome(
            KeyType.PRIVATE, extern_key=key, passphrase=password
        )

    token = jwt.encode(
        payload=payload,
        key=private_key.export_key(),
        algorithm="RS256",
    )

    return token


def decode(
    token: str,
    key: Union[RsaKey, BytesOrString],
    audience: str | Iterable[str] | None = None,
    subject: OptionalString = None,
    issuer: str | Sequence[str] | None = None,
    leeway: float | timedelta = 0,
) -> StringToAnyDict:
    if isinstance(key, RsaKey):
        public_key = key
    else:
        public_key = with_pycryptodome(KeyType.PRIVATE, extern_key=key)

    payload = jwt.decode(
        jwt=token,
        key=public_key.export_key(),
        algorithms=["RS256"],
        audience=audience,
        subject=subject,
        issuer=issuer,
        leeway=leeway,
    )

    return payload
