import os
import logging
from pathlib import Path
from typing import List, Literal, Optional
from hestia_earth.schema.pydantic import ImpactAssessment

from hestia_earth.converters.base.portable_tools import secure_filename

from ..log import logger
from . import hestia_to_simapro_converter_from_recalculated_impact_assessment
from ..pydantic_models import SimaProFile


def save_sima_pro_to_file(file: SimaProFile, full_path: Path = None, skip_existing: bool = False):
    data = file.model_dump(exclude_unset=True, exclude_none=False, mode="json")

    os.makedirs(str(full_path.parent), exist_ok=True)

    logger.info(f"Saving to: {full_path}")

    if full_path.exists():
        if skip_existing:
            raise Exception("File exists {}, skipping.".format(full_path))
        else:
            logger.info("Overwriting existing file at %s", full_path)

    full_path.unlink(missing_ok=True)

    with open(full_path, "wb") as f:
        for line in data:
            f.write(str.encode(line, encoding="windows-1252").replace(b"\\n", b""))
            f.write(str.encode("\n", encoding="windows-1252"))


def convert(
    impact_assessments: List[ImpactAssessment],
    output_folder: str,
    mapping_files_directory: Optional[str] = None,
    skip_existing: bool = False,
    verbose: bool = False,
    debug_file: bool = False,
    filter_by_name: list[str] = [],
    simapro_output_process_type: Literal['System', 'Unit process'] = 'System',
    **kwargs
):
    """
    Program that converts a HESTIA results zip file to a SimaPro csv.

    Outputs a SimaPro CSV file version: 9.0.0

    """
    # import_product_system = True  # todo do we want a '--include_all_references' flag that will expand all "Ref" fields?
    # import_process_refs = True  # todo do we want a '--include_all_references' flag that will expand all "Ref" fields?

    if verbose:
        logger.setLevel(logging.DEBUG)

    if debug_file:
        fh = logging.FileHandler(Path(Path.cwd()) / f"debug_log_{Path(__file__).stem}.log")
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)

    if mapping_files_directory and not Path(mapping_files_directory).exists():
        raise FileNotFoundError(f"Flow map directory '{mapping_files_directory}' does not exist.")

    results_white_list = list(filter_by_name)
    if results_white_list:
        logger.info("Filtering using: '{}".format("','".join(results_white_list)))

    logger.debug(f"Found {len(impact_assessments)} recalculated ImpactAssessment files.")

    for i, target_impactassessment in enumerate(impact_assessments):

        if results_white_list and target_impactassessment.name not in results_white_list:
            continue

        logger.info(f"Processing result {i + 1} of {len(impact_assessments)}: "
                    f"[{target_impactassessment.id}] aka '{target_impactassessment.name}'")

        try:
            sima_pro_obj = hestia_to_simapro_converter_from_recalculated_impact_assessment(
                target_impactassessment,
                Path(mapping_files_directory),
                process_type=simapro_output_process_type)

            filename = secure_filename(sima_pro_obj.header.project) + ".csv"
            save_sima_pro_to_file(
                file=sima_pro_obj,
                full_path=Path(os.path.join(output_folder, filename)),
                skip_existing=skip_existing
            )
        except Exception as e:
            logger.error(e)
            raise e

    logger.info("Complete")
