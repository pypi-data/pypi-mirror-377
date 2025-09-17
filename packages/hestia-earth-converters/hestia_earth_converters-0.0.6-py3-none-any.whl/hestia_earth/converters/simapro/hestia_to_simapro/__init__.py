from collections import defaultdict
from decimal import Decimal
from itertools import groupby
from pathlib import Path
from functools import cache
from typing import List, Union, Literal, Set, Tuple, Dict
from hestia_earth.schema.pydantic import (
    NodeRef, Source, Cycle, ImpactAssessment, Indicator, Product, Emission, Input, Term, Optional
)
from hestia_earth.utils.tools import safe_parse_date
from hestia_earth.utils.blank_node import get_lookup_value

from hestia_earth.converters.base.pydantic_models.hestia.api_utils import download_hestia, update_hestia_node
from hestia_earth.converters.base.pydantic_models.hestia import (
    LandOccupationIndicator,
    LandTransformationIndicator,
    HestiaCycleContent
)
from hestia_earth.converters.base.pydantic_models.hestia.hestia_schema_tools import (
    proxy_terms_with_inputs_field,
    recursively_expand_all_refs
)
from hestia_earth.converters.base.pydantic_models.hestia.hestia_file_tools import clean_impact_data
from hestia_earth.converters.base.converter import Converter
from hestia_earth.converters.base.converter.utils import safe_string
from hestia_earth.converters.base.RosettaFlow import (
    FlowMap, MapperError, pick_best_match
)

from .. import tmp_node_cache
from ..log import logger
from ..rosetta_flow.helpers import (
    prefer_relevant_simapro_candidate,
    prefer_relevant_simapro_candidate_block_alias
)
from ..pydantic_models import (
    SimaProFile, ElementaryExchangeRow, ProductOutputRow, SimaProHeader, UnitBlock, SimaProBlock,
    GenericBiosphere, ElementaryFlowRow,
    QuantityBlock,
    SimaProProcessBlock, UncertaintyRecordUndefined, UnitRow, QuantityRow,
    TechExchangeRow, SystemDescriptionBlock,
    SystemDescriptionRow, ExternalDocumentsRow, LiteratureRow,
    LiteratureReferenceBlock, EcoinventTechExchangeRow
)
from ..pydantic_models.schema_enums import unit_categories
from ..pydantic_models.util import minify_semapro_compartment
from ..ecoinvent_api import get_external_ecoinvent_process_data
from .helpers import _product_is_waste, parse_ecoinvent_ref_id, is_electricity_heat_input
from .string_generators import (
    generate_tech_exchange_comment,
    _build_hestia_product_description,
    _build_elementary_flow_description,
    generate_elementary_exchange_comment, generate_dummy_process_comment,
    generate_product_comment,
    generate_project_name, generate_process_comment, _map_to_category, minify_unit_slug
)

UnitTuple = Tuple[str, Union[float, int], str]

cached_get_external_ecoinvent_process_data = cache(get_external_ecoinvent_process_data)

TARGET_SEMA_PRO_NOMENCLATURES = [
    "SimaPro/Professional 10.2",
    "Professional 10.2",
    "SimaPro EF 3.1.2",
    "SimaPro/SimaPro EF 3.1.1",
    "SimaPro ecoinvent 3.11 EN15804",
    "SimaPro ecoinvent 3.10 EN15804",
    "SimaPro EF 3.1",
    "Professional 9.6",
    "Professional 9.5",
    "Professional 9.4",
    "SimaPro9.4",
    "Professional 10.2+Hestia",
]

global SPLIT_OUT_LINKED_IMPACT_ASSESSMENTS
global SPLIT_ALL_BACKGROUND_EMISSION_INPUTS

HESTIA_ECOINVENT_MODELS = ['ecoinventV3AndEmberClimate',
                           'ecoinventV3',
                           'ecoinventV2']
SIMAPRO_LIBRARY_ECOINVENT = {
    # 'Ecoinvent 3 - allocation at point of substitution - system',
    'Ecoinvent 3 - allocation, cut-off by classification - unit',
    # 'Ecoinvent 3 - consequential - system',
    # 'Ecoinvent 3 - consequential - unit',
}

# ecoinvent libraries available in simapro. Can be different than internal names used in SIMAPRO_LIBRARY_ECOINVENT
ACCEPTABLE_SIMAPRO_DATA_LIBRARY_ECOINVENT_SYSTEM_MODELS = [
    "Ecoinvent 3 - allocation, cut-off by classification - unit",  # "ecoinvent (allocation, cut-off by classification)"
    "Agribalyse 3.1",
    "AGRIBALYSE - unit",
    "ecoinvent 3.11 (APOS)"
]

converter_obj = Converter()

hestia_transformation_indicator_ids = ['landTransformation20YearAverageInputsProduction',
                                       'landTransformation20YearAverageDuringCycle']
hestia_occupation_indicator_ids = ['landOccupationInputsProduction', 'landOccupationDuringCycle']
hestia_land_use_indicator_ids = hestia_occupation_indicator_ids + hestia_transformation_indicator_ids

attribute_maps = {
    "emission": {
        "ToAir": "emissionsToAir",  # ElementaryExchangeRow
        # 'pErosionSoilFlux': "emissionsToAir",  # ElementaryExchangeRow
        # 'nErosionSoilFlux': "emissionsToAir",  # ElementaryExchangeRow
        "ToWater": "emissionsToWater",  # ElementaryExchangeRow
        "ToGroundwater": "emissionsToWater",  # ElementaryExchangeRow
        "ToDrainageWater": "emissionsToWater",  # ElementaryExchangeRow
        "ToSoil": "emissionsToSoil",  # ElementaryExchangeRow
    },
    "resourceUse": {
        "landTransformation": "resources",  # ElementaryExchangeRow
        "landOccupation": "resources",  # ElementaryExchangeRow
        "freshwaterWithdrawals": "resources",  # ElementaryExchangeRow
        "resourceUseMineralsAndMetals": "resources",  # ElementaryExchangeRow
    },
    "electricity": {
        "electricity": "electricityAndHeat"  # TechExchangeRow
    }
}
attribute_maps_blocks = {  # ElementaryFlowTypeAlias
    "emission": {
        "ToAir": "Airborne emissions",
        # 'pErosionSoilFlux': "Airborne emissions",
        # 'nErosionSoilFlux': "Airborne emissions",
        "ToWater": "Waterborne emissions",
        "ToGroundwater": "Waterborne emissions",
        "ToDrainageWater": "Waterborne emissions",
        "ToSoil": "Emissions to soil",
    },
    "resourceUse": "Raw materials",
    "electricity": {"electricity": "electricityAndHeat"}
}


class ExtractingProcessError(Exception):
    """Cannot turn a Hestia cycle input and related emission into a separate Simapro process"""


def _country_to_iso_code(country: Term) -> Union[str, None]:
    if not country.iso31662Code:
        country = update_hestia_node(country)
    return country.iso31662Code


def _handle_hestia_indicator_to_simapro_exchange_row(source_model: Indicator, context=None,
                                                     **kwargs) -> Union[
    ElementaryExchangeRow, List[ElementaryExchangeRow]]:
    if context is None:
        context = {}

    hestia_indicator = source_model

    if ((
            hestia_indicator.landCover and hestia_indicator.previousLandCover and hestia_indicator.term.id in hestia_transformation_indicator_ids) or
            isinstance(hestia_indicator, LandTransformationIndicator)):

        from_exchange_row = convert_hestia_indicator_to_simapro_exchange_row(
            context | {
                "target_context": [
                    "Resources/land",
                ],
                "requirement": {"FlowName": "Transformation, from "}},
            hestia_indicator,
            hestia_indicator.previousLandCover)

        to_exchange_row = convert_hestia_indicator_to_simapro_exchange_row(
            context | {
                "target_context": [
                    "Resources/land",
                ],
                "requirement": {"FlowName": "Transformation, to "}},
            hestia_indicator,
            hestia_indicator.landCover)

        if from_exchange_row.amount != to_exchange_row.amount:
            raise Exception("Bad land transformation flowmap")
        return [from_exchange_row, to_exchange_row]

    elif ((hestia_indicator.landCover and hestia_indicator.term.id in hestia_occupation_indicator_ids) or
          isinstance(hestia_indicator, LandOccupationIndicator)):

        exchange_row = convert_hestia_indicator_to_simapro_exchange_row(
            context | {
                "target_context": [
                    "Resources/land",
                ],
                "requirement": {"FlowName": "Occupation, "}},
            hestia_indicator,
            hestia_indicator.landCover)
        return exchange_row

    elif hestia_indicator.key:
        exchange_row = convert_hestia_indicator_to_simapro_exchange_row(context, hestia_indicator, hestia_indicator.key)
        return exchange_row

    elif hestia_indicator.inputs and hestia_indicator.term.id in proxy_terms_with_inputs_field:
        exchange_row = convert_hestia_indicator_to_simapro_exchange_row(context, hestia_indicator,
                                                                        hestia_indicator.inputs[0])
        return exchange_row

    else:
        exchange_row = convert_hestia_indicator_to_simapro_exchange_row(context, hestia_indicator,
                                                                        hestia_indicator.term)
        return exchange_row


