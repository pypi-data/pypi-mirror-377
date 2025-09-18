import json
import pathlib

import pandas
import pydantic

from ..config import get_summary_directory


@pydantic.validate_call
def generate_dandiset_totals(
    summary_directory: str | pathlib.Path | None = None,
) -> None:
    """
    Generate top-level totals of summarized access activity for all Dandisets.

    Parameters
    ----------
    summary_directory : pathlib.Path
        Path to the folder containing all previously generated summaries of the S3 access logs.
    """
    summary_directory = pathlib.Path(summary_directory) if summary_directory is not None else get_summary_directory()

    # TODO: record progress over

    all_dandiset_totals = dict()
    for dandiset_id_folder_path in summary_directory.iterdir():
        if not dandiset_id_folder_path.is_dir():
            continue

        dandiset_id = dandiset_id_folder_path.name
        if dandiset_id == "archive":
            continue

        summary_file_path = summary_directory / dandiset_id / "by_region.tsv"
        summary = pandas.read_table(filepath_or_buffer=summary_file_path)

        unique_countries = dict()
        for region in summary["region"]:
            if region in ["VPN", "GitHub", "unknown"]:
                continue

            region_split = region.split("/")
            country_code = region_split[0]
            region_code = "-".join(region_split[1:])
            if "AWS" in country_code:
                country_code = region_code.split("-")[0].upper()

            unique_countries[country_code] = True

        number_of_unique_regions = len(summary["region"])
        number_of_unique_countries = len(unique_countries)
        all_dandiset_totals[dandiset_id] = {
            "total_bytes_sent": int(summary["bytes_sent"].sum()),
            "number_of_unique_regions": number_of_unique_regions,
            "number_of_unique_countries": number_of_unique_countries,
        }

    top_level_summary_file_path = summary_directory / "totals.json"
    with top_level_summary_file_path.open(mode="w") as io:
        json.dump(obj=all_dandiset_totals, fp=io)
