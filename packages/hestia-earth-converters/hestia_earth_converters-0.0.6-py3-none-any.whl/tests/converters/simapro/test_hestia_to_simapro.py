import os
import logging
import json
import pytest
from pathlib import Path
from tests.utils import fixtures_path, flowmaps_folder, format_csv_output
from hestia_earth.schema.pydantic import ImpactAssessment

from hestia_earth.converters.base.pydantic_models.hestia.hestia_file_tools import (
    sort_schema_dict,
    clean_impact_data
)
from hestia_earth.converters.base.pydantic_models.hestia.hestia_schema_tools import recursively_expand_all_refs
from hestia_earth.converters.simapro.hestia_to_simapro import (
    hestia_to_simapro_converter_from_recalculated_impact_assessment
)
from hestia_earth.converters.simapro.log import logger

logger.setLevel(logging.ERROR)

fixtures_folder = os.path.join(fixtures_path, 'converters', 'simapro')
_aggregated_folder = os.path.join(fixtures_folder, 'hestia', 'aggregated')
_aggregated_folders = [d for d in os.listdir(_aggregated_folder) if os.path.isdir(os.path.join(_aggregated_folder, d))]


def _write_result(filepath: str, data: list):
    with open(filepath, encoding='windows-1252', mode='w') as f:
        f.write(format_csv_output(data))


def _convert(data: dict, process_type = 'System'):
    impact_assessment = ImpactAssessment.model_validate(clean_impact_data(data, include_aggregated_sources=False))
    new_simapro_pydantic_obj = hestia_to_simapro_converter_from_recalculated_impact_assessment(
        impact_assessment,
        mapping_files_directory=flowmaps_folder,
        process_type=process_type,
    )
    return new_simapro_pydantic_obj.model_dump(exclude_unset=False, exclude_none=False, mode="json")


def _run_test(test_name: str, data_folder: str, process_type = 'System'):
    with open(os.path.join(data_folder, 'impact.jsonld')) as f:
        data = json.load(f)

    expected_filename = f"expected_{process_type.lower().replace(' ', '_')}.csv"
    expected_path = os.path.join(data_folder, expected_filename)
    with open(expected_path, encoding='windows-1252') as f:
        expected = f.read()

    output = _convert(data, process_type=process_type)
    _write_result(expected_path, output)
    assert expected.strip() == format_csv_output(output), test_name


@pytest.mark.parametrize(
    'folder',
    _aggregated_folders
)
def test_aggregated_system(folder: str):
    data_folder = os.path.join(_aggregated_folder, folder)
    _run_test(folder, data_folder, process_type='System')


@pytest.mark.parametrize(
    'folder',
    _aggregated_folders
)
def test_aggregated_unit_process(folder: str):
    data_folder = os.path.join(_aggregated_folder, folder)
    _run_test(folder, data_folder, process_type='Unit process')


@pytest.mark.parametrize(
    'folder',
    [
        'bananaFruit-brazil'
    ]
)
def test_non_aggregated(folder: str):
    data_folder = os.path.join(fixtures_folder, 'hestia', folder)
    _run_test(folder, data_folder, process_type='System')
