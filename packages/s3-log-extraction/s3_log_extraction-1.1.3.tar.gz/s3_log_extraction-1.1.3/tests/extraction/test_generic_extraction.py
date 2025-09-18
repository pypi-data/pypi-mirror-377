import pathlib

import py

import s3_log_extraction


def test_extraction(tmpdir: py.path.local) -> None:
    tmpdir = pathlib.Path(tmpdir)

    base_directory = pathlib.Path(__file__).parent
    test_logs_directory = base_directory / "test_generic_logs"
    output_directory = tmpdir / "test_extraction"
    output_directory.mkdir(exist_ok=True)
    expected_output_directory = base_directory / "expected_generic_output"

    extractor = s3_log_extraction.extractors.S3LogAccessExtractor(cache_directory=output_directory)
    extractor.extract_directory(directory=test_logs_directory, workers=1)

    relative_output_files = {file.relative_to(output_directory) for file in output_directory.rglob(pattern="*.txt")}
    relative_expected_files = {
        file.relative_to(expected_output_directory) for file in expected_output_directory.rglob(pattern="*.txt")
    }
    assert relative_output_files == relative_expected_files

    s3_log_extraction.testing.assert_expected_extraction_content(
        extractor_name="S3LogAccessExtractor",
        output_directory=output_directory,
        expected_output_directory=expected_output_directory,
        relative_output_files=relative_output_files,
        relative_expected_files=relative_expected_files,
    )


def test_extraction_parallel(tmpdir: py.path.local) -> None:
    tmpdir = pathlib.Path(tmpdir)

    base_directory = pathlib.Path(__file__).parent
    test_logs_directory = base_directory / "test_generic_logs"
    output_directory = tmpdir / "test_extraction"
    output_directory.mkdir(exist_ok=True)
    expected_output_directory = base_directory / "expected_generic_output"

    extractor = s3_log_extraction.extractors.S3LogAccessExtractor(cache_directory=output_directory)
    extractor.extract_directory(directory=test_logs_directory, workers=2)

    relative_output_files = {file.relative_to(output_directory) for file in output_directory.rglob(pattern="*.txt")}
    relative_expected_files = {
        file.relative_to(expected_output_directory) for file in expected_output_directory.rglob(pattern="*.txt")
    }
    assert relative_output_files == relative_expected_files

    s3_log_extraction.testing.assert_expected_extraction_content(
        extractor_name="S3LogAccessExtractor",
        output_directory=output_directory,
        expected_output_directory=expected_output_directory,
        relative_output_files=relative_output_files,
        relative_expected_files=relative_expected_files,
    )


# TODO: CLI
