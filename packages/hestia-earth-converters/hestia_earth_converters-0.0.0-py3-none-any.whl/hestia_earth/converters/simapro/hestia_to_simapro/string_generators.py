from collections import defaultdict
from itertools import groupby
from typing import Union, Optional
from hestia_earth.utils.tools import safe_parse_date
from hestia_earth.schema.pydantic import (
    Input, NodeRef, Product, Emission, Indicator, Cycle, ImpactAssessment
)

from hestia_earth.converters.base.RosettaFlow import CandidateFlow, MappingChoices
from hestia_earth.converters.base.pydantic_models.hestia import HestiaCycleContent
from hestia_earth.converters.base.pydantic_models.hestia.api_utils import update_hestia_node, download_hestia

from .helpers import _product_is_waste
from ..pydantic_models import ElementaryExchangeRow


def generate_tech_exchange_comment(best_candidate: CandidateFlow = None, hestia_input: Input = None) -> str:
    comment = f"Mapped from HESTIA term '{hestia_input.term.id}'{add_indirect_mapping_comment(best_candidate)} {generate_input_model_comment(hestia_input)}{generate_input_comment(hestia_input)}"
    # todo generate comment iterate with model dump on hestia_input
    return comment


def generate_input_comment(hestia_input: Input) -> str:
    comment = ""
    if hestia_input.description:
        comment += f"Input Description: {repr(hestia_input.description)}"
    return comment


def generate_input_model_comment(hestia_input: Input) -> str:
    hestia_model_input = ""
    if hestia_input and hestia_input.model:  # todo merge with
        if isinstance(hestia_input.model, NodeRef):
            hestia_input.model = hestia_input.model.download_node_from_api()
        hestia_model_input = f" - Input estimated by model: {repr(hestia_input.model.name)}"
        if hestia_input.model.description:
            hestia_model_input += f" Model Description: {repr(hestia_input.model.description)}"
    return hestia_model_input


def add_indirect_mapping_comment(best_candidate: CandidateFlow) -> str:
    if best_candidate and best_candidate.meta_data and best_candidate.meta_data.stepping_stones:
        via_str = " indirectly via " + " > ".join(
            [f"'{x.list_name}'" for x in best_candidate.meta_data.stepping_stones])
    else:
        via_str = ""
    return via_str


def _build_hestia_product_description(hestia_product: Product) -> str:
    product_comment = ""
    hestia_product.term = update_hestia_node(hestia_product.term)
    for k, v in hestia_product.term.model_dump(exclude_none=True, by_alias=True, mode='json',
                                               include={'name', 'id',
                                                        'synonyms',
                                                        'definition', 'description', 'scientificName', 'agrovoc',
                                                        'wikipedia', 'pubchem',
                                                        'subClassOf', 'casNumber', 'gadmFullName', 'iso31662Code',
                                                        }).items():
        product_comment = convert_schema_dict_to_text(k, product_comment, v)

    for k, v in hestia_product.model_dump(
            exclude_none=True, by_alias=True, mode='json',
            include={'description', 'variety', 'startDate', 'endDate', 'dates', 'fate', 'observations',
                     'priceStatsDefinition', 'price', 'priceMax', 'priceMin',
                     'priceSd', 'properties', 'revenueStatsDefinition', 'revenue', 'revenueMax', 'revenueMin',
                     'revenueSd', 'transport'
                     }).items():
        product_comment = convert_schema_dict_to_text(k, product_comment, v)
    return product_comment.strip("\n")


def convert_schema_dict_to_text(k: str, comment_str: str, v: Union[str, dict, list]) -> str:
    comment_str += f"{k.capitalize()}: "
    if isinstance(v, str):
        comment_str += f"'{v}'\n"
    elif isinstance(v, dict) and "@id" in v:
        comment_str += f"'{v.get('@id')}'\n"
    elif isinstance(v, list):
        items = []
        for entry in v[:min(4, len(v))]:
            if isinstance(entry, str) or isinstance(entry, float):
                items.append(repr(entry))
            elif isinstance(entry, dict):
                if entry.get('@type') == "Term":
                    items.append(f"'{entry.get('@id')}'")
                elif entry.get('@type') == "Property":
                    items.append(f"Property: '{entry.get('term', {}).get('@id')}'")
                    if entry.get("value"):
                        items.append(f"with value: '{entry.get('value')}'")
                    if entry.get("share"):
                        items.append(f"with share: '{entry.get('share')}'")
                else:
                    items.append(repr(entry))
            else:
                pass
        comment_str += ", ".join(items) + "\n"
    else:
        comment_str += f"{repr(v)}\n"
    return comment_str