def _handle_hestia_emission_to_simapro_exchange_row(source_model: Emission, context=None,
                                                    **kwargs) -> Union[
    ElementaryExchangeRow, List[ElementaryExchangeRow]]:
    if context is None:
        context = {}

    hestia_emission = source_model

    exchange_row = convert_hestia_indicator_to_simapro_exchange_row(context, hestia_emission, hestia_emission.term)
    return exchange_row


def _handle_hestia_product_to_simapro_exchange_row(source_model: Product, context=None,
                                                   **kwargs) -> ElementaryExchangeRow:
    if context is None:
        context = {}

    hestia_product = source_model

    exchange_row = convert_hestia_indicator_to_simapro_exchange_row(context, hestia_product, hestia_product.term)
    return exchange_row


def _hestia_input_to_simapro_external_process(source_model: Input, context=None,
                                              **kwargs) -> List[EcoinventTechExchangeRow]:
    if context is None:
        context = {}

    input_entry = source_model

    tech_exchange_rows = []

    ecoinventMapping_process_name = get_hestia_ecoinvent_model_process_name(input_entry)

    if not ecoinventMapping_process_name:
        raise Exception(f"No ecoinventMapping for {input_entry.term.id}")

    available_processes = ecoinventMapping_process_name.split(";")
    for entry in available_processes:
        hestia_ecoinvent_process_name, percent_contribution_str = entry.rsplit(":", maxsplit=1)
        percent_contribution = Decimal(percent_contribution_str.strip())

        # Check if this process name is mapped to another name in Simapro craft
        possible_ecoinvent_processes = term_map_obj.map_flow(
            {"id": hestia_ecoinvent_process_name},
            check_reverse=True,
            search_indirect_mappings=False,
            source_nomenclatures=["ecoinvent_hestia_process"],
            target_nomenclature=ACCEPTABLE_SIMAPRO_DATA_LIBRARY_ECOINVENT_SYSTEM_MODELS,
        )

        ecoinvent_processes_candidate = pick_best_match(
            possible_ecoinvent_processes,
            prefer_unit=input_entry.term.units,
            preferred_list_names=ACCEPTABLE_SIMAPRO_DATA_LIBRARY_ECOINVENT_SYSTEM_MODELS,
        )
        if not ecoinvent_processes_candidate:
            raise Exception(f"No ecoinventProcesses for HESTIA process {repr(hestia_ecoinvent_process_name)} and "
                            f"input: {repr(input_entry.term.id)}")

        comment = generate_tech_exchange_comment(ecoinvent_processes_candidate, input_entry)
        if percent_contribution != 1:
            comment += f"This entry represents {percent_contribution * 100:.2f}% of HESTIA term {input_entry.term.id}. "
        conversion_factor = ecoinvent_processes_candidate.ConversionFactor
        if ecoinvent_processes_candidate.Memo:
            comment += f"Flowmap info: {repr(ecoinvent_processes_candidate.Memo)}"

        term_ecoinvent_id = parse_ecoinvent_ref_id(input_entry)
        if term_ecoinvent_id:
            comment += f" Ecoinvent product uuid: {repr(term_ecoinvent_id)} "

            try:
                ecoinvent_api_json = cached_get_external_ecoinvent_process_data(
                    input_entry.term.ecoinventReferenceProductId.field_id)
                if ecoinvent_api_json.get('product_information', None) is not None:
                    comment += f"Ecoinvent product information: {repr(ecoinvent_api_json.get('product_information').strip())} "
                if ecoinvent_api_json.get("comment", None) is not None:
                    comment += f"Ecoinvent comment: {repr(ecoinvent_api_json.get('comment').strip())} "
            except Exception as e:
                logger.error(e)

        if context.get('input_method_model', None):
            comment += f" Emissions estimated by HESTIA {repr(context.get('input_method_model'))} model."

        # reference the process with a tech exchange row
        updated_amount = conversion_factor * unpack_list_values(
            input_entry.value) * percent_contribution  # todo check conversion is correct
        tech_exchange_row = EcoinventTechExchangeRow(
            platformId=None,  # Must be None to avoid import issues
            name=ecoinvent_processes_candidate.FlowUUID,  # Uses the ecoinvent process name.
            # Points to the _PRODUCT_ of a dummy unit.
            comment=comment,
            unit=ecoinvent_processes_candidate.Unit,
            amount=updated_amount,
            uncertainty=UncertaintyRecordUndefined(),
            flow_metadata={"conversion_factor": conversion_factor,
                           "original_term": input_entry.term.model_dump(by_alias=True, exclude_none=True),
                           "source_unit": input_entry.term.units,
                           "target_unit": ecoinvent_processes_candidate.Unit,
                           "ecoinventMapping_process_name": ecoinventMapping_process_name,
                           "percent_contribution": percent_contribution,
                           "ListName": ecoinvent_processes_candidate.ListName
                           }
        )

        if source_model.country:
            if not source_model.country.name:
                source_model.country = update_hestia_node(source_model.country)
            tech_exchange_row.flow_metadata.update(
                {
                    "original_term_country": source_model.country.model_dump(by_alias=True, exclude_unset=True),
                    "original_term_country_iso31662Code": _country_to_iso_code(source_model.country),
                }
            )
        tech_exchange_rows.append(tech_exchange_row)

    return tech_exchange_rows


# def _hestia_emission_to_simapro_dummy_process(source_model: Emission, context=None,  # todo remove
#                                               **kwargs) -> List[SimaProProcessBlock]:
#     if context is None:
#         context = {}
#
#     cycle_emission = source_model
#
#     dummy_processes = []
#     for input_term in cycle_emission.inputs:
#
#         common_name = f"{cycle_emission.methodModel.name} | {input_term.termType}/{input_term.id}"
#         product_name = common_name
#         dummy_process_name = f"Dummy: {common_name}"
#
#         if cycle_emission.country:
#             iso_str = _country_to_iso_code(cycle_emission.country)
#             product_name += " {" + iso_str + "}"
#
#         dummy_process = SimaProProcessBlock(
#             category="material",
#             processType="Unit process",
#             name=dummy_process_name,
#             status="",
#             infrastructure=False,
#             date=context.get("sima_pro_process_date"),
#             comment=cycle_emission.methodModelDescription or "No",
#             systemDescription=SystemDescriptionRow(name="HESTIA", comment=""),
#             products=[
#                 ProductOutputRow(
#                     name=product_name,
#                     unit=minify_unit_slug(input_term.units),
#                     amount=1,
#                     allocation=100,
#                     wasteType="Undefined",  # todo
#                     category='Others\\Dummies',
#                     comment='',
#                     # comment=_build_hestia_product_description(hestia_product) + allocation_notes,
#                     # platformId=input_term.id,
#                     row_metadata={"original_term": input_term.model_dump(by_alias=True, exclude_unset=True)}
#                 )
#             ],
#         )
#         inventory_blocks = defaultdict(list)  # todo
#         used_units: Set[UnitTuple] = set()  # todo
#         added = False
#         # if cycle_emission.term.termType in attribute_maps:
#         # for compartment_string, attribute_name in attribute_maps[str(cycle_emission.term.termType)].items():
#         #     if compartment_string in cycle_emission.term.id:
#         # block_name = attribute_maps2[str(cycle_emission.term.termType)][compartment_string]
#
#         attribute_name = _bucket_term_to_process_field(cycle_emission.term)
#         block_name = _bucket_term_to_inventory_block(cycle_emission.term)
#
#         dummy_process, used_units, inventory_blocks = hestia_entry_to_exchange_fields(
#             context, cycle_emission,
#             inventory_blocks,
#             dummy_process,
#             used_units,
#             process_attribute=attribute_name,
#             inventory_blocks_name=block_name)
#
#         dummy_processes.append(dummy_process)
#
#     return dummy_processes
#

def _handle_hestia_input_to_simapro_elementary_exchange_row(
        source_model: Input, context=None, **kwargs) -> Union[ElementaryExchangeRow, List[ElementaryExchangeRow]]:
    if context is None:
        context = {}

    hestia_input = source_model
    context = context | {"target_context": ["Raw materials",
                                            "Resources/land",
                                            "Resources/biotic",
                                            "Resources/in ground",
                                            "Resources/in air",
                                            "Resources/in water",
                                            "Resources/fossil well",
                                            "Substance",
                                            ]}
    exchange_row = convert_hestia_indicator_to_simapro_exchange_row(context, hestia_input, hestia_input.term)
    return exchange_row


