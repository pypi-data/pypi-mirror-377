import os
import pathlib
import subprocess
import sys


def _deploy_subprocess(
    *,
    command: str | list[str],
    environment_variables: dict[str, str] | None = None,
    error_message: str | None = None,
    ignore_errors: bool = False,
) -> str | None:
    error_message = error_message or "An error occurred while executing the command."

    result = subprocess.run(
        args=command,
        env=environment_variables,
        shell=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0 and ignore_errors is False:
        message = (
            f"\n\nError code {result.returncode}\n"
            f"{error_message}\n\n"
            f"stdout: {result.stdout}\n\n"
            f"stderr: {result.stderr}\n\n"
        )
        raise RuntimeError(message)
    if result.returncode != 0 and ignore_errors is True:
        return None

    return result.stdout


def _handle_aws_credentials() -> None:
    """Handle AWS credentials by checking environment variables or the AWS credentials file."""
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID", None)
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY", None)
    aws_credentials_file_path = pathlib.Path.home() / ".aws" / "credentials"

    if aws_access_key_id is None or aws_secret_access_key is None and aws_credentials_file_path.exists():
        with aws_credentials_file_path.open(mode="r") as file_stream:
            aws_credentials_content = file_stream.read()
        if (
            aws_credentials_content.count("aws_access_key_id") > 1
            or aws_credentials_content.count("aws_secret_access_key") > 1
        ):
            message = (
                "Missing environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` and multiple AWS "
                "credentials were found in the system credentials file - please set the environment variables "
                "to disambiguate."
            )
            raise ValueError(message)
        aws_access_key_id = next(line.strip() for line in aws_credentials_content.splitlines())
        aws_secret_access_key = next(
            line.strip() for line in aws_credentials_content.splitlines() if "aws_secret_access_key" in line
        )

    if aws_access_key_id is None or aws_secret_access_key is None:
        message = (
            "Missing environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` - "
            "please set your these variables or configure via AWS CLI."
        )
        raise ValueError(message)


def _handle_gawk_base() -> str:
    """Handle the gawk command based on the platform."""
    # GNU AWK is not as readily available on Windows
    if sys.platform == "win32":
        gawk_path = pathlib.Path.home() / "anaconda3" / "Library" / "usr" / "bin" / "gawk.exe"

        if not gawk_path.exists():
            message = "Unable to find `gawk`, which is required for extraction - please raise an issue."
            raise RuntimeError(message)

    gawk_base = "gawk" if sys.platform != "win32" else str(gawk_path.absolute())
    return gawk_base