def _build_elementary_flow_description(row: ElementaryExchangeRow) -> tuple[Optional[str], str]:
    include_cas = True
    cas_field = None

    comment_field = ""
    if row.flow_metadata.get('original_term_country') and row.flow_metadata.get('original_term_country_iso31662Code'):
        country_str = row.flow_metadata.get('original_term_country').get("name") or row.flow_metadata.get(
            'original_term_country').get("@id")
        comment_field += f"{repr(row.flow_metadata.get('original_term_country_iso31662Code'))} = {repr(country_str)} "
    if row.comment:
        if "Emission from: " in row.comment:
            stripped_comment = row.comment.split("Emission from: ")[0]
            comment_field += stripped_comment.rstrip(" ") + " "
        else:
            comment_field += row.comment + " "
    if include_cas:
        result = download_hestia(row.flow_metadata.get('original_term', {}).get("@id"))
        cas_entry = result.get('casNumber')
        if cas_entry:
            padded_cas_entry = cas_entry.rjust(11, '0')

            if len(cas_entry) == 12:
                cas_field = None
                comment_field = comment_field + "Cas: " + padded_cas_entry + " "
            else:
                cas_field = padded_cas_entry

        if result.get("canonicalSmiles"):
            comment_field += f"Formula: {result.get('canonicalSmiles')} "
        elif row.flow_metadata.get('original_term', {}).get("units", "").startswith("kg "):
            unit = row.flow_metadata.get('original_term', {}).get("units")
            if (unit.startswith("kg ") and
                    not any([non_formula in unit for non_formula in ["dry matter", "active ingredient"]])):
                formula = unit.removeprefix("kg ")
                comment_field += f"Formula: {formula} "
    return cas_field, comment_field.rstrip()


def generate_elementary_exchange_comment(best_candidate: CandidateFlow,
                                         hestia_indicator: HestiaCycleContent,
                                         term_dict: dict) -> str:
    via_str = add_indirect_mapping_comment(best_candidate)

    if best_candidate.MatchCondition == MappingChoices.A_PROXY_FOR.value:
        match_str = "Proxy mapped"
    elif best_candidate.MatchCondition == MappingChoices.A_SUBSET_OF.value:
        match_str = "Subset mapped"
    elif best_candidate.MatchCondition == MappingChoices.A_SUPERSET_OF.value:
        match_str = "Superset mapped"
    else:
        match_str = "Mapped"

    comment = f"{match_str} from HESTIA term '{term_dict.get('termType')}/{term_dict.get('@id')}\'{via_str}"
    comment += f" conversion factor: {best_candidate.ConversionFactor}" if best_candidate.ConversionFactor != 1 else ""
    if (isinstance(hestia_indicator, Emission) or isinstance(hestia_indicator, Indicator)) and hestia_indicator.inputs:
        comment += f" Emission from: "

        grouped_inputs_termtype = defaultdict(list)
        for k, v in groupby(hestia_indicator.inputs, key=lambda item: item.termType):
            grouped_inputs_termtype[k].extend(list(v))

        for term_type, input_entries in grouped_inputs_termtype.items():
            comment += f"[TermType:'{term_type}']: "
            for input_e in input_entries:
                comment += f"'{input_e.id}',"
        comment = comment.rstrip(',')

    if hasattr(hestia_indicator, "methodTier") and hestia_indicator.methodTier:
        comment += f" Emission tier: {repr(hestia_indicator.methodTier)}"

    if hasattr(hestia_indicator, "methodModel") and hestia_indicator.methodModel and hestia_indicator.methodModel.name:
        comment += f" Modeled by {repr(hestia_indicator.methodModel.name)}"

    if hasattr(hestia_indicator, "methodModelDescription") and hestia_indicator.methodModelDescription:
        comment += f" Model description:{repr(hestia_indicator.methodModelDescription)}"

    if hasattr(hestia_indicator, "description") and hestia_indicator.description:
        comment += f" {type(hestia_indicator).__name__} description '{hestia_indicator.description}'"

    return comment[0:1000]


def generate_dummy_process_comment(full_input: Input) -> str:
    process_block_comment = ""
    for k, v in full_input.model_dump(exclude_none=True, by_alias=True, mode='json',
                                      include={
                                          "description", "sd", "min", "max",
                                          "statsDefinition", "observations", "dates", "startDate", "endDate",
                                          "inputDuration", "methodClassification", "methodClassificationDescription",
                                          "model", "modelDescription", "isAnimalFeed", "fromCycle", "producedInCycle",
                                          "price", "priceSd", "priceMin", "priceMax", "priceStatsDefinition", "cost",
                                          "costSd", "costMin", "costMax", "costStatsDefinition", "lifespan",
                                          "operation", "country", "region", "impactAssessment",
                                          "impactAssessmentIsProxy", "site", "source", "otherSources", "properties",
                                          "transport", "schemaVersion", "added", "addedVersion", "updated",
                                          "updatedVersion",
                                          # "aggregated",
                                          # "aggregatedVersion"
                                      }
                                      ).items():
        process_block_comment = convert_schema_dict_to_text(k, process_block_comment, v)
    return process_block_comment