def _handle_hestia_input_to_simapro_tech_exchange_row(source_model: Input, context=None, **kwargs) -> TechExchangeRow:
    if context is None:
        context = {}

    hestia_input = source_model

    term_dict = hestia_input.term.model_dump(by_alias=True, exclude_unset=True)

    candidate_mapped_flows = term_map_obj.map_flow(term_dict, check_reverse=True,
                                                   search_indirect_mappings=False,
                                                   source_nomenclatures=["HestiaList"],
                                                   target_nomenclature=TARGET_SEMA_PRO_NOMENCLATURES,
                                                   target_context=["Raw materials", "Raw materials/"])
    if not candidate_mapped_flows:
        raise MapperError("Could not map HESTIA term: '{}'".format(term_dict.get("@id")))

    prefer = prefer_relevant_simapro_candidate_block_alias(hestia_input.term)  # inputs?

    iso_str = None
    if hasattr(hestia_input, "country") and hestia_input.country:
        iso_str = _country_to_iso_code(hestia_input.country)
        requirement = context.get("requirement", {}) | {"Geography": iso_str}
    else:
        requirement = context.get("requirement", {}) | {"Geography": None}

    best_candidate = pick_best_match(candidate_mapped_flows, context={"prefer": prefer}, requirement=requirement,
                                     preferred_list_names=TARGET_SEMA_PRO_NOMENCLATURES)

    comment = generate_tech_exchange_comment(best_candidate, hestia_input)
    new_amount = best_candidate.ConversionFactor * unpack_list_values(hestia_input.value)

    tech_row = TechExchangeRow(platformId=best_candidate.FlowUUID.upper(),
                               name=best_candidate.FlowName,
                               comment=comment,
                               line_no=None,
                               unit=best_candidate.Unit,
                               amount=new_amount,
                               uncertainty=UncertaintyRecordUndefined(),
                               flow_metadata={}
                               )
    tech_row.flow_metadata = {"conversion_factor": best_candidate.ConversionFactor,
                              "original_term": term_dict,
                              "source_unit": hestia_input.term.units,
                              "target_unit": best_candidate.Unit,
                              }

    if source_model.country:
        if not source_model.country.name:
            source_model.country = update_hestia_node(source_model.country)
        tech_row.flow_metadata.update(
            {
                "original_term_country": source_model.country.model_dump(by_alias=True, exclude_unset=True),
                "original_term_country_iso31662Code": _country_to_iso_code(source_model.country),
            }
        )

    return tech_row


def convert_hestia_indicator_to_simapro_exchange_row(context: dict, hestia_indicator: HestiaCycleContent,
                                                     term: Term) -> ElementaryExchangeRow:
    term_dict = term.model_dump(by_alias=True, exclude_unset=True)

    candidate_mapped_flows = term_map_obj.map_flow(term_dict,
                                                   check_reverse=True,
                                                   search_indirect_mappings=False,
                                                   source_nomenclatures=["HestiaList"],
                                                   target_nomenclature=TARGET_SEMA_PRO_NOMENCLATURES,
                                                   target_context=context.get("target_context"))
    if not candidate_mapped_flows:
        raise MapperError("Could not map HESTIA term: '{}'".format(term.id))

    if isinstance(hestia_indicator, Emission):
        prefer = prefer_relevant_simapro_candidate(term)
    elif isinstance(hestia_indicator, Input):
        prefer = prefer_relevant_simapro_candidate_block_alias(term)
    else:
        prefer = []

    if hasattr(hestia_indicator, "country") and hestia_indicator.country:
        iso_str = _country_to_iso_code(hestia_indicator.country)
        requirement = context.get("requirement", {}) | {"Geography": iso_str}
    else:
        requirement = context.get("requirement", {}) | {"Geography": None}

    best_candidate = pick_best_match(candidate_mapped_flows, context={"prefer": prefer}, requirement=requirement,
                                     preferred_list_names=TARGET_SEMA_PRO_NOMENCLATURES)
    if not best_candidate:
        raise MapperError(f"Could not map HESTIA term: '{term_dict.get('@id')}' with requirements {repr(requirement)}")

    new_amount = best_candidate.ConversionFactor * unpack_list_values(hestia_indicator.value)

    comment = generate_elementary_exchange_comment(best_candidate, hestia_indicator, term_dict)

    exchange_row = ElementaryExchangeRow(
        platformId=best_candidate.FlowUUID.upper() if best_candidate.FlowUUID else None,
        subCompartment=minify_semapro_compartment(best_candidate.FlowContext),
        name=best_candidate.FlowName,
        comment=comment,
        unit=best_candidate.Unit,
        amount=new_amount,
        uncertainty=UncertaintyRecordUndefined(),
        flow_metadata={}
    )

    exchange_row.flow_metadata = {"conversion_factor": best_candidate.ConversionFactor,
                                  "original_term": term_dict,
                                  "source_unit": hestia_indicator.term.units,
                                  "target_unit": best_candidate.Unit,
                                  }

    if hasattr(hestia_indicator, "country") and hestia_indicator.country:
        if not hestia_indicator.country.name:
            hestia_indicator.country = update_hestia_node(hestia_indicator.country)
        exchange_row.flow_metadata.update(
            {
                "original_term_country": hestia_indicator.country.model_dump(by_alias=True, exclude_unset=True),
                "original_term_country_iso31662Code": _country_to_iso_code(hestia_indicator.country),
            }
        )

    return exchange_row


def unpack_list_values(schema_value: Union[List, int, float, Decimal]):
    if isinstance(schema_value, list):
        return sum(schema_value)
    else:
        return schema_value


def _source_to_literature_ref_block(source_model: Source, **kwargs) -> LiteratureReferenceBlock:
    description = f"Uploader notes: {source_model.uploadNotes}\n" if source_model.uploadNotes else ""

    if source_model.model_fields_set == {'id', 'type'}:
        source_model = update_hestia_node(source_model)

    if source_model.bibliography:
        for k, v in source_model.bibliography.model_dump(exclude_none=True, by_alias=True, mode='python',
                                                         exclude=['name', 'type', 'authors']).items():
            description += f"{k.capitalize()}: {v}\n"  # todo use  = convert_schema_dict_to_text(k, comment, v)
        if source_model.bibliography.authors:
            authors_str = f"Authors:"
            has_authors = False
            for author in source_model.bibliography.authors:
                if (author.model_fields_set.issubset({"@id", "@type", "name", "added", "addedVersion"}) or
                        isinstance(author, NodeRef)):
                    author = update_hestia_node(author)
                if author.dataPrivate is not True and author.name:
                    authors_str += f" {author.name},"
                    has_authors = True
            if has_authors:
                description += authors_str.rstrip(",") + "\n"

    if source_model.originalLicense:
        description += f"Original license: {source_model.originalLicense}\n"

    return LiteratureReferenceBlock(name=source_model.name,
                                    documentation_link=f"https://www.hestia.earth/source/{source_model.id}",
                                    category="HESTIA sources",
                                    description=description.strip("\n"),
                                    )


# def _build_header_from_ia(source_model, model_data, **kwargs) -> SimaProHeader:
#     header = SimaProHeader()
#     return header
#
#
# def _create_process_block(source_model, model_data, **kwargs) -> SimaProProcessBlock:
#     pass
#
#
# converter_obj.register_model_map(source_model_type=ImpactAssessment,
#                                  destination_model_type=SimaProFile,
#                                  map_field_dict={"header": _build_header_from_ia,
#                                                  "blocks": _create_process_block,
#                                                  # # todo all by alias or by real field name? or both?
#                                                  # # "location": "country",
#                                                  # "header.project": "name",
#                                                  # "header.version": "version",
#                                                  # "header.date": "updatedAt",
#                                                  # "header.time": "updatedAt",
#                                                  # "_get_process_block.resources": _distribute_emissionsResourceUse,
#                                                  # "_get_process_block.emissionsToAir": _distribute_emissionsResourceUse,
#                                                  # "_get_process_block.emissionsToWater": _distribute_emissionsResourceUse,
#                                                  # "_get_process_block.emissionsToSoil": _distribute_emissionsResourceUse,
#                                                  # "_get_process_block.finalWasteFlows": _distribute_emissionsResourceUse,
#                                                  # "_get_process_block.nonMaterialEmissions": _distribute_emissionsResourceUse,
#                                                  # "_get_process_block.socialIssues": _distribute_emissionsResourceUse,
#                                                  # "_get_process_block.economicIssues": _distribute_emissionsResourceUse,
#                                                  # # "_always_run_": _convert_product_and_move_to_exchanges
#                                                  })


converter_obj.register_model_map(source_model_type=Product,
                                 destination_model_type=ElementaryExchangeRow,
                                 map_function=_handle_hestia_product_to_simapro_exchange_row)

converter_obj.register_model_map(source_model_type=Indicator,
                                 destination_model_type=ElementaryExchangeRow,
                                 map_function=_handle_hestia_indicator_to_simapro_exchange_row)

converter_obj.register_model_map(source_model_type=LandOccupationIndicator,
                                 destination_model_type=ElementaryExchangeRow,
                                 map_function=_handle_hestia_indicator_to_simapro_exchange_row)

converter_obj.register_model_map(source_model_type=LandTransformationIndicator,
                                 destination_model_type=ElementaryExchangeRow,
                                 map_function=_handle_hestia_indicator_to_simapro_exchange_row)

converter_obj.register_model_map(source_model_type=Emission,
                                 destination_model_type=ElementaryExchangeRow,
                                 map_function=_handle_hestia_emission_to_simapro_exchange_row)

# converter_obj.register_model_map(source_model_type=Emission,
#                                  destination_model_type=SimaProProcessBlock,
#                                  map_function=_hestia_emission_to_simapro_dummy_process)

converter_obj.register_model_map(source_model_type=Input,
                                 destination_model_type=EcoinventTechExchangeRow,
                                 map_function=_hestia_input_to_simapro_external_process)

