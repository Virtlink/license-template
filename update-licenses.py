#!/usr/bin/env python3
"""Regenerate license templates from declared upstream sources."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import sys
import tempfile
import urllib.request

import yaml

USER_AGENT = "virtlink-license-template-updater/1"
TIMEOUT_SECONDS = 30
COPYRIGHT_YEAR = "{{copyright_year}}"
COPYRIGHT_HOLDER = "{{copyright_holder}}"


@dataclass(frozen=True)
class Source:
    url: str


@dataclass(frozen=True)
class Notice:
    source: str
    start: str
    end: str
    replacements: tuple[tuple[str, str], ...] = ()
    prepend_copyright: bool = False
    apache_compact: bool = False

def gnu_notice(source: str, start: str, end: str, replacements: tuple[tuple[str, str], ...]) -> Notice:
    """Build a GNU notice extraction descriptor.

    :param source: Artifact kind used for extraction, such as ``"markdown"``.
    :param start: Unique marker that starts the prescribed notice.
    :param end: Unique marker that ends the prescribed notice.
    :param replacements: Placeholder replacements required inside the notice.
    :returns: Notice descriptor for the registry entry.
    """
    return Notice(source=source, start=start, end=end, replacements=replacements)

@dataclass(frozen=True)
class License:
    display_name: str
    copier_choice: str
    spdx_id: str
    canonical_url: str
    text: Source | None
    markdown: Source | None
    text_renderer: str = "plain"
    markdown_renderer: str = "plain"
    notice: Notice | None = None


def raw_github(owner: str, repo: str, rev: str, path: str) -> str:
    """Return an immutable raw GitHub URL.

    :param owner: GitHub organization or user.
    :param repo: Repository name.
    :param rev: Commit or tag to pin.
    :param path: Repository-relative file path.
    :returns: Direct ``raw.githubusercontent.com`` URL.
    """
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{rev}/{path}"


GNU = "https://www.gnu.org/licenses"
CC_MD_REV = "eaba9eb3f69a4d257ba3159fc3991007a65a18bc"
CHOOSE_REV = "8975b74de1bd8a05b5eb8ee27b937ea00eb95f9d"
MD_LICENSES_REV = "66202b51f3cfa74d8008e395f89d403a7f5a27ed"



LICENSES: tuple[License, ...] = (
    License(
        display_name="GNU General Public License 3.0",
        copier_choice="GNU General Public License (GPL) 3.0",
        spdx_id="GPL-3.0-or-later",
        canonical_url=f"{GNU}/gpl-3.0",
        text=Source(f"{GNU}/gpl-3.0.txt"),
        markdown=Source(f"{GNU}/gpl-3.0.md"),
        notice=gnu_notice(
            "markdown",
            "<one line to give the program's name and a brief idea of what it does.>",
            "along with this program.  If not, see <https://www.gnu.org/licenses/>.",
            (("<year>", COPYRIGHT_YEAR), ("<name of author>", COPYRIGHT_HOLDER)),
        ),
    ),
    License(
        display_name="GNU General Public License 2.0",
        copier_choice="GNU General Public License (GPL) 2.0",
        spdx_id="GPL-2.0-or-later",
        canonical_url=f"{GNU}/gpl-2.0",
        text=Source(f"{GNU}/gpl-2.0.txt"),
        markdown=Source(f"{GNU}/gpl-2.0.md"),
        notice=gnu_notice(
            "markdown",
            "one line to give the program's name and an idea of what it does.",
            "along with this program; if not, see <https://www.gnu.org/licenses/>.",
            (("yyyy", COPYRIGHT_YEAR), ("name of author", COPYRIGHT_HOLDER)),
        ),
    ),
    License(
        display_name="GNU Lesser General Public License 3.0",
        copier_choice="GNU Lesser General Public License (LGPL) 3.0",
        spdx_id="LGPL-3.0-or-later",
        canonical_url=f"{GNU}/lgpl-3.0",
        text=Source(f"{GNU}/lgpl-3.0.txt"),
        markdown=Source(f"{GNU}/lgpl-3.0.md"),
    ),
    License(
        display_name="GNU Lesser General Public License 2.1",
        copier_choice="GNU Lesser General Public License (LGPL) 2.1",
        spdx_id="LGPL-2.1-or-later",
        canonical_url=f"{GNU}/lgpl-2.1",
        text=Source(f"{GNU}/lgpl-2.1.txt"),
        markdown=Source(f"{GNU}/lgpl-2.1.md"),
        notice=gnu_notice(
            "markdown",
            "one line to give the library's name and an idea of what it does.",
            "License along with this library; if not, see <https://www.gnu.org/licenses/>.",
            (("year", COPYRIGHT_YEAR), ("name of author", COPYRIGHT_HOLDER)),
        ),
    ),
    License(
        display_name="GNU Affero General Public License 3.0",
        copier_choice="GNU Affero General Public License (AGPL) 3.0",
        spdx_id="AGPL-3.0-or-later",
        canonical_url=f"{GNU}/agpl-3.0",
        text=Source(f"{GNU}/agpl-3.0.txt"),
        markdown=Source(f"{GNU}/agpl-3.0.md"),
        notice=gnu_notice(
            "markdown",
            "<one line to give the program's name and a brief idea of what it does.>",
            "along with this program.  If not, see <https://www.gnu.org/licenses/>.",
            (("<year>", COPYRIGHT_YEAR), ("<name of author>", COPYRIGHT_HOLDER)),
        ),
    ),
    License(
        display_name="GNU Free Documentation License 1.3",
        copier_choice="GNU Free Documentation License (GFDL) 1.3",
        spdx_id="GFDL-1.3-or-later",
        canonical_url=f"{GNU}/fdl-1.3",
        text=Source(f"{GNU}/fdl-1.3.txt"),
        markdown=Source(f"{GNU}/fdl-1.3.md"),
        notice=gnu_notice(
            "markdown",
            "Copyright (C)  YEAR  YOUR NAME.",
            "Free Documentation License\".",
            (("YEAR", COPYRIGHT_YEAR), ("YOUR NAME", COPYRIGHT_HOLDER)),
        ),
    ),
    License(
        display_name="Creative Commons Attribution 4.0 International",
        copier_choice="Creative Commons Attribution (CC-BY) 4.0 International",
        spdx_id="CC-BY-4.0",
        canonical_url="https://creativecommons.org/licenses/by/4.0/",
        text=Source("https://creativecommons.org/licenses/by/4.0/legalcode.txt"),
        markdown=Source(raw_github("idleberg", "Creative-Commons-Markdown", CC_MD_REV, "4.0/by.markdown"))
    ),
    License(
        display_name="Creative Commons Attribution Share Alike 4.0 International",
        copier_choice="Creative Commons Attribution Share Alike (CC-BY-SA) 4.0 International",
        spdx_id="CC-BY-SA-4.0",
        canonical_url="https://creativecommons.org/licenses/by-sa/4.0/",
        text=Source("https://creativecommons.org/licenses/by-sa/4.0/legalcode.txt"),
        markdown=Source(raw_github("idleberg", "Creative-Commons-Markdown", CC_MD_REV, "4.0/by-sa.markdown"))
    ),
    License(
        display_name="Creative Commons Attribution Non Commercial 4.0 International",
        copier_choice="Creative Commons Attribution Non Commercial (CC-BY-NC) 4.0 International",
        spdx_id="CC-BY-NC-4.0",
        canonical_url="https://creativecommons.org/licenses/by-nc/4.0/",
        text=Source("https://creativecommons.org/licenses/by-nc/4.0/legalcode.txt"),
        markdown=Source(raw_github("idleberg", "Creative-Commons-Markdown", CC_MD_REV, "4.0/by-nc.markdown"))
    ),
    License(
        display_name="Creative Commons Attribution No Derivatives 4.0 International",
        copier_choice="Creative Commons Attribution No Derivatives (CC-BY-ND) 4.0 International",
        spdx_id="CC-BY-ND-4.0",
        canonical_url="https://creativecommons.org/licenses/by-nd/4.0/",
        text=Source("https://creativecommons.org/licenses/by-nd/4.0/legalcode.txt"),
        markdown=Source(raw_github("idleberg", "Creative-Commons-Markdown", CC_MD_REV, "4.0/by-nd.markdown"))
    ),
    License(
        display_name="Creative Commons Attribution Non Commercial Share Alike 4.0 International",
        copier_choice="Creative Commons Attribution Non Commercial (CC-BY-NC-SA) Share Alike 4.0 International",
        spdx_id="CC-BY-NC-SA-4.0",
        canonical_url="https://creativecommons.org/licenses/by-nc-sa/4.0/",
        text=Source("https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.txt"),
        markdown=Source(raw_github("idleberg", "Creative-Commons-Markdown", CC_MD_REV, "4.0/by-nc-sa.markdown"))
    ),
    License(
        display_name="Creative Commons Attribution Non Commercial No Derivatives 4.0 International",
        copier_choice="Creative Commons Attribution Non Commercial No Derivatives (CC-BY-NC-ND) 4.0 International",
        spdx_id="CC-BY-NC-ND-4.0",
        canonical_url="https://creativecommons.org/licenses/by-nc-nd/4.0/",
        text=Source("https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode.txt"),
        markdown=Source(raw_github("idleberg", "Creative-Commons-Markdown", CC_MD_REV, "4.0/by-nc-nd.markdown"))
    ),
    License(
        display_name="Creative Commons Zero v1.0 Universal",
        copier_choice="Creative Commons Zero (CC0) v1.0 Universal",
        spdx_id="CC0-1.0",
        canonical_url="https://creativecommons.org/publicdomain/zero/1.0/",
        text=Source("https://creativecommons.org/publicdomain/zero/1.0/legalcode.txt"),
        markdown=Source(raw_github("idleberg", "Creative-Commons-Markdown", CC_MD_REV, "4.0/zero.markdown"))
    ),
    License(
        display_name="MIT License",
        copier_choice="MIT License",
        spdx_id="MIT",
        canonical_url="https://opensource.org/licenses/MIT",
        text=None,
        markdown=None,
        text_renderer="repo",
        markdown_renderer="mit"
    ),
    License(
        display_name="Apache License 2.0",
        copier_choice="Apache License 2.0",
        spdx_id="Apache-2.0",
        canonical_url="https://www.apache.org/licenses/LICENSE-2.0",
        text=Source("https://www.apache.org/licenses/LICENSE-2.0.txt"),
        markdown=Source(raw_github("IQAndreas", "markdown-licenses", MD_LICENSES_REV, "apache-v2.0.md")),
        notice=Notice(
            "markdown",
            "Copyright [yyyy] [name of copyright owner]",
            "limitations under the License.",
            (("[yyyy]", COPYRIGHT_YEAR), ("[name of copyright owner]", COPYRIGHT_HOLDER)),
            apache_compact=True
        ),
    ),
    License(
        display_name="Eclipse Public License 2.0",
        copier_choice="Eclipse Public License (EPL) 2.0",
        spdx_id="EPL-2.0",
        canonical_url="https://www.eclipse.org/legal/epl-2.0/",
        text=Source("https://www.eclipse.org/org/documents/epl-2.0/EPL-2.0.txt"),
        markdown=None,
        markdown_renderer="text",
        notice=Notice(
            "text",
            "\"This Source Code may also be made available under the following",
            "You may add additional accurate notices of copyright ownership.",
            prepend_copyright=True
        ),
    ),
    License(
        display_name="Mozilla Public License 2.0",
        copier_choice="Mozilla Public License (MPL) 2.0",
        spdx_id="MPL-2.0",
        canonical_url="https://www.mozilla.org/en-US/MPL/2.0/",
        text=Source("https://www.mozilla.org/media/MPL/2.0/index.f75d2927d3c1.txt"),
        markdown=Source(raw_github("IQAndreas", "markdown-licenses", MD_LICENSES_REV, "mpl-v2.0.md")),
        notice=Notice(
            "markdown",
            "This Source Code Form is subject to the terms of the Mozilla Public",
            "file, You can obtain one at http://mozilla.org/MPL/2.0/.",
            prepend_copyright=True,
        ),
    ),
    License(
        display_name="BSD 2-Clause \"Simplified\" License",
        copier_choice="BSD 2-Clause \"Simplified\" License",
        spdx_id="BSD-2-Clause",
        canonical_url="https://opensource.org/license/BSD-2-Clause",
        text=Source(raw_github("github", "choosealicense.com", CHOOSE_REV, "_licenses/bsd-2-clause.txt")),
        markdown=Source(raw_github("IQAndreas", "markdown-licenses", MD_LICENSES_REV, "bsd-2.md")),
        text_renderer="choosealicense",
        markdown_renderer="bsd"
    ),
    License(
        display_name="BSD 3-Clause \"New\" or \"Revised\" License",
        copier_choice="BSD 3-Clause \"New\" or \"Revised\" License",
        spdx_id="BSD-3-Clause",
        canonical_url="https://opensource.org/license/BSD-3-Clause",
        text=Source(raw_github("github", "choosealicense.com", CHOOSE_REV, "_licenses/bsd-3-clause.txt")),
        markdown=Source(raw_github("IQAndreas", "markdown-licenses", MD_LICENSES_REV, "bsd-3.md")),
        text_renderer="choosealicense",
        markdown_renderer="bsd"
    ),
    License(
        display_name="Boost Software License 1.0",
        copier_choice="Boost Software License (BSL) 1.0",
        spdx_id="BSL-1.0",
        canonical_url="https://www.boost.org/LICENSE_1_0.txt",
        text=Source("https://www.boost.org/LICENSE_1_0.txt"),
        markdown=None,
        markdown_renderer="text"
    ),
    License(
        display_name="The Unlicense",
        copier_choice="The Unlicense",
        spdx_id="Unlicense",
        canonical_url="https://unlicense.org/",
        text=Source(raw_github("github", "choosealicense.com", CHOOSE_REV, "_licenses/unlicense.txt")),
        markdown=Source(raw_github("IQAndreas", "markdown-licenses", MD_LICENSES_REV, "unlicense.md")),
        text_renderer="choosealicense"
    ),
)

def normalize(raw: bytes, url: str) -> str:
    """Normalize bytes fetched from a source artifact.

    :param raw: UTF-8 encoded source bytes.
    :param url: Source URL or path used in error messages.
    :returns: Text with UTF-8 decoded, BOM removed, LF newlines, and one final newline.
    :raises ValueError: If ``raw`` is not valid UTF-8.
    """
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"UTF-8 decode failed for {url}: {exc}") from exc
    if text.startswith("\ufeff"):
        text = text[1:]
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.rstrip("\n") + "\n"


def fetch(url: str) -> str:
    """Download and normalize one source URL.

    :param url: URL to download.
    :returns: Normalized response body.
    :raises urllib.error.URLError: If the request fails.
    :raises ValueError: If the response body cannot be normalized.
    """
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return normalize(response.read(), url)


def checked_in_gnu_source(root: Path, url: str) -> str | None:
    """Return a checked-in GNU artifact when the repository owns the local copy.

    :param root: Repository root.
    :param url: GNU source URL requested by the registry.
    :returns: Normalized checked-in artifact text, or ``None`` when no local GNU cache applies.
    """
    for license in LICENSES:
        if license.text is not None and license.text.url == url:
            path = root / f"license.{license.spdx_id}.txt.jinja"
            break
        if license.markdown is not None and license.markdown.url == url:
            path = root / f"license.{license.spdx_id}.md.jinja"
            break
    else:
        return None
    if "://www.gnu.org/" not in url or not path.exists():
        return None
    return normalize(path.read_bytes(), str(path))


def fetch_all(urls: set[str], root: Path) -> dict[str, str]:
    """Fetch all distinct source URLs required for a run.

    :param urls: Source URLs to resolve.
    :param root: Repository root used for checked-in GNU artifacts.
    :returns: Mapping from URL to normalized source text.
    :raises RuntimeError: If a non-local source cannot be fetched.
    """
    fetched: dict[str, str] = {}
    for url in sorted(urls):
        fallback = checked_in_gnu_source(root, url)
        if fallback is not None:
            fetched[url] = fallback
            continue
        try:
            fetched[url] = fetch(url)
        except Exception as exc:
            raise RuntimeError(f"failed to fetch {url}: {exc}") from exc
    return fetched


def strip_front_matter(text: str, license_id: str) -> str:
    """Remove choosealicense.com metadata from a license source.

    :param text: Normalized choosealicense.com file content.
    :param license_id: SPDX identifier used in diagnostics.
    :returns: License body without YAML front matter.
    :raises ValueError: If the front matter is missing or unterminated.
    """
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError(f"{license_id}: choosealicense source has no YAML front matter")
    try:
        second = lines[1:].index("---") + 1
    except ValueError as exc:
        raise ValueError(f"{license_id}: choosealicense source has unterminated YAML front matter") from exc
    body = "\n".join(lines[second + 1 :]).lstrip("\n")
    return body.rstrip("\n") + "\n"


def replace_exact(text: str, replacements: tuple[tuple[str, str], ...], context: str) -> str:
    """Replace each declared placeholder exactly once.

    :param text: Source text containing placeholders.
    :param replacements: Ordered ``(old, new)`` replacements.
    :param context: Diagnostic label for failures.
    :returns: Text after all replacements.
    :raises ValueError: If any placeholder occurs zero or multiple times.
    """
    out = text
    for old, new in replacements:
        count = out.count(old)
        if count != 1:
            raise ValueError(f"{context}: expected one {old!r}, found {count}")
        out = out.replace(old, new)
    return out


def artifact_path(root: Path, license: License, suffix: str) -> Path:
    """Build a generated artifact path.

    :param root: Repository root.
    :param license: Registry entry.
    :param suffix: Artifact suffix including its leading separator.
    :returns: Repository path for the artifact.
    """
    return root / f"license.{license.spdx_id}{suffix}"


def read_authoritative_artifact(root: Path, license: License, suffix: str) -> str:
    """Read a repository-owned artifact.

    :param root: Repository root.
    :param license: Registry entry.
    :param suffix: Artifact suffix including its leading separator.
    :returns: Normalized artifact content.
    :raises ValueError: If the authoritative artifact is missing.
    """
    path = artifact_path(root, license, suffix)
    if not path.exists():
        raise ValueError(f"{license.spdx_id}: authoritative artifact is missing: {path.name}")
    return normalize(path.read_bytes(), str(path))


def render_text(root: Path, license: License, fetched: dict[str, str]) -> str:
    """Render or read the plain-text artifact for a license.

    :param root: Repository root.
    :param license: Registry entry.
    :param fetched: Downloaded source text keyed by URL.
    :returns: Normalized text artifact content.
    :raises ValueError: If the renderer and source configuration are inconsistent.
    """
    if license.text_renderer == "repo":
        if license.text is not None:
            raise ValueError(f"{license.spdx_id}: repo text renderer must not declare a download source")
        return read_authoritative_artifact(root, license, ".txt.jinja")
    if license.text is None:
        raise ValueError(f"{license.spdx_id}: text renderer {license.text_renderer} requires a download source")
    text = fetched[license.text.url]
    if license.text_renderer == "choosealicense":
        text = strip_front_matter(text, license.spdx_id)
        replacements = (("[year]", COPYRIGHT_YEAR), ("[fullname]", COPYRIGHT_HOLDER))
        for old, new in replacements:
            if old in text:
                text = text.replace(old, new)
    elif license.text_renderer != "plain":
        raise ValueError(f"{license.spdx_id}: unknown text renderer {license.text_renderer}")
    return text.rstrip("\n") + "\n"


def render_mit_markdown() -> str:
    """Render the repository-defined MIT Markdown layout.

    :returns: MIT Markdown template content with Jinja copyright fields.
    """
    return "\n".join(
        [
            "# MIT License (MIT)",
            "",
            f"- **Copyright © {COPYRIGHT_YEAR} {COPYRIGHT_HOLDER}**",
            "",
            'Permission is hereby granted, free of charge, to any person obtaining a copy of *this software and associated documentation files* (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:',
            "",
            "The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.",
            "",
            'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL *THE AUTHORS OR COPYRIGHT HOLDERS* BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.',
            "",
        ]
    )


def render_markdown(license: License, fetched: dict[str, str], text_output: str) -> str:
    """Render the Markdown artifact for a license.

    :param license: Registry entry.
    :param fetched: Downloaded source text keyed by URL.
    :param text_output: Plain-text artifact content, used when text is valid Markdown.
    :returns: Normalized Markdown artifact content.
    :raises ValueError: If the Markdown renderer is unknown or lacks a source.
    """
    if license.markdown_renderer == "mit":
        return render_mit_markdown()
    if license.markdown_renderer == "text":
        return text_output
    if license.markdown is None:
        raise ValueError(f"{license.spdx_id}: markdown source missing")
    text = fetched[license.markdown.url]
    if license.markdown_renderer == "bsd":
        if "`<YEAR>`" in text or "`<OWNER>`" in text:
            text = replace_exact(text, (("`<YEAR>`", COPYRIGHT_YEAR), ("`<OWNER>`", COPYRIGHT_HOLDER)), f"{license.spdx_id} markdown")
        else:
            text = replace_exact(text, (("`<year>`", COPYRIGHT_YEAR), ("`<copyright holder>`", COPYRIGHT_HOLDER)), f"{license.spdx_id} markdown")
        if "`<COPYRIGHT HOLDER>`" in text:
            text = replace_exact(text, (("`<COPYRIGHT HOLDER>`", COPYRIGHT_HOLDER),), f"{license.spdx_id} markdown")
        if "`<organization>`" in text:
            text = replace_exact(text, (("`<organization>`", COPYRIGHT_HOLDER),), f"{license.spdx_id} markdown")
    elif license.markdown_renderer != "plain":
        raise ValueError(f"{license.spdx_id}: unknown markdown renderer {license.markdown_renderer}")
    return text.rstrip("\n") + "\n"


def dedent_notice(block: str) -> str:
    """Remove Markdown code-block indentation from an extracted notice.

    :param block: Notice block extracted from source text.
    :returns: Notice text without source code-block indentation and with one final newline.
    """
    lines = block.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    # Source legal notices are code blocks. Drop code-block indentation from
    # extracted lines even when a marker starts inside the first indented line.
    while any(line.startswith("    ") for line in lines):
        lines = [line[4:] if line.startswith("    ") else line for line in lines]
    return "\n".join(lines).rstrip() + "\n"


def extract_notice(text: str, notice: Notice, license_id: str) -> str:
    """Extract and normalize a prescribed notice block.

    :param text: Source artifact text.
    :param notice: Extraction descriptor.
    :param license_id: SPDX identifier used in diagnostics.
    :returns: Notice text with declared placeholders replaced.
    :raises ValueError: If the markers are not unique or replacements fail.
    """
    start_count = text.count(notice.start)
    end_count = text.count(notice.end)
    if start_count != 1 or end_count != 1:
        raise ValueError(f"{license_id}: expected one notice block bounded by {notice.start!r}/{notice.end!r}, found {start_count}/{end_count}")
    start = text.index(notice.start)
    end = text.index(notice.end, start) + len(notice.end)
    block = dedent_notice(text[start:end])
    notice_lines = block.splitlines()
    if notice_lines and "one line to give" in notice_lines[0]:
        block = dedent_notice("\n".join(notice_lines[1:]))
    if notice.apache_compact:
        block = block.replace("http://www.apache.org/licenses/LICENSE-2.0", "https://www.apache.org/licenses/LICENSE-2.0")
        block = block.replace('an "AS IS" BASIS,\nWITHOUT WARRANTIES OR CONDITIONS OF ANY KIND', 'an **"as is" basis, without warranties or conditions of any kind**')
        block = "\n".join(
            [
                block.splitlines()[0],
                "",
                'Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at <https://www.apache.org/licenses/LICENSE-2.0>.',
                "",
                'Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an **"as is" basis, without warranties or conditions of any kind**, either express or implied. See the License for the specific language governing permissions and limitations under the License.',
                "",
            ]
        )
    block = replace_exact(block, notice.replacements, f"{license_id} notice") if notice.replacements else block
    if notice.prepend_copyright:
        block = f"Copyright {COPYRIGHT_YEAR} {COPYRIGHT_HOLDER}\n\n{block}"
    return block.rstrip("\n") + "\n"


def fallback_summary(license: License) -> str:
    """Render the deterministic fallback project summary.

    :param license: Registry entry.
    :returns: Fallback summary pointing at the canonical license URL.
    """
    return f"Copyright {COPYRIGHT_YEAR} {COPYRIGHT_HOLDER}\n\nThis project is licensed under the [{license.display_name}]({license.canonical_url}).\n"


def render_summary(license: License, fetched: dict[str, str], markdown_output: str, text_output: str) -> str:
    """Render the project summary for a license.

    :param license: Registry entry.
    :param fetched: Downloaded source text keyed by URL.
    :param markdown_output: Rendered Markdown artifact content.
    :param text_output: Rendered plain-text artifact content.
    :returns: Summary Markdown content.
    """
    if license.notice is None:
        return fallback_summary(license)
    source_text = markdown_output if license.notice.source == "markdown" else text_output
    summary = extract_notice(source_text, license.notice, license.spdx_id)
    if license.canonical_url not in summary:
        summary = summary.rstrip("\n") + f"\n\nFull license: <{license.canonical_url}>.\n"
    return summary


def validate_output(path: Path, content: str, license: License, artifact: str) -> None:
    """Validate one generated artifact before writing any output.

    :param path: Destination path.
    :param content: Generated artifact content.
    :param license: Registry entry.
    :param artifact: Artifact file name used in diagnostics.
    :raises ValueError: If the output is empty, leaks placeholders, or has bad final newlines.
    """
    if not content:
        raise ValueError(f"{license.spdx_id} {artifact}: generated output is empty")
    placeholders = ("[year]", "[fullname]", "YEAR RIGHTSHOLDER", "`<year>`", "`<copyright holder>`", "`<COPYRIGHT HOLDER>`", "`<organization>`")
    if artifact.endswith("-summary.md.jinja"):
        placeholders = placeholders + ("<year>", "<name of author>", "[yyyy]", "[name of copyright owner]", "YOUR NAME")
    leaked = [placeholder for placeholder in placeholders if placeholder in content]
    if leaked:
        raise ValueError(f"{license.spdx_id} {artifact}: unreplaced upstream placeholder(s): {', '.join(leaked)}")
    if not content.endswith("\n") or content.endswith("\n\n"):
        raise ValueError(f"{license.spdx_id} {artifact}: output must have exactly one final newline")


def configured_license_pairs(root: Path) -> list[tuple[str, str]]:
    """Read configured Copier license choices and SPDX identifiers.

    :param root: Repository root.
    :returns: Ordered ``(license choice, SPDX ID)`` pairs excluding ``None``.
    """
    config = yaml.safe_load((root / "copier.yml").read_text(encoding="utf-8"))
    license_choices = [item for item in config["license"]["choices"] if item != "None"]
    license_ids = [item for item in config["license_id"]["choices"] if item != "None"]
    return list(zip(license_choices, license_ids, strict=True))


def validate_registry(root: Path) -> None:
    """Ensure the registry matches ``copier.yml`` exactly.

    :param root: Repository root.
    :raises ValueError: If configured license choices differ from the registry.
    """
    configured = configured_license_pairs(root)
    registry = [(license.copier_choice, license.spdx_id) for license in LICENSES]
    if configured != registry:
        raise ValueError(f"copier.yml configured licenses differ from updater registry: configured={configured!r} registry={registry!r}")


def build_outputs(root: Path) -> dict[Path, str]:
    """Build the complete generated output map.

    :param root: Repository root.
    :returns: Mapping from destination paths to fully validated artifact content.
    :raises RuntimeError: If any artifact fails to render.
    :raises ValueError: If registry validation or output validation fails.
    """
    validate_registry(root)
    print(f"Fetching {len(LICENSES)} licenses...", flush=True)
    urls = {license.text.url for license in LICENSES if license.text is not None}
    urls.update(license.markdown.url for license in LICENSES if license.markdown is not None)
    fetched = fetch_all(urls, root)
    outputs: dict[Path, str] = {}
    expected_outputs = 0
    for license in LICENSES:
        try:
            text_output = render_text(root, license, fetched)
            markdown_output = render_markdown(license, fetched, text_output)
            summary_output = render_summary(license, fetched, markdown_output, text_output)
        except Exception as exc:
            urls_for_license = ([license.text.url] if license.text is not None else []) + ([license.markdown.url] if license.markdown else [])
            source_description = ", ".join(urls_for_license) if urls_for_license else "authoritative repository artifact"
            raise RuntimeError(f"{license.spdx_id}: failed to render artifacts from {source_description}: {exc}") from exc
        artifacts: dict[Path, str] = {}
        if license.text is not None:
            artifacts[artifact_path(root, license, ".txt.jinja")] = text_output
        artifacts[artifact_path(root, license, ".md.jinja")] = markdown_output
        artifacts[artifact_path(root, license, "-summary.md.jinja")] = summary_output
        for path, content in artifacts.items():
            validate_output(path, content, license, path.name)
        expected_outputs += len(artifacts)
        outputs.update(artifacts)
        print(f"Fetched {license.spdx_id}.", flush=True)
    if len(outputs) != expected_outputs:
        raise ValueError(f"expected {expected_outputs} outputs, built {len(outputs)}")
    return outputs


def atomic_write(path: Path, content: str) -> None:
    """Atomically replace one destination file.

    :param path: Destination path.
    :param content: Final file content.
    :raises OSError: If the temporary write or replacement fails.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def write_outputs(outputs: dict[Path, str]) -> None:
    """Write all generated artifacts in deterministic path order.

    :param outputs: Mapping from destination paths to final content.
    """
    print(f"Writing {len(outputs)} files...", flush=True)
    for path in sorted(outputs):
        atomic_write(path, outputs[path])


def main() -> int:
    """Run the updater for the current working directory.

    :returns: Process exit code, where ``0`` means success.
    """
    root = Path.cwd()
    try:
        outputs = build_outputs(root)
        write_outputs(outputs)
        print("Done.", flush=True)
    except Exception as exc:
        print(f"update-licenses.py: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
