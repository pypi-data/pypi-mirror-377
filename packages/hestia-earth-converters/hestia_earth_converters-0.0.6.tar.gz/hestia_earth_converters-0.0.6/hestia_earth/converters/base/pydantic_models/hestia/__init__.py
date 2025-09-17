from typing import Union
from hestia_earth.schema.pydantic import Indicator, Term, Emission, Input, Product
from pydantic import Field

HestiaCycleContent = Union[
    Indicator,
    Emission,
    Input,
    Product
]


def generate_default_landOccupationInputsProduction():
    return Term(**{
        '@id': 'landOccupationInputsProduction',
        'termType': 'resourceUse',
        'units': 'm2*year'
    })


def generate_default_landTransformation20YearAverageInputsProduction():
    return Term(**{
        "@id": "landTransformation20YearAverageInputsProduction",
        "name": "Land transformation, 20 year average, inputs production",
        "termType": "resourceUse",
        "units": "m2 / year"
    })


class LandOccupationIndicator(Indicator):
    term: "Term" = Field(default_factory=generate_default_landOccupationInputsProduction)

    class Config:
        use_enum_values = True
        revalidate_instances = "subclass-instances"


class LandTransformationIndicator(Indicator):
    term: "Term" = Field(default_factory=generate_default_landTransformation20YearAverageInputsProduction)

    class Config:
        use_enum_values = True
        revalidate_instances = "subclass-instances"