converter_obj.register_model_map(source_model_type=Input,
                                 destination_model_type=TechExchangeRow,
                                 map_function=_handle_hestia_input_to_simapro_tech_exchange_row)

converter_obj.register_model_map(source_model_type=Input,
                                 destination_model_type=ElementaryExchangeRow,
                                 map_function=_handle_hestia_input_to_simapro_elementary_exchange_row)

converter_obj.register_model_map(source_model_type=Source,
                                 destination_model_type=LiteratureReferenceBlock,
                                 map_function=_source_to_literature_ref_block)

converter_obj.register_model_map(source_model_type=Source,
                                 destination_model_type=LiteratureRow,
                                 map_field_dict={
                                     "Name": "name",
                                     "comment": lambda source_model, field_name, default,
                                                       model_data: f"https://www.hestia.earth/source/{source_model.id}",
                                 })


def _bucket_term_to_process_field(
        term: Term) -> str:  # todo replace with get_term_standard_compartment > compartment to field_name
    if term.termType in attribute_maps:
        for compartment_string, attribute_name in attribute_maps[str(term.termType)].items():
            if compartment_string in term.id:
                return attribute_name
    raise MapperError(f"Do not know what emission compartment the term {term.id} is emitted to.")


def _bucket_term_to_inventory_block(term: Term) -> str:
    if term.termType in attribute_maps:
        for compartment_string, block_name in attribute_maps_blocks[str(term.termType)].items():
            if compartment_string in term.id:
                return block_name
    raise MapperError(f"Do not know what emission compartment the term {term.id} is emitted to.")


def _group__by_inputs_key(emission: Emission) -> tuple:
    if not emission.inputs:
        return None, emission.methodModel.id
    input_ids = set([x.id for x in emission.inputs])
    return tuple(input_ids), emission.methodModel.id


def hestia_to_simapro_converter_from_recalculated_impact_assessment(impact_assessment: ImpactAssessment,
                                                                    mapping_files_directory: Path = None,
                                                                    process_type: Literal[
                                                                        'System',
                                                                        'Unit process'] = "System",
                                                                    convert_linked_impact_assessment: bool = False,
                                                                    create_dummy_processes: bool = False,
                                                                    ) -> SimaProFile:
    """

    Given a cycle containing one or more cycle.products, the inputs/emissions/products/transformations are expressed per "1ha"

    We create a SimaPro process block that contains the same products as in the form of "ProductOutputRow" and contains the same list of cycle.emissions and cycle.inputs converted and stored in
     `ProcessBlock.emissionsToAir`
     `ProcessBlock.emissionsToWater`
     `ProcessBlock.electricityAndHeat`
     `ProcessBlock.resources`
     etc, with the same amounts.

     Each ProductOutputRow has a ProductOutputRow.allocation as a %. Summing all ProductOutputRow.allocation sums to 100. The SemaPro software will display scaled values of all emissions / resources depending on the product selected.

     We turn the cycle into a system process block.


    """
    global term_map_obj
    global shared_mapping_files_directory
    global SPLIT_OUT_LINKED_IMPACT_ASSESSMENTS
    global SPLIT_ALL_BACKGROUND_EMISSION_INPUTS

    SPLIT_OUT_LINKED_IMPACT_ASSESSMENTS = convert_linked_impact_assessment
    SPLIT_ALL_BACKGROUND_EMISSION_INPUTS = create_dummy_processes

    shared_mapping_files_directory = mapping_files_directory

    term_map_obj = FlowMap(mapping_files_directory / 'FlowMaps')
    context = {"term_map_obj": term_map_obj}

    if not impact_assessment.cycle:
        raise Exception(f"No cycle found in {impact_assessment.id}")

    target_cycle = impact_assessment.cycle
    if target_cycle.transformations:
        logger.warning("Not implemented: cycle.transformations")

    if target_cycle.functionalUnit != "1 ha":
        logger.warning("Only 1 ha functional unit supported")  # todo

    if target_cycle.functionalUnitDetails:
        logger.warning("Not implemented: cycle.functionalUnitDetails")

    if target_cycle.siteArea and target_cycle.siteArea != 1:
        logger.warning("Not implemented: cycle.siteArea !- 1")

    if target_cycle.covarianceMatrixIds or target_cycle.covarianceMatrix:
        logger.warning("Not implemented: covarianceMatrix")

    logger.info(msg=f"Loaded data as HESTIA schema '{type(impact_assessment).__name__}'")

    date_created = (target_cycle.updatedAt or
                    target_cycle.createdAt or
                    impact_assessment.updatedAt or
                    impact_assessment.createdAt)

    sima_pro_header = SimaProHeader(date=date_created, project=generate_project_name(impact_assessment, target_cycle))

    sema_pro_file_obj = SimaProFile(header=sima_pro_header, blocks=[])

    if impact_assessment.allocationMethod != "economic":
        raise Exception("Only economic allocation supported")

    hestia_products = [product for product in target_cycle.products if not _product_is_waste(product)]
    hestia_waste_products = [product for product in target_cycle.products if _product_is_waste(product)]

    total_allocation = sum([x.economicValueShare or 0 for x in hestia_products])
    recalculate_allocation = total_allocation != 100
    recalculate_allocation and logger.warning(
        "Product allocations do not sum to 100%. Estimating new product allocations.")

    product_rows = convert_products(hestia_products, target_cycle, recalculate_allocation=recalculate_allocation)
    finalWasteFlows, waste_to_treatment = convert_waste_products(context, hestia_waste_products, target_cycle)

    process_name = f"{target_cycle.name or impact_assessment.name}, at farm gate"
    if process_type == "System":
        process_name += ", S"
    elif process_type == "Unit process":
        process_name += ", U"

    literatures, new_literature_blocks = convert_cycle_sources(context, impact_assessment, target_cycle)

    verification_comment = "Validator: HESTIA Team\\nE-mail: community@hestia.earth"
    if target_cycle.aggregated and target_cycle.aggregatedDataValidated is not None:
        verification_comment += f"\\nAggregation validated by hestia: {target_cycle.aggregatedDataValidated}"
    context = {"process_date": target_cycle.updatedAt or target_cycle.createdAt}
    sima_pro_process = SimaProProcessBlock(
        category="material",
        processType=process_type,
        name=process_name,
        status="Draft",
        time_period=f"{safe_parse_date(target_cycle.startDate).year}-{safe_parse_date(target_cycle.endDate).year}" if target_cycle.startDate and target_cycle.endDate else None,
        geography=safe_string(target_cycle.site.country.name) if target_cycle.site.country else None,
        infrastructure=False,
        date=target_cycle.updatedAt or target_cycle.createdAt,
        record="Data entry by: HESTIA Team\\nE-mail: community@hestia.earth",
        generator="HESTIA team",
        collectionMethod="Data collected by the HESTIA team from industry reports, databases, and published Life Cycle Assessments.",
        verification=verification_comment,
        comment=generate_process_comment(target_cycle),
        allocationRules="economic",
        allocation_method=None,
        dataTreatment=None,
        systemDescription=SystemDescriptionRow(name="HESTIA", comment=""),
        external_documents=ExternalDocumentsRow(url=f"https://www.hestia.earth/cycle/{target_cycle.id}"),
        wasteTreatment=None,
        # wasteScenario=None,
        literatures=literatures,
        products=product_rows,
        avoidedProducts=[],
        materialsAndFuels=[],  # TechExchangeRow ref upstream processes and their products
        electricityAndHeat=[],
        wasteToTreatment=waste_to_treatment,  # TechExchangeRow
        # separatedWaste=[],
        # remainingWaste=[],
        resources=[],
        emissionsToAir=[],
        emissionsToWater=[],
        emissionsToSoil=[],
        finalWasteFlows=finalWasteFlows,
        nonMaterialEmissions=[],
        socialIssues=[],
        economicIssues=[],
        inputParameters=[],
        calculatedParameters=[],
    )

    inventory_blocks = defaultdict(list)
    inventory_blocks.update({
        "Raw materials": [],
        "Airborne emissions": [],
        "Waterborne emissions": [],
        "Emissions to soil": [],
        "Final waste flows": finalWasteFlows,
        "Non material emissions": [],
    })
    used_units: Set[UnitTuple] = set()
    new_processes = []

    if target_cycle.transformations:
        raise Exception("Cycle transformations not implemented")

    if sima_pro_process.processType == "Unit process":
        recreate_processes_from_background_emissions = True
    else:
        recreate_processes_from_background_emissions = False

    (
        cycle_background_emissions_from_electricity,
        cycle_background_emissions_not_from_electricity,
        cycle_other_emissions,
        electricityAndHeat_inputs,
        resources_inputs,
    ) = collect_emissions_and_inputs(target_cycle)

    if recreate_processes_from_background_emissions:
        # WIP todo cannot recreate unit processes when an emission comes from multiple .inputs
        (
            updated_cycle_emissions,
            updated_cycle_inputs,
            sima_pro_process,
            new_processes,
            used_libraries,
            used_units,
            inventory_blocks
        ) = convert_to_multiple_processes(inventory_blocks,
                                          context,
                                          cycle_background_emissions_not_from_electricity,
                                          resources_inputs,
                                          sima_pro_process,
                                          target_cycle)
        emissions_to_add_to_main_process = cycle_other_emissions + updated_cycle_emissions
        resources_inputs_to_add_to_main_process = [input_entry for input_entry in updated_cycle_inputs
                                                   if not is_electricity_heat_input(input_entry)]
        sema_pro_file_obj.header.libraries.extend(sorted(list(used_libraries)))

    else:
        emissions_to_add_to_main_process = cycle_other_emissions + cycle_background_emissions_not_from_electricity
        resources_inputs_to_add_to_main_process = resources_inputs

    for cycle_emission in emissions_to_add_to_main_process:

        if cycle_emission.sd or cycle_emission.min or cycle_emission.max or cycle_emission.statsDefinition != "cycles":
            logger.warning("Not implemented: Emission SD/Min/Max")

        try:
            if cycle_emission.term.termType in attribute_maps:

                attribute_name = _bucket_term_to_process_field(cycle_emission.term)
                block_name = _bucket_term_to_inventory_block(cycle_emission.term)

                sima_pro_process, used_units, inventory_blocks = hestia_entry_to_exchange_fields(
                    context, cycle_emission,
                    inventory_blocks,
                    sima_pro_process,
                    used_units,
                    process_attribute=attribute_name,
                    inventory_blocks_name=block_name)

            else:
                raise Exception("not implemented")

        except MapperError as e:
            logger.error(e)
        except Exception as e:
            logger.error(e)
            raise e

    # cycle.inputs to ElementaryExchangeRow
    for input_entry in resources_inputs_to_add_to_main_process:
        if input_entry.sd or input_entry.min or input_entry.max:
            logger.warning("Not implemented: Input SD/Min/Max")

        if input_entry.impactAssessment or input_entry.impactAssessmentIsProxy:
            logger.warning("Background emissions via impactAssessment not implemented")

        if input_entry.operation:
            logger.warning("Not implemented: Input operation")

        try:
            sima_pro_process, used_units, inventory_blocks = hestia_entry_to_exchange_fields(
                context, input_entry,
                inventory_blocks,
                sima_pro_process,
                used_units,
                process_attribute="resources",
                inventory_blocks_name="Raw materials")

        except MapperError as e:
            logger.error(e)
        except Exception as e:
            logger.error(e)
            raise e

    # impact_assessment.emissionsResourceUse to ElementaryExchangeRow (rescaled)
    for product in target_cycle.products:
        if _product_is_waste(product):
            continue
        for target_impact_assessment in [impact_assessment]:
            if product.term.id in target_impact_assessment.product.term.id:
                for indicator_entry in target_impact_assessment.emissionsResourceUse:
                    if indicator_entry.term.id in hestia_land_use_indicator_ids:
                        if indicator_entry.value != 0:
                            # rescale as impact assessments have functional unit 1.
                            indicator_entry.value = [indicator_entry.value * unpack_list_values(product.value)]

                            try:
                                sima_pro_process, used_units, inventory_blocks = hestia_entry_to_exchange_fields(
                                    context, indicator_entry,
                                    inventory_blocks,
                                    sima_pro_process,
                                    used_units,
                                    process_attribute="resources",
                                    inventory_blocks_name="Raw materials")

                            except MapperError as e:
                                logger.error(e)
                            except Exception as e:
                                logger.error(e)
                                raise e

    for input_entry in electricityAndHeat_inputs:  # TechExchangeRow
        if input_entry.sd or input_entry.min or input_entry.max:
            raise Exception("Not implemented: Input SD/Min/Max")
        try:
            input_entry.term = update_hestia_node(input_entry.term)

            tech_exchange_row = converter_obj.transmute(source_model_obj=input_entry,
                                                        destination_model=EcoinventTechExchangeRow, context=context)
            if isinstance(tech_exchange_row, list):
                tech_exchange_rows = tech_exchange_row
            else:
                tech_exchange_rows = [tech_exchange_row]

            for tech_exchange_row in tech_exchange_rows:
                sima_pro_process.electricityAndHeat.append(tech_exchange_row)

                if tech_exchange_row.flow_metadata and "target_unit" in tech_exchange_row.flow_metadata:
                    used_units.add(add_default_unit(tech_exchange_row))

        except MapperError as e:
            logger.error(e)
        except Exception as e:
            logger.error(e)
            raise e

    sema_pro_file_obj.blocks.append(sima_pro_process)
    sema_pro_file_obj.blocks.extend(new_processes)

    units_block = UnitBlock(rows=[])
    for used_unit in sorted(list(used_units)):
        units_block.rows.append(UnitRow(name=used_unit[0],
                                        conversion_factor=used_unit[1],
                                        dimension=unit_categories.get(used_unit[2], "Unknown"),
                                        reference_unit=used_unit[2],
                                        )
                                )

    quantities_block = QuantityBlock(rows=[])

    quantities_cats = set()
    for used_unit in units_block.rows:
        quantities_cats.add(used_unit.dimension)

    for used_category in sorted(list(quantities_cats)):
        quantities_block.rows.append(QuantityRow(name=used_category, comment=True))
    sema_pro_file_obj.blocks.append(quantities_block)
    sema_pro_file_obj.blocks.append(units_block)

    for block_label, inventory_rows in inventory_blocks.items():
        new_block = GenericBiosphere(block_header=block_label, rows=[])

        seen = set()
        for row in inventory_rows:
            cas_field, comment_field = _build_elementary_flow_description(row)

            if (row.name, row.unit, cas_field) in seen:
                continue

            new_block.rows.append(ElementaryFlowRow(name=row.name,
                                                    unit=row.unit,
                                                    cas=cas_field,
                                                    comment=comment_field,
                                                    platformId=row.platformId)
                                  )
            seen.add((row.name, row.unit, cas_field))
        sema_pro_file_obj.blocks.append(new_block)

    sema_pro_file_obj.blocks.append(SystemDescriptionBlock(name="HESTIA",
                                                           category="Others",
                                                           description="HESTIA Platform",
                                                           allocation_rules="economic",
                                                           ))
    sema_pro_file_obj.blocks.extend(new_literature_blocks)

    return sema_pro_file_obj


