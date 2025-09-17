from typing import Union, Optional
from hestia_earth.schema.pydantic import Product, Emission, Input

from hestia_earth.converters.base.converter.helpers import is_url, is_uuid


def _product_is_waste(product: Product) -> bool:
    if product.term.termType in ['cropResidue', 'waste', 'excreta', 'substrate']:
        # todo confirm with domain expert  # discardedCropTotal , aboveGroundCropResidueTotal
        return True
    else:
        return False


def emission_is_from_ecoinvent(emission: Emission) -> bool:
    if emission.methodModel and emission.methodModel.id in ['ecoinventV3']:
        return True
    return False


def input_is_from_ecoinvent(input_entry: Input) -> bool:
    if input_entry and parse_ecoinvent_ref_id(input_entry) is not None:
        return True
    return False


def parse_ecoinvent_ref_id(hestia_product: Union[Product, Input]) -> Optional[str]:
    platform_id = None
    if hestia_product.term.ecoinventReferenceProductId:
        if is_url(hestia_product.term.ecoinventReferenceProductId.field_id):
            new_id = hestia_product.term.ecoinventReferenceProductId.field_id.removesuffix("/").removeprefix(
                "https://glossary.ecoinvent.org/ids/")
            if is_uuid(new_id):
                platform_id = new_id.upper()
        elif is_uuid(hestia_product.term.ecoinventReferenceProductId.field_id):
            platform_id = hestia_product.term.ecoinventReferenceProductId.field_id.upper()
    return platform_id


def is_electricity_heat_input(input_entry: Input) -> bool:
    return input_entry.term.termType in ['electricity']  # todo are there others?
