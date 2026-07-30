"""Provider factory and registry for Utilități Moldova."""

from typing import Any

from ..const import (
    PROVIDER_AUTO_SALUBRITATE,
    PROVIDER_CHISINAU_GAZ,
    PROVIDER_INFO_SARP,
    PROVIDER_PREMIER_ENERGY,
)
from .auto_salubritate import AutoSalubritateProvider
from .base import BaseUtilityProvider
from .chisinau_gaz import ChisinauGazProvider
from .info_sarp import InfoSarpProvider
from .premier_energy import PremierEnergyProvider

PROVIDER_CLASSES: dict[str, type[BaseUtilityProvider]] = {
    PROVIDER_PREMIER_ENERGY: PremierEnergyProvider,
    PROVIDER_CHISINAU_GAZ: ChisinauGazProvider,
    PROVIDER_INFO_SARP: InfoSarpProvider,
    PROVIDER_AUTO_SALUBRITATE: AutoSalubritateProvider,
}


def get_provider_instance(
    provider_id: str,
    contract_number: str,
    place_of_consumption: str | None = None,
    username: str | None = None,
    password: str | None = None,
    extra_config: dict[str, Any] | None = None,
) -> BaseUtilityProvider:
    """Instantiate and return the appropriate provider connector.

    Raises ValueError if provider_id is unknown.
    """
    provider_cls = PROVIDER_CLASSES.get(provider_id)
    if not provider_cls:
        raise ValueError(f"Unknown utility provider: {provider_id}")

    return provider_cls(
        contract_number=contract_number,
        place_of_consumption=place_of_consumption,
        username=username,
        password=password,
        extra_config=extra_config,
    )