def collect_emissions_and_inputs(target_cycle: Cycle) -> Tuple[list, list, list, list, list]:
    electricityAndHeat_inputs = [
        input_entry
        for input_entry in target_cycle.inputs
        if is_electricity_heat_input(input_entry)
    ]  # TechExchangeRow
    resources_inputs = [
        input_entry
        for input_entry in target_cycle.inputs
        if not is_electricity_heat_input(input_entry)
    ]  # ElementaryExchangeRow
    electricity_inputs_term_ids = {
        input_entry.term.id for input_entry in electricityAndHeat_inputs
    }
    filtered_emissions = [
        em for em in target_cycle.emissions if unpack_list_values(em.value) != 0
    ]
    cycle_background_emissions = [
        em for em in filtered_emissions if em.methodTier == "background"
    ]
    cycle_other_emissions = [
        em for em in filtered_emissions if em.methodTier != "background"
    ]
    cycle_background_emissions_from_electricity = [
        em
        for em in cycle_background_emissions
        if electricity_inputs_term_ids.intersection({i.id for i in em.inputs})
    ]
    cycle_background_emissions_not_from_electricity = [
        em
        for em in cycle_background_emissions
        if not electricity_inputs_term_ids.intersection({i.id for i in em.inputs})
    ]

    return (
        cycle_background_emissions_from_electricity,
        cycle_background_emissions_not_from_electricity,
        cycle_other_emissions,
        electricityAndHeat_inputs,
        resources_inputs,
    )


def get_hestia_ecoinvent_model_process_name(input_entry: Input) -> Optional[str]:
    try:
        term_dict = input_entry.term.model_dump(by_alias=True, exclude_none=True)
        ecoinventMapping_process_name = get_lookup_value({'term': term_dict}, 'ecoinventMapping')
        return ecoinventMapping_process_name
    except Exception:
        return None