def generate_product_comment(full_input: Input) -> str:
    product_comment = ""
    for k, v in full_input.term.model_dump(exclude_none=True, by_alias=True, mode='json',
                                           include={'name', 'id',
                                                    'synonyms',
                                                    'definition', 'description', 'scientificName', 'agrovoc',
                                                    'wikipedia', 'pubchem',
                                                    'subClassOf', 'casNumber', 'gadmFullName', 'iso31662Code',
                                                    }
                                           ).items():
        product_comment = convert_schema_dict_to_text(k, product_comment, v)
    return product_comment


def generate_project_name(impact_assessment: ImpactAssessment, target_cycle: Cycle) -> str:
    if target_cycle and target_cycle.name:
        project_name = target_cycle.name
        if target_cycle.aggregated:
            project_name += " (aggregated)"

    else:
        project_name = impact_assessment.name
        if impact_assessment.aggregated:
            project_name += " (aggregated)"
    return project_name


def generate_process_comment(cycle: Cycle) -> str:
    """
    # DescriptionStatus: DraftRecord: Data entry by: HESTIA TeamGenerator: HESTIA team# Timetime description 2027 to 2028# Geographygeo afghanistan desciption# Technologytech description# ProjectSystem: HESTIA# CopyrightNo
    """

    hestia_products = [product for product in cycle.products if not _product_is_waste(product)]

    main_hestia_product = next((product_entry for product_entry in hestia_products if product_entry.primary), None)

    comment = ""
    if main_hestia_product:
        comment += f"\nMain product:\n"
        for k, v in main_hestia_product.term.model_dump(exclude_none=True, by_alias=True, mode='json',
                                                        include={'name', 'iso31662Code', 'gadmFullName'
                                                                 }).items():
            comment = convert_schema_dict_to_text(k, comment, v)

        for k, v in main_hestia_product.model_dump(
                exclude_none=True, by_alias=True, mode='json',
                include={'description', 'variety', 'primary'}).items():
            comment = convert_schema_dict_to_text(k, comment, v)
        comment += "\n"

    if cycle and cycle.site and cycle.site.country:
        # comment += f"\\n# Geography\\n{cycle.site.country.name}\\n"  # todo openlca workaround
        comment += f"\nGeography\n{cycle.site.country.name}\n"

    if cycle.aggregated:
        comment += f"\nAggregated from multiple cycles: Yes"
        comment += f"\nAggregated from {len(cycle.aggregatedCycles)} cycles"

    if cycle.aggregatedQualityScore:
        comment += f"\nAggregated Quality Score: {cycle.aggregatedQualityScore}"

    if cycle.aggregatedQualityScoreMax:
        comment += f"\nMaximum Aggregated Quality Score: {cycle.aggregatedQualityScoreMax}"

    if cycle.startDate and cycle.endDate:
        comment += f"\nTime Period: {safe_parse_date(cycle.startDate).year}-{safe_parse_date(cycle.endDate).year}"

    comment += f"\n"
    for k, v in cycle.model_dump(
            exclude_none=True, by_alias=True, mode='json',
            include={'startDateDefinition',
                     'originalId',
                     'numberOfCycles',
                     'numberOfReplications',
                     'description',
                     'updatedAt',
                     'treatment',
                     }).items():
        comment = convert_schema_dict_to_text(k, comment, v)
    return comment.replace("\n", "\\n")


product_category_map = {  # todo
    "material": "Others",
    "crop": "Agricultural\\Plant production",
    "seed": "Agricultural\\Plant production",
    "animalProduct": "Agricultural\\Animal production",
    "liveAnimal": "Agricultural\\Animal production",
    "liveAquaticSpecies": "Agricultural\\Animal production",
    "processedFood": "Agricultural\\Food",
    "fuel": "Fuels",
    # "":"Agricultural\\Plant production\\Cereals",
    # "":"Agricultural\\Plant production\\Sugar crops",
    # "":"Agricultural\\Plant production\\Vegetables",
}  # , , cropResidue, electricity, feedFoodAdditive, forage, fuel, , , excreta, organicFertiliser, inorganicFertiliser, biochar, otherOrganicChemical, otherInorganicChemical, processingAid, , , soilAmendment, substrate,, waste


def _map_to_category(hestia_product: Product) -> str:
    if hestia_product.term.termType in product_category_map:
        return product_category_map[hestia_product.term.termType]
    return f"Material\{str(hestia_product.term.termType).capitalize()}"


def minify_unit_slug(new_unit: str) -> str:
    if new_unit.startswith("kg "):
        new_unit = "kg"
    unit_slug_map = {
        "number/Cycle": "unit/cycle",

        "kg": "kg"

    }
    new_unit = unit_slug_map.get(new_unit, new_unit)
    new_unit = new_unit[:10]
    return new_unit
