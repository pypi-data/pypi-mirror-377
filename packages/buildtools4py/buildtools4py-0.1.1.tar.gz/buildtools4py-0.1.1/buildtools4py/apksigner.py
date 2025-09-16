# SPDX-FileCopyrightText: 2025 Michael Pöhn <michael@poehn.at>
# SPDX-License-Identifier: Apache-2.0


"""Wrapper for apksinger from Android build-tools."""


import re
import pathlib
import subprocess
import dataclasses
from typing import Dict, List, Optional, Union

import buildtools4py


@dataclasses.dataclass
class SignerData:
    """Fingerprints of signatures, public keys, etc."""

    public_key_sha256: Optional[str] = None
    certificate_sha256: Optional[str] = None


@dataclasses.dataclass
class ApkSignerData:
    """Verification data of an APK."""

    verifies: Optional[bool] = None
    v1_verified: Optional[bool] = None
    v2_verified: Optional[bool] = None
    v3_verified: Optional[bool] = None
    v31_verified: Optional[bool] = None
    v4_verified: Optional[bool] = None
    source_stamp_verified: Optional[bool] = None
    number_of_signers: Optional[int] = None
    error: Optional[str] = None
    signers: List[SignerData] = dataclasses.field(default_factory=list)


_REGEXCACHE: Dict[str, re.Pattern] = {}


def _re_parse(regex, string):
    r = _REGEXCACHE.get(regex)
    if not r:
        r = re.compile(regex)
        _REGEXCACHE[regex] = r
    m = r.match(string)
    if m:
        return m.group(1)
    return None


def apksigner_verify(
    apk_path: Union[str, pathlib.Path],
    apksigner_path: Optional[Union[str, pathlib.Path]] = None,
    min_sdk: Optional[int] = None,
    max_sdk: Optional[int] = None,
) -> ApkSignerData:
    """Get output from apksigner verify call."""
    apksigner = (
        buildtools4py.lookup_buildtools_bin("apksigner")
        if apksigner_path is None
        else pathlib.Path(apksigner_path)
    )
    if apksigner is None or not apksigner.is_file():
        raise FileNotFoundError(
            "Could not find 'apksigner' please make sure it's installed (e.g. sdkmanager 'build-tools;36.0.0')"
        )
    if not pathlib.Path(apk_path).is_file():
        raise FileNotFoundError(f"Could not find '{apk_path}'.")

    cmd = [str(apksigner), "verify", "--verbose", "--print-certs"]
    if min_sdk is not None:
        cmd += ["--min-sdk-version", str(min_sdk)]
    if max_sdk is not None:
        cmd += ["--max-sdk-version", str(max_sdk)]
    cmd.append(str(apk_path))

    r = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )
    if r.returncode == 0:
        return parse_apksigner_output(r.stdout, stderr=r.stderr)
    else:
        return ApkSignerData(error=r.stderr)


def parse_apksigner_output(
    apksigner_output: str, stderr: Optional[str] = None
) -> ApkSignerData:
    """Parse apksigner verify output into python data class."""
    result = ApkSignerData()
    signer_data = SignerData()

    lines = apksigner_output.split("\n")
    result.verifies = len(lines) > 0 and lines[0] == "Verifies"

    for line in lines:
        verified_v1 = _re_parse(
            r"^Verified using v1 scheme \(JAR signing\): (true|false)$", line
        )
        if verified_v1:
            result.v1_verified = verified_v1 == "true"

        verified_v2 = _re_parse(
            r"^Verified using v2 scheme \(APK Signature Scheme v2\): (true|false)$",
            line,
        )
        if verified_v2:
            result.v2_verified = verified_v2 == "true"

        verified_v3 = _re_parse(
            r"^Verified using v3 scheme \(APK Signature Scheme v3\): (true|false)$",
            line,
        )
        if verified_v3:
            result.v3_verified = verified_v3 == "true"

        verified_v31 = _re_parse(
            r"^Verified using v3.1 scheme \(APK Signature Scheme v3.1\): (true|false)$",
            line,
        )
        if verified_v31:
            result.v31_verified = verified_v31 == "true"

        verified_v4 = _re_parse(
            r"^Verified using v4 scheme \(APK Signature Scheme v4\): (true|false)$",
            line,
        )
        if verified_v4:
            result.v4_verified = verified_v4 == "true"

        source_stamp_verified = _re_parse(
            r"^Verified for SourceStamp: (false|true)$", line
        )
        if source_stamp_verified:
            result.source_stamp_verified = source_stamp_verified == "true"

        number_of_signer = _re_parse(r"^Number of signers: ([0-9]+)$", line)
        if number_of_signer:
            result.number_of_signers = int(number_of_signer)

        pubkey_sha256_a = _re_parse(
            r"Signer #[0-9]+ public key SHA-256 digest: ([a-f0-9]{64})", line
        )
        if pubkey_sha256_a:
            if signer_data.public_key_sha256:
                result.signers.append(signer_data)
                signer_data = SignerData()
            signer_data.public_key_sha256 = pubkey_sha256_a

        pubkey_sha256_b = _re_parse(
            r"Signer .minSdkVersion=[0-9]+, maxSdkVersion=[0-9]+. public key SHA-256 digest: ([a-f0-9]{64})",
            line,
        )
        if pubkey_sha256_b:
            if signer_data.public_key_sha256:
                result.signers.append(signer_data)
                signer_data = SignerData()
            signer_data.public_key_sha256 = pubkey_sha256_b

    if signer_data.public_key_sha256:
        result.signers.append(signer_data)

    if stderr:
        result.error = stderr

    return result