def create_dummy_process(
        inventory_blocks: defaultdict[list],
        used_units: Set[UnitTuple],
        full_input: Input,
        grouped_emissions: List[Emission],
        context: dict = None) -> Tuple[
    Dict[str, list], Set[UnitTuple], List[SimaProProcessBlock], List[TechExchangeRow], List[Emission], Set[UnitTuple],
    Dict[str, list]]:
    if not context:
        context = {}

    new_processes: List[SimaProProcessBlock] = []
    new_tech_exchange_rows: List[TechExchangeRow] = []
    emissions_to_remove: List[Emission] = []

    added = False

    hestia_model_input = ""
    if full_input.model:  # todo merge with generate_tech_exchange_comment
        if isinstance(full_input.model, NodeRef):
            full_input.model = update_hestia_node(full_input.model)
        hestia_model_input = f" - Input estimated by model: {repr(full_input.model.name)}"

    hestia_model_emissions = "Emissions modeled by model:"
    hestia_model_emissions += " ".join({repr(em.methodModel.name) for em in grouped_emissions if em.methodModel})
    dummy_process_name = f"HESTIA Dummy Unit Process - {repr(full_input.term.name)} - {hestia_model_emissions}{hestia_model_input}"

    if full_input.aggregated:
        dummy_process_name += "- Aggregated from multiple cycles. "

    if full_input.country:
        dummy_process_name += f"- {_country_to_iso_code(full_input.country)}"

    dummy_product_name = f"HESTIA {repr(full_input.term.name)} - {full_input.term.termType}"
    if full_input.country:
        dummy_product_name += f"- {_country_to_iso_code(full_input.country)}"

    dummy_product_name = dummy_process_name.strip() + " S"

    process_block_comment = generate_dummy_process_comment(full_input)

    product_comment = generate_product_comment(full_input)

    new_process_block = SimaProProcessBlock(
        category="material",
        processType="System",
        name=dummy_process_name.strip(),
        status="Temporary",
        infrastructure=False,
        date=context.get("process_date"),
        comment=process_block_comment,
        systemDescription=SystemDescriptionRow(name="HESTIA", comment=""),
        products=[ProductOutputRow(
            name=dummy_product_name,
            unit=minify_unit_slug(full_input.term.units),
            amount=unpack_list_values(full_input.value),
            allocation=100,
            wasteType="Undefined",  # todo
            category=f'Others\\HESTIA Dummies\\{full_input.term.termType}',
            comment=product_comment,
            # comment=_build_hestia_product_description(hestia_product) + allocation_notes,
            platformId=None,
            row_metadata={"original_term": full_input.term.model_dump(by_alias=True, exclude_unset=True)}
        )]
    )

    for emission in grouped_emissions:
        if len(emission.inputs) != 1:
            raise ExtractingProcessError(f"Cannot separate emissions with more than one contributing "
                                         f"inputs: {repr(emission.inputs)}")
        if emission.term.termType not in attribute_maps:
            raise Exception("not implemented")

        attribute_name = _bucket_term_to_process_field(emission.term)
        block_name = _bucket_term_to_inventory_block(emission.term)
        new_process_block, used_units, inventory_blocks = hestia_entry_to_exchange_fields(
            context, emission,
            inventory_blocks,
            new_process_block,
            used_units,
            process_attribute=attribute_name,
            inventory_blocks_name=block_name)
        emissions_to_remove.append(emission)

    new_processes.append(new_process_block)

    new_exchange = TechExchangeRow(line_no=None,
                                   name=dummy_product_name,  # must point to the product name not the process name
                                   unit=minify_unit_slug(full_input.term.units),
                                   amount=unpack_list_values(full_input.value),
                                   uncertainty=UncertaintyRecordUndefined(),
                                   comment=generate_tech_exchange_comment(None, hestia_input=full_input),
                                   platformId=None,
                                   flow_metadata={
                                       "original_term": full_input.term.model_dump(by_alias=True, exclude_unset=True),
                                   })
    new_tech_exchange_rows.append(new_exchange)
    used_units.add((minify_unit_slug(full_input.term.units), 1, minify_unit_slug(full_input.term.units)))
    return new_processes, new_tech_exchange_rows, emissions_to_remove, used_units, inventory_blocks


def combine_emissions(emissions: List[Emission]) -> List[Emission]:
    result = []
    grouped_emissions = defaultdict(list)
    for k, v in groupby(emissions, key=lambda em: em.term.id):
        grouped_emissions[k].extend(list(v))

    for k, v in grouped_emissions.items():
        new_term = v[0].term
        new_val = sum([unpack_list_values(em.value) for em in v])
        new_em = Emission(term=new_term, value=[new_val], methodTier="background",
                          methodModel=Term(**{"@id": "aggregatedModels", "@type": "Term", "termType": "model"}))

        result.append(new_em)
    return result


def convert_to_multiple_processes(
        inventory_blocks: defaultdict[list],
        context: dict,
        cycle_background_emissions_not_from_electricity: List[Emission],
        resources_inputs: List[Input],
        sima_pro_process: SimaProProcessBlock,
        target_cycle: Cycle
) -> Tuple[List[Emission], List[Input], SimaProProcessBlock, List[SimaProProcessBlock], Set[str], Set[UnitTuple], Dict[
    str, list]]:
    new_processes_blocks = []
    used_libraries = set()
    used_units: Set[UnitTuple] = set()
    updated_cycle_background_emissions = cycle_background_emissions_not_from_electricity.copy()
    updated_cycle_inputs = resources_inputs.copy()

    if not cycle_background_emissions_not_from_electricity:
        return (cycle_background_emissions_not_from_electricity,
                resources_inputs,
                sima_pro_process,
                new_processes_blocks,
                used_libraries,
                used_units,
                inventory_blocks)

    background_emissions_group_by_inputs = defaultdict(list)
    for k, v in groupby(cycle_background_emissions_not_from_electricity, key=_group__by_inputs_key):
        background_emissions_group_by_inputs[k].extend(list(v))

    for input_key, grouped_cycle_emission in background_emissions_group_by_inputs.items():
        # Each background emission should have one or more .inputs that match cycle.inputs.
        tech_exchange_row = None
        is_ecoinvent_process = False
        create_new_process = False
        added_tech_exchange = False
        input_term_ids, input_method_model = input_key
        for input_term_id in input_term_ids:
            try:
                full_input = next(
                    (input_e for input_e in resources_inputs if input_e.term.id == input_term_id), None
                )
                if not full_input:
                    raise ExtractingProcessError(f"Cannot find referenced input for emission group {input_key}")

                full_input.term = update_hestia_node(full_input.term)

                if (
                        input_method_model in HESTIA_ECOINVENT_MODELS and
                        get_hestia_ecoinvent_model_process_name(full_input)
                ):
                    # Then we must remove the Input/Emissions and replace with link to equivalent library process
                    # create_new_process = False
                    # link_to_internal_library = True
                    # is_ecoinvent_process = True
                    if len(input_term_ids) != 1:
                        raise ExtractingProcessError(f"Cannot separate emissions with more than one contributing "
                                                     f"input_term_ids: {input_term_ids}")

                    if any([len(emission.inputs) != 1 for emission in grouped_cycle_emission]):
                        raise ExtractingProcessError("Cannot separate emissions with more than one contributing input")

                    try:
                        tech_exchange_rows = converter_obj.transmute(
                            source_model_obj=full_input,
                            destination_model=EcoinventTechExchangeRow,
                            context={'input_method_model': input_method_model}
                        )
                        sima_pro_process.materialsAndFuels.extend(tech_exchange_rows)
                        for tech_exchange_row in tech_exchange_rows:
                            if tech_exchange_row.flow_metadata.get('ListName', False):
                                used_libraries.update({tech_exchange_row.flow_metadata.get('ListName')})

                        updated_cycle_inputs, updated_cycle_background_emissions = remove_input_and_emissions(
                            full_input, grouped_cycle_emission,
                            updated_cycle_background_emissions, updated_cycle_inputs)
                    except Exception as e:
                        raise ExtractingProcessError(e)

                elif full_input.term.openLCAId:
                    raise ExtractingProcessError("Not implemented openLCAId")

                elif full_input.impactAssessment and SPLIT_OUT_LINKED_IMPACT_ASSESSMENTS:
                    # Then we can add an entire new process to the file and link processes together
                    # create_new_process = True
                    # is_ecoinvent_process = False
                    # link_to_internal_library = False
                    if len(input_term_ids) != 1:
                        raise ExtractingProcessError(f"Cannot separate emissions with more than one contributing "
                                                     f"input_term_ids: {input_term_ids}")

                    if any([len(emission.inputs) != 1 for emission in grouped_cycle_emission]):
                        raise ExtractingProcessError("Cannot separate emissions with more than one contributing input")
                    try:
                        (  # todo check for cached unit process avoid adding twice
                            new_sima_pro_processes,
                            new_tech_exchanges,
                            emissions_to_remove,
                            other_blocks
                        ) = convert_input_impact_assessment(full_input)
                        new_processes_blocks.extend(new_sima_pro_processes)
                        for new_p in new_sima_pro_processes:
                            logger.debug(f"Adding new process block '{new_p.name}' with {len(new_p.products)} "
                                         f"products: {[repr(p.name) for p in new_p.products]}")

                        sima_pro_process.materialsAndFuels.extend(new_tech_exchanges)

                        # Remove emissions referenced in impact assessment process
                        processed_del_emissions = []
                        combined_emissions_to_remove = combine_emissions(emissions_to_remove)
                        for del_emission in combined_emissions_to_remove:
                            for em in grouped_cycle_emission:
                                if em.term.id == del_emission.term.id:
                                    ia_em = unpack_list_values(del_emission.value) * unpack_list_values(
                                        full_input.value)
                                    em_from_cycle = unpack_list_values(em.value)
                                    if round(em_from_cycle, 3) != round(ia_em, 3):
                                        # sanity check
                                        logger.warning(
                                            f"Sanity check fail:"
                                            f" Removing Emission {em.term.id} from main process in favor of Input "
                                            f"'{full_input.term.id}' with linked impact assessment "
                                            f"'{full_input.impactAssessment.id}' converted to new unit processes "
                                            f"{[repr(pr.name) for pr in new_sima_pro_processes]}: "
                                            f"Emission values differ: cycle emission='{unpack_list_values(em.value)}' "
                                            f"impact assessment emission='{ia_em}")

                                    updated_cycle_background_emissions.remove(em)
                                    grouped_cycle_emission.remove(em)
                                    processed_del_emissions.append(del_emission)
                                    break

                        if len(processed_del_emissions) != len(combined_emissions_to_remove):
                            logger.warning(f"Not all emissions referenced in linked impact assessment "
                                           f"'{full_input.impactAssessment.id}' could found. "
                                           f"Expected {len(combined_emissions_to_remove)} Emissions for input "
                                           f"'{full_input.term.id}', but found only {len(processed_del_emissions)}. ")

                        if grouped_cycle_emission:
                            logger.warning(f"There are {len(grouped_cycle_emission)} emissions related to input "
                                           f"'{input_term_ids}' in this cycle not mentioned in the linked  input "
                                           f"impactAssessment '{full_input.impactAssessment.id}'. "
                                           f"Removing anyway!")
                            for em in grouped_cycle_emission:
                                updated_cycle_background_emissions.remove(em)

                        updated_cycle_inputs.remove(full_input)
                    except Exception as e:
                        print(e)
                        raise e

                else:
                    # Then we can still create a simple stand alone "dummy process" or leave it in the main block
                    if SPLIT_ALL_BACKGROUND_EMISSION_INPUTS:
                        if len(input_key[0]) != 1:  # Todo can turn this into a combined dummy process?
                            raise ExtractingProcessError(f"Cannot separate emissions with more than one contributing "
                                                         f"input: {input_key}")

                        if any([len(emission.inputs) != 1 for emission in grouped_cycle_emission]):
                            raise ExtractingProcessError(
                                "Cannot separate emissions with more than one contributing input")

                        if any([emission.methodTier != "background" for emission in grouped_cycle_emission]):
                            raise ExtractingProcessError("All emissions in dummy process must be background emissions.")

                        try:
                            (
                                new_sima_pro_processes,
                                new_tech_exchanges,
                                emissions_to_remove,
                                used_units,
                                inventory_blocks
                            ) = create_dummy_process(inventory_blocks,
                                                     used_units,
                                                     full_input,
                                                     grouped_cycle_emission,
                                                     context=context,
                                                     )

                            new_processes_blocks.extend(new_sima_pro_processes)
                            sima_pro_process.materialsAndFuels.extend(new_tech_exchanges)

                            updated_cycle_inputs, updated_cycle_background_emissions = remove_input_and_emissions(
                                full_input, emissions_to_remove,
                                updated_cycle_background_emissions, updated_cycle_inputs)

                        except Exception as e:
                            print(e)
                            raise e

                    else:
                        # We leave this Input and it's emissions in the main process
                        create_new_process = False
                        is_ecoinvent_process = False
                        link_to_internal_library = False
                        used_libraries = set()


            except MapperError as e:
                logger.error(e)
            except ExtractingProcessError as e:
                logger.error(e)
                added_tech_exchange = False
                break
            except Exception as e:
                logger.error(e)
                raise e

    return (updated_cycle_background_emissions,
            updated_cycle_inputs,
            sima_pro_process,
            new_processes_blocks,
            used_libraries,
            used_units,
            inventory_blocks)


