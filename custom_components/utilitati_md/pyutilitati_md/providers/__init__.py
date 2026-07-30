"""Provider factory registry for pyutilitati_md."""

from __future__ import annotations

from typing import Any

from aiohttp import ClientSession

from .auto_salubritate import AutoSalubritateProvider
from .base import BaseUtilityProvider
from .chisinau_gaz import ChisinauGazProvider
from .energocom import EnergocomProvider
from .infosarp import InfoSarpProvider
from .premier_energy import PremierEnergyProvider

PROVIDER_CLASSES: dict[str, type[BaseUtilityProvider]] = {
    "premier_energy": PremierEnergyProvider,
    "chisinau_gaz": ChisinauGazProvider,
    "infosarp": InfoSarpProvider,
    "energocom": EnergocomProvider,
    "auto_salubritate": AutoSalubritateProvider,
}


def get_provider_instance(
    provider_id: str,
    contract_number: str,
    place_of_consumption: str | None = None,
    username: str | None = None,
    password: str | None = None,
    session: ClientSession | None = None,
    extra_config: dict[str, Any] | None = None,
) -> BaseUtilityProvider:
    """Instantiate and return the appropriate provider connector."""
    provider_cls = PROVIDER_CLASSES.get(provider_id)
    if not provider_cls:
        raise ValueError(f"Unknown utility provider: {provider_id}")

    return provider_cls(
        contract_number=contract_number,
        place_of_consumption=place_of_consumption,
        username=username,
        password=password,
        session=session,
        extra_config=extra_config,
    )
