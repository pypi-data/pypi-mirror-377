from __future__ import annotations

from typing import Any, Dict

from .errors import DPDInvalidParam


def base_params(default_lang: str, lang: str | None) -> Dict[str, Any]:
    """Return the base query parameters used by most endpoints.

    Includes `type=json` and resolves the effective `lang` using the client's
    default language unless a per-call override is provided.
    """

    return {"type": "json", "lang": lang or default_lang}


def params_with_id_lang(default_lang: str, *, id: int, lang: str | None) -> Dict[str, Any]:
    """Base params with `id` and resolved `lang`."""

    params = base_params(default_lang, lang)
    params["id"] = id
    return params


def params_with_id_lang_active(
    default_lang: str, *, id: int, active: bool | None, lang: str | None
) -> Dict[str, Any]:
    """Base params with `id`, resolved `lang`, and optional `active=yes`."""

    params = params_with_id_lang(default_lang, id=id, lang=lang)
    if active:
        params["active"] = "yes"
    return params


def params_packaging(id: int) -> Dict[str, Any]:
    """Params for `packaging` endpoint (no lang param)."""

    return {"id": id, "type": "json"}


def params_pharmaceuticalstd(id: int) -> Dict[str, Any]:
    """Params for `pharmaceuticalstd` endpoint (no lang param)."""

    return {"id": id, "type": "json"}


def params_drugproduct(
    default_lang: str,
    *,
    id: int | None,
    din: str | None,
    brandname: str | None,
    status: str | None,
    lang: str | None,
) -> Dict[str, Any]:
    """Validate and build query params for `drugproduct`.

    Requires at least one of: id, din, brandname, status.
    """

    if not any([id, din, brandname, status]):
        raise DPDInvalidParam("Provide at least one of id, din, brandname, or status")
    params = base_params(default_lang, lang)
    if id is not None:
        params["id"] = id
    if din is not None:
        params["din"] = din
    if brandname is not None:
        params["brandname"] = brandname
    if status is not None:
        params["status"] = status
    return params


def params_activeingredient(
    default_lang: str,
    *,
    id: int | None,
    ingredientname: str | None,
    lang: str | None,
) -> Dict[str, Any]:
    """Validate and build query params for `activeingredient`.

    Requires at least one of: id, ingredientname.
    """

    if id is None and ingredientname is None:
        raise DPDInvalidParam("Provide id or ingredientname for activeingredient")
    params = base_params(default_lang, lang)
    if id is not None:
        params["id"] = id
    if ingredientname is not None:
        params["ingredientname"] = ingredientname
    return params