def remove_input_and_emissions(full_input, grouped_cycle_emission, updated_cycle_background_emissions,
                               updated_cycle_inputs):
    if full_input in updated_cycle_inputs:
        updated_cycle_inputs.remove(full_input)
    else:
        raise Exception(f"Input {full_input.term.id} cannot be removed from updated_cycle_inputs.")

    for emission in grouped_cycle_emission:
        if emission in updated_cycle_background_emissions:
            updated_cycle_background_emissions.remove(emission)
        else:
            raise Exception("emission missmatch")
    return updated_cycle_inputs, updated_cycle_background_emissions


def convert_cycle_sources(context: dict, impact_assessment: ImpactAssessment, target_cycle: Cycle) -> Tuple[list, list]:
    new_literature_blocks = []
    literatures = []
    target_sources = []
    if target_cycle.defaultSource:
        target_sources.append(target_cycle.defaultSource)
        if target_cycle.defaultSource.metaAnalyses:
            target_sources.extend(target_cycle.defaultSource.metaAnalyses)
    if target_cycle.aggregatedSources:
        target_sources.extend(target_cycle.aggregatedSources)
    if impact_assessment.source:
        target_sources.append(impact_assessment.source)
        if impact_assessment.source.metaAnalyses:
            target_sources.extend(impact_assessment.source.metaAnalyses)
    for source in target_sources:
        if isinstance(source, NodeRef):
            logger.warning(f"Missing source {source.id} in cycle {target_cycle.id}")
            continue
        if not any([source.name == x.name for x in new_literature_blocks]):
            literature_row = converter_obj.transmute(source_model_obj=source,
                                                     destination_model=LiteratureRow,
                                                     context=context)
            literatures.append(literature_row)

            literature_ref_block = converter_obj.transmute(source_model_obj=source,
                                                           destination_model=LiteratureReferenceBlock,
                                                           context=context)

            new_literature_blocks.append(literature_ref_block)
    return literatures, new_literature_blocks


def _add_missing_evs(products: List[Product]):
    def add_evs(product: Product):
        term = product.term.model_dump(by_alias=True, exclude_unset=True)
        value = get_lookup_value({'term': term}, 'global_economic_value_share')
        if value:
            product.economicValueShare = Decimal(value)
        return product

    updated_products = [
        add_evs(product.model_copy()) if product.economicValueShare is None else product
        for product in products
    ]
    total_evs = sum([p.economicValueShare for p in updated_products if p.economicValueShare is not None])
    return updated_products if total_evs <= 100 else products


def convert_products(
    hestia_products: List[Product],
    target_cycle: Cycle,
    recalculate_allocation=False
) -> List[ProductOutputRow]:
    product_rows = []
    allocation_notes = ''

    if recalculate_allocation:
        hestia_products = _add_missing_evs(hestia_products)

        products_with_economic_value_share = [p for p in hestia_products if not p.economicValueShare is None]
        products_missing_economic_value_share = [p for p in hestia_products if p.economicValueShare is None]
        remaining = 100 - sum([p.economicValueShare for p in products_with_economic_value_share])

        if len(hestia_products) == 1 and hestia_products[0].primary:
            hestia_product = hestia_products[0]
            new_allocation = 100
            logger.warning(f"Updating primary product '{hestia_product.term.id}' allocation to {new_allocation}")
            allocation_notes = f"\n Original economicValueShare: {hestia_product.economicValueShare}"
            hestia_product.flow_metadata['allocation_notes'] = allocation_notes
            hestia_product.economicValueShare = Decimal(new_allocation)

        elif len(products_with_economic_value_share) > 0 and len(products_missing_economic_value_share) == 1:
            new_allocation = remaining
            hestia_product = products_missing_economic_value_share[0]
            logger.warning(f"Updating primary product '{hestia_product.term.id}' allocation to {new_allocation}")
            allocation_notes = f"\n Original economicValueShare: {hestia_product.economicValueShare or '0'}"
            hestia_product.flow_metadata['allocation_notes'] = allocation_notes
            hestia_product.economicValueShare = Decimal(new_allocation)

        elif (len(products_with_economic_value_share) > 0 and
              len(products_missing_economic_value_share) > 1 and
              remaining < 5):
            # We consider all products with missing economicValueShare value share contributing less than 5% of
            # the total to be excluded and set to economicValueShare = 0:

            for hestia_product in products_missing_economic_value_share:
                new_allocation = 0
                logger.warning(f"Updating primary product '{hestia_product.term.id}' allocation to {new_allocation}")
                allocation_notes = f"\n Original economicValueShare: {hestia_product.economicValueShare or '0'}"
                hestia_product.flow_metadata['allocation_notes'] = allocation_notes
                hestia_product.economicValueShare = Decimal(new_allocation)

            if remaining > 0:
                for hestia_product in products_with_economic_value_share:
                    new_allocation = hestia_product.economicValueShare + (
                            remaining / len(products_with_economic_value_share)
                    )
                    logger.warning(f"Updating primary product '{hestia_product.term.id}' allocation to "
                                   f"{new_allocation}")
                    allocation_notes = f"\n Original economicValueShare: {hestia_product.economicValueShare or '0'}"
                    hestia_product.flow_metadata['allocation_notes'] = allocation_notes
                    hestia_product.economicValueShare = Decimal(new_allocation)


        else:
            raise Exception(f"Cannot recalculate missing economicValueShare for "
                            f"{len(products_missing_economic_value_share)} products "
                            f"contributing {remaining}% of remaining share.")

    total_evs = 0
    for hestia_product in hestia_products:  # todo replace with transmute()
        if hestia_product.value and unpack_list_values(hestia_product.value) != 0:
            product_platform_id = parse_ecoinvent_ref_id(hestia_product)

            if hestia_product.economicValueShare is None:
                logger.error(f"Skipping product '{hestia_product.term.id}' because 'economicValueShare' is None")
                continue
            total_evs += hestia_product.economicValueShare
            product_rows.append(ProductOutputRow(
                name=hestia_product.term.name + " | " + target_cycle.name + ", at farm gate",
                unit=minify_unit_slug(hestia_product.term.units),
                amount=unpack_list_values(hestia_product.value),
                allocation=hestia_product.economicValueShare,
                wasteType="Undefined",  # todo
                category=_map_to_category(hestia_product),
                comment=_build_hestia_product_description(hestia_product) + hestia_product.flow_metadata.get(
                    'allocation_notes', ''),
                platformId=product_platform_id.upper() if product_platform_id else None,
                row_metadata={'original_term_id': hestia_product.term.id,
                              "original_term_used_conversion_factor": 1},  # todo
            )
            )

    if not product_rows:
        raise Exception("No products can be added")

    if not (99.5 <= total_evs <= 100.5):
        raise Exception("Total sum of economicValueShare must be 100%")

    return product_rows


