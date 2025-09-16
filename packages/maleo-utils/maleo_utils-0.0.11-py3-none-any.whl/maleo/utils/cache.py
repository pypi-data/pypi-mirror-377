from typing import Literal, overload
from maleo.enums.cache import Origin, Layer
from maleo.types.base.string import ListOfStrings, OptionalString


@overload
def build_namespace(
    *ext: str,
    base: OptionalString = None,
    origin: Literal[Origin.SERVICE],
    layer: Layer,
    sep: str = ":",
) -> str: ...
@overload
def build_namespace(
    *ext: str,
    base: OptionalString = None,
    client: str,
    origin: Literal[Origin.CLIENT],
    layer: Layer,
    sep: str = ":",
) -> str: ...
def build_namespace(
    *ext: str,
    base: OptionalString = None,
    client: OptionalString = None,
    origin: Origin,
    layer: Layer,
    sep: str = ":",
) -> str:
    slugs: ListOfStrings = []
    if base is not None:
        slugs.append(base)
    slugs.extend([origin, layer])
    if client is not None:
        slugs.append(client)
    slugs.extend(ext)
    return sep.join(slugs)


def build_key(*ext: str, namespace: str, sep: str = ":"):
    return sep.join([namespace, *ext])