def convert_waste_products(context: dict,
                           hestia_waste_products: List[Product],
                           target_cycle: Cycle,
                           split_out_waste=True,
                           waste_fallback_to_tech_exchange=False
                           ) -> Tuple[list[ElementaryExchangeRow], list[TechExchangeRow]]:
    # strip out "duplicate" waste entries when the cycle contains overlapping indicators:
    for waste_product in hestia_waste_products:
        waste_term_u = update_hestia_node(waste_product.term)
        waste_product.term = waste_term_u

    new_hestia_waste_products = hestia_waste_products.copy()
    for waste_product in hestia_waste_products:
        if waste_product.term.subClassOf:
            for parent_term in waste_product.term.subClassOf:
                for i, prod in enumerate(new_hestia_waste_products):
                    if parent_term.id == prod.term.id:
                        del new_hestia_waste_products[i]
                        break
    hestia_waste_products = new_hestia_waste_products

    final_waste_flows = []
    waste_to_treatment = []

    if split_out_waste:
        for hestia_product in hestia_waste_products:
            if hestia_product.value and unpack_list_values(hestia_product.value) != 0:

                try:
                    elementary_exchange_row_waste = converter_obj.transmute(source_model_obj=hestia_product,
                                                                            destination_model=ElementaryExchangeRow,
                                                                            context=context)
                    final_waste_flows.append(elementary_exchange_row_waste)
                except Exception as e:
                    logger.error(e)

                    if waste_fallback_to_tech_exchange:
                        waste_to_treatment.append(
                            TechExchangeRow(
                                name=hestia_product.term.name + " | " + target_cycle.name,
                                unit=hestia_product.term.units,
                                amount=unpack_list_values(hestia_product.value),
                                uncertainty=UncertaintyRecordUndefined(),
                                # wasteType="Undefined",  # todo
                                # category=f"material\\{hestia_product.term.termType}",
                                # todo add hestia_product.term.id in freetext?
                                comment=_build_hestia_product_description(hestia_product),
                                platformId=None)  # todo check platformid
                        )
                    else:
                        if not "kg" in hestia_product.term.units:
                            raise Exception("Cannot fallback to mapping waste product to 'Waste, unspecified' "
                                            "due to unit missmatch")
                        final_waste_flows.append(ElementaryExchangeRow(
                            name="Waste, unspecified",
                            subCompartment="Final waste flows",
                            unit="kg",
                            amount=unpack_list_values(hestia_product.value),
                            # uncertainty=UncertaintyRecordUndefined,
                            comment=_build_hestia_product_description(
                                hestia_product) + f" HESTIA term id: {hestia_product.term.id}",
                            platformId="a9e58a44-064a-4870-ab7c-07312074c42c".upper(),
                            # Professional 9.6	"Waste, unspecified"
                            flow_metadata={
                                "original_term": hestia_product.term.model_dump(by_alias=True, exclude_unset=True)}
                        ))
    return final_waste_flows, waste_to_treatment


def hestia_entry_to_exchange_fields(context: dict,
                                    input_entry, inventory_blocks: dict, sima_pro_process, used_units: Set[UnitTuple],
                                    process_attribute: Literal[
                                        'resources',
                                        'emissionsToAir',
                                        'emissionsToSoil',
                                        'emissionsToWater',
                                        'nonMaterialEmissions',
                                        'economicIssues',
                                        'socialIssues',
                                        'finalWasteFlows',
                                    ],
                                    inventory_blocks_name: Literal[
                                        "Raw materials",
                                        "Airborne emissions",
                                        "Waterborne emissions",
                                        "Emissions to soil",
                                        "Final waste flows",
                                        "Non material emissions",
                                    ]) -> Tuple[SimaProProcessBlock, Set[UnitTuple], Dict[str, list]]:
    try:
        elementary_exchange_row = converter_obj.transmute(source_model_obj=input_entry,
                                                          destination_model=ElementaryExchangeRow,
                                                          context=context)
    except MapperError as err:
        raise err
    except Exception as err:
        raise err
    if isinstance(elementary_exchange_row, list):
        elementary_exchange_rows = elementary_exchange_row
    else:
        elementary_exchange_rows = [elementary_exchange_row]

    for elementary_exchange_row in elementary_exchange_rows:
        getattr(sima_pro_process, process_attribute).append(elementary_exchange_row)

        if elementary_exchange_row.flow_metadata and "target_unit" in elementary_exchange_row.flow_metadata:
            used_units.add(add_default_unit(elementary_exchange_row))

        inventory_blocks[inventory_blocks_name].append(elementary_exchange_row)

    return sima_pro_process, used_units, inventory_blocks


def add_default_unit(e_row) -> UnitTuple:
    return e_row.flow_metadata['target_unit'], 1, e_row.flow_metadata['target_unit']


def convert_input_impact_assessment(full_input: Input) -> Tuple[
    List[SimaProProcessBlock], List[TechExchangeRow], List[Emission], List[SimaProBlock]]:
    """
    ! Impact assessments may be proportional to 1 unit of product, but
    `hestia_to_simapro_converter_from_recalculated_impact_assessment()` does not read the impact_Assessment.Emissions
     list, instead it converts the impact_assessment.cycle to a simapro file.
     Therefore the returned emissions_to_remove Emissions are scaled down for one unit of product patching `full_input`
    """
    new_processes: List[SimaProProcessBlock] = []
    new_tech_exchange_rows: List[TechExchangeRow] = []
    emissions_to_remove: List[Emission] = []
    try:  # todo wip
        if not full_input.impactAssessment or full_input.impactAssessmentIsProxy is None:
            raise Exception("No impact assessment associated with input {}".format(input))
        # full_input = load_hestia_model_from_id(full_input.impactAssessment) # todo
        logger.debug(f"Converting Input '{full_input.term.id}' with linked impact assessment "
                     f"'{full_input.impactAssessment.id}' into unit process")

        input_impact_assessment_d = download_hestia(full_input.impactAssessment.id, "ImpactAssessment",
                                                    # or full_input.impactAssessment.download_node_from_api() ?
                                                    data_state='recalculated')
        if not input_impact_assessment_d or "message" in input_impact_assessment_d:
            raise Exception(f"Could not find ImpactAssessment with id: {id}")
        updated_ia = recursively_expand_all_refs(input_impact_assessment_d, Path(tmp_node_cache))
        updated_ia = clean_impact_data(updated_ia)
        input_impact_assessment = ImpactAssessment.model_validate(updated_ia)
        new_simapro_file_pydantic_obj = hestia_to_simapro_converter_from_recalculated_impact_assessment(
            input_impact_assessment,
            mapping_files_directory=shared_mapping_files_directory,
            process_type="System",
        )
        process_blocks = [block for block in new_simapro_file_pydantic_obj.blocks if
                          isinstance(block, SimaProProcessBlock)]
        new_processes.extend(process_blocks)

        for process_block in process_blocks:
            main_product = None
            for product in process_block.products:
                if product.row_metadata.get("original_term_id", "") == full_input.term.id:
                    main_product = product
                    break
            if not main_product:
                raise Exception(f"Could not find main product with id: {id}")
            conversion_factor_of_product = main_product.row_metadata.get("original_term_used_conversion_factor", 1)
            # todo get conversion factor of new process product, if any

            new_tech_exchange_row = TechExchangeRow(
                name=main_product.name,  # todo check should be the product name not process name? With ", S"?
                comment=generate_tech_exchange_comment(None, full_input),
                line_no=None,
                unit=minify_unit_slug(main_product.unit),
                amount=unpack_list_values(full_input.value) * conversion_factor_of_product,
                uncertainty=UncertaintyRecordUndefined(),
                flow_metadata=main_product.row_metadata,
            )
            new_tech_exchange_rows.append(new_tech_exchange_row)

            main_cycle_product = None
            for cycle_product in input_impact_assessment.cycle.products:
                if cycle_product.term.id == full_input.term.id:
                    main_cycle_product = cycle_product
                    break
            if not main_cycle_product:
                raise Exception(f"Could not find main cycle product matching id: {full_input.term.id}")
            amount_of_product = unpack_list_values(main_cycle_product.value)
            for em in input_impact_assessment.cycle.emissions:
                updated_em = em.model_copy(deep=True)
                updated_em.value = [unpack_list_values(updated_em.value) / amount_of_product]
                emissions_to_remove.append(updated_em)

        other_blocks = [block for block in new_simapro_file_pydantic_obj.blocks if
                        not isinstance(block, SimaProProcessBlock)]
    except Exception as err:
        logger.error(err)
        raise ExtractingProcessError(err)

    # todo merge inventories, literature refs, and units.
    return new_processes, new_tech_exchange_rows, emissions_to_remove, other_blocks
