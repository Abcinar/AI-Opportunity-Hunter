#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Opportunity Intelligence Platform - Project Rename Utility.

Developer Tool #001 of the Opportunity Intelligence Platform (OIP).
Version 1.1

Scans a repository, replaces all project name variants in file contents,
renames matching files and directories, creates timestamped backups,
supports undo, generates rich JSON reports, provides colored console
output with a progress bar, and offers dry-run previews with line-level
context.

Features
--------
* Regex-based replacement engine (longest-first, compiled once)
* Binary-file detection and size-based skipping
* Content, filename and directory renaming
* Dry-run line-level previews (max 10 per file)
* Git command suggestions after successful runs
* Dual configuration support (YAML preferred over JSON)
* Comprehensive safety guards (symlinks, protected paths)

Requirements
------------
Python 3.13+

Usage examples
--------------
    python rename_project.py --scan
    python rename_project.py --replace --backup
    python rename_project.py --undo
    python rename_project.py --report
    python rename_project.py --replace --dry-run
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import shutil
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Sequence, Set, Tuple

# ---------------------------------------------------------------------------
# Optional YAML support
# ---------------------------------------------------------------------------

try:
    import yaml  # type: ignore

    _HAS_YAML = True
except ImportError:  # pragma: no cover
    _HAS_YAML = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VERSION: str = "1.1.0"
DEFAULT_CONFIG_JSON: str = "rename_config.json"
DEFAULT_CONFIG_YAML: str = "rename_config.yaml"
DEFAULT_LOG_DIR: str = "logs"
DEFAULT_LOG_FILE: str = "rename_project.log"
DEFAULT_BACKUP_DIR: str = "backup"
DEFAULT_REPORT_FILE: str = "report.json"
ENCODING: str = "utf-8"
MAX_FILE_SIZE_BYTES: int = 25 * 1024 * 1024  # 25 MB
MAX_PREVIEWS_PER_FILE: int = 10

BINARY_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".ico",
        ".pdf",
        ".sqlite",
        ".db",
        ".exe",
        ".dll",
        ".so",
        ".zip",
        ".7z",
        ".bin",
        ".pyc",
        ".pyo",
        ".pyd",
        ".class",
        ".o",
        ".a",
        ".lib",
        ".wasm",
        ".ttf",
        ".woff",
        ".woff2",
        ".eot",
        ".mp3",
        ".mp4",
        ".avi",
        ".mov",
        ".mkv",
        ".webm",
        ".ogg",
        ".wav",
        ".flac",
        ".tar",
        ".gz",
        ".bz2",
        ".xz",
        ".rar",
    }
)

PROTECTED_DIR_NAMES: frozenset[str] = frozenset(
    {
        ".git",
        ".github",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".idea",
        ".vscode",
        "dist",
        "build",
        "logs",
        "tmp",
        ".cache",
        "backup",
    }
)

# ---------------------------------------------------------------------------
# Color support (ANSI, no external dependencies)
# ---------------------------------------------------------------------------


class Color(Enum):
    """ANSI color codes for console output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"


def colorize(text: str, color: Color, *, enabled: bool = True) -> str:
    """Apply ANSI color to text if enabled and stdout is a TTY.

    Args:
        text: The text to colorize.
        color: The Color enum value.
        enabled: Whether coloring is active.

    Returns:
        Colored or plain text.
    """
    if not enabled or not sys.stdout.isatty():
        return text
    return f"{color.value}{text}{Color.RESET.value}"


# ---------------------------------------------------------------------------
# Progress bar (pure Python)
# ---------------------------------------------------------------------------


class ProgressBar:
    """Simple terminal progress bar without external dependencies."""

    def __init__(
        self,
        total: int,
        *,
        width: int = 40,
        prefix: str = "Progress",
        enabled: bool = True,
    ) -> None:
        """Initialize the progress bar.

        Args:
            total: Total number of steps.
            width: Width of the bar in characters.
            prefix: Text shown before the bar.
            enabled: Whether to display the bar.
        """
        self.total = max(total, 1)
        self.width = width
        self.prefix = prefix
        self.enabled = enabled and sys.stdout.isatty()
        self.current = 0
        self._start = time.perf_counter()

    def update(self, n: int = 1) -> None:
        """Advance the progress bar by n steps.

        Args:
            n: Number of steps to advance.
        """
        self.current = min(self.current + n, self.total)
        if self.enabled:
            self._render()

    def finish(self) -> None:
        """Complete the progress bar and move to the next line."""
        self.current = self.total
        if self.enabled:
            self._render()
            sys.stdout.write("\n")
            sys.stdout.flush()

    def _render(self) -> None:
        """Render the current state of the progress bar."""
        ratio = self.current / self.total
        filled = int(self.width * ratio)
        bar = "█" * filled + "░" * (self.width - filled)
        percent = ratio * 100
        elapsed = time.perf_counter() - self._start
        line = (
            f"\r{self.prefix} |{bar}| "
            f"{self.current}/{self.total} "
            f"({percent:5.1f}%) "
            f"[{elapsed:5.1f}s]"
        )
        sys.stdout.write(line)
        sys.stdout.flush()


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class NameMapping:
    """A single old-name to new-name mapping."""

    old: str
    new: str


@dataclass
class RenameConfig:
    """Configuration loaded from rename_config.yaml / rename_config.json or defaults."""

    root_dir: str = "."
    ignore_dirs: List[str] = field(
        default_factory=lambda: list(PROTECTED_DIR_NAMES)
    )
    supported_extensions: List[str] = field(
        default_factory=lambda: [
            ".py",
            ".md",
            ".txt",
            ".json",
            ".toml",
            ".yaml",
            ".yml",
            ".ini",
            ".cfg",
            ".html",
            ".css",
            ".js",
            ".ts",
            ".xml",
        ]
    )
    mappings: List[NameMapping] = field(default_factory=list)
    backup_dir: str = DEFAULT_BACKUP_DIR
    log_dir: str = DEFAULT_LOG_DIR
    log_file: str = DEFAULT_LOG_FILE
    report_file: str = DEFAULT_REPORT_FILE
    create_backup: bool = True
    dry_run: bool = False
    colored_output: bool = True
    max_file_size_bytes: int = MAX_FILE_SIZE_BYTES

    def __post_init__(self) -> None:
        """Ensure default mappings exist when none are provided."""
        if not self.mappings:
            self.mappings = [
                NameMapping("AI Opportunity Hunter", "Opportunity Intelligence Platform"),
                NameMapping("AI-Opportunity-Hunter", "Opportunity-Intelligence-Platform"),
                NameMapping("AI_Opportunity_Hunter", "Opportunity_Intelligence_Platform"),
                NameMapping("ai_opportunity_hunter", "opportunity_intelligence_platform"),
                NameMapping("AIOpportunityHunter", "OpportunityIntelligencePlatform"),
                NameMapping("AIOPPORTUNITYHUNTER", "OPPORTUNITYINTELLIGENCEPLATFORM"),
            ]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RenameConfig":
        """Create a RenameConfig from a dictionary.

        Args:
            data: Dictionary typically loaded from JSON or YAML.

        Returns:
            A fully populated RenameConfig instance.
        """
        mappings_raw = data.get("mappings", [])
        mappings = [
            NameMapping(old=m["old"], new=m["new"])
            for m in mappings_raw
            if isinstance(m, dict) and "old" in m and "new" in m
        ]
        return cls(
            root_dir=data.get("root_dir", "."),
            ignore_dirs=data.get("ignore_dirs", list(PROTECTED_DIR_NAMES)),
            supported_extensions=data.get(
                "supported_extensions",
                [
                    ".py",
                    ".md",
                    ".txt",
                    ".json",
                    ".toml",
                    ".yaml",
                    ".yml",
                    ".ini",
                    ".cfg",
                    ".html",
                    ".css",
                    ".js",
                    ".ts",
                    ".xml",
                ],
            ),
            mappings=mappings or cls().mappings,
            backup_dir=data.get("backup_dir", DEFAULT_BACKUP_DIR),
            log_dir=data.get("log_dir", DEFAULT_LOG_DIR),
            log_file=data.get("log_file", DEFAULT_LOG_FILE),
            report_file=data.get("report_file", DEFAULT_REPORT_FILE),
            create_backup=data.get("create_backup", True),
            dry_run=data.get("dry_run", False),
            colored_output=data.get("colored_output", True),
            max_file_size_bytes=data.get("max_file_size_bytes", MAX_FILE_SIZE_BYTES),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize configuration to a dictionary suitable for JSON/YAML.

        Returns:
            Dictionary representation of the configuration.
        """
        result = asdict(self)
        result["mappings"] = [{"old": m.old, "new": m.new} for m in self.mappings]
        return result


def _load_yaml(path: Path) -> Dict[str, Any]:
    """Load a YAML file into a dictionary.

    Args:
        path: Path to the YAML file.

    Returns:
        Parsed dictionary.

    Raises:
        RuntimeError: If PyYAML is not installed.
        OSError, ValueError: On I/O or parse errors.
    """
    if not _HAS_YAML:
        raise RuntimeError(
            "PyYAML is required to load YAML configuration. "
            "Install it with: pip install pyyaml"
        )
    with path.open("r", encoding=ENCODING) as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping, got {type(data).__name__}")
    return data


def _load_json(path: Path) -> Dict[str, Any]:
    """Load a JSON file into a dictionary.

    Args:
        path: Path to the JSON file.

    Returns:
        Parsed dictionary.
    """
    with path.open("r", encoding=ENCODING) as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object, got {type(data).__name__}")
    return data


def load_config(base_dir: Path) -> RenameConfig:
    """Load configuration preferring YAML over JSON.

    Search order:
        1. rename_config.yaml (if PyYAML available)
        2. rename_config.json
        3. Built-in defaults

    Args:
        base_dir: Directory in which to look for config files.

    Returns:
        Loaded or default RenameConfig.
    """
    yaml_path = base_dir / DEFAULT_CONFIG_YAML
    json_path = base_dir / DEFAULT_CONFIG_JSON

    if yaml_path.is_file() and _HAS_YAML:
        try:
            data = _load_yaml(yaml_path)
            return RenameConfig.from_dict(data)
        except (OSError, ValueError, RuntimeError) as exc:
            logging.getLogger(__name__).warning(
                "Failed to load YAML config %s: %s. Trying JSON.", yaml_path, exc
            )

    if json_path.is_file():
        try:
            data = _load_json(json_path)
            return RenameConfig.from_dict(data)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            logging.getLogger(__name__).warning(
                "Failed to load JSON config %s: %s. Using defaults.", json_path, exc
            )

    return RenameConfig()


def save_default_config(base_dir: Path) -> None:
    """Write a default JSON configuration file if neither config exists.

    Args:
        base_dir: Directory in which to write the config.
    """
    yaml_path = base_dir / DEFAULT_CONFIG_YAML
    json_path = base_dir / DEFAULT_CONFIG_JSON
    if yaml_path.exists() or json_path.exists():
        return
    config = RenameConfig()
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with json_path.open("w", encoding=ENCODING) as fh:
        json.dump(config.to_dict(), fh, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


@dataclass
class PreviewEntry:
    """A single dry-run preview of a replacement."""

    line_number: int
    old_text: str
    new_text: str
    context: str


@dataclass
class FileResult:
    """Result of processing a single file."""

    path: str
    replacements: int
    modified: bool
    error: Optional[str] = None
    size_bytes: int = 0
    previews: List[PreviewEntry] = field(default_factory=list)
    skipped_reason: Optional[str] = None


@dataclass
class PathRenameResult:
    """Result of renaming a file or directory."""

    old_path: str
    new_path: str
    is_directory: bool
    success: bool
    error: Optional[str] = None


@dataclass
class RenameReport:
    """Aggregated report of a rename operation."""

    files_scanned: int = 0
    files_modified: int = 0
    total_replacements: int = 0
    errors: List[str] = field(default_factory=list)
    ignored_files: List[str] = field(default_factory=list)
    skipped_binary_files: List[str] = field(default_factory=list)
    skipped_large_files: List[str] = field(default_factory=list)
    skipped_symlinks: List[str] = field(default_factory=list)
    modified_directories: List[str] = field(default_factory=list)
    modified_filenames: List[str] = field(default_factory=list)
    modified_file_contents: List[str] = field(default_factory=list)
    execution_time_seconds: float = 0.0
    dry_run: bool = False
    backup_path: Optional[str] = None
    file_results: List[FileResult] = field(default_factory=list)
    path_renames: List[PathRenameResult] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    version: str = VERSION
    average_replacements_per_file: float = 0.0
    largest_modified_file: Optional[str] = None
    largest_modified_file_size: int = 0

    def finalize_statistics(self) -> None:
        """Compute derived statistics after processing."""
        if self.files_modified > 0:
            self.average_replacements_per_file = (
                self.total_replacements / self.files_modified
            )
        largest_size = 0
        largest_path: Optional[str] = None
        for fr in self.file_results:
            if fr.modified and fr.size_bytes > largest_size:
                largest_size = fr.size_bytes
                largest_path = fr.path
        self.largest_modified_file = largest_path
        self.largest_modified_file_size = largest_size

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to a JSON-serializable dictionary.

        Returns:
            Dictionary representation of the report.
        """
        return {
            "timestamp": self.timestamp,
            "version": self.version,
            "files_scanned": self.files_scanned,
            "files_modified": self.files_modified,
            "total_replacements": self.total_replacements,
            "average_replacements_per_file": round(
                self.average_replacements_per_file, 3
            ),
            "largest_modified_file": self.largest_modified_file,
            "largest_modified_file_size_bytes": self.largest_modified_file_size,
            "errors": self.errors,
            "ignored_files_count": len(self.ignored_files),
            "ignored_files": self.ignored_files[:200],
            "skipped_binary_files_count": len(self.skipped_binary_files),
            "skipped_binary_files": self.skipped_binary_files[:100],
            "skipped_large_files_count": len(self.skipped_large_files),
            "skipped_large_files": self.skipped_large_files[:50],
            "skipped_symlinks_count": len(self.skipped_symlinks),
            "skipped_symlinks": self.skipped_symlinks[:50],
            "modified_directories": self.modified_directories,
            "modified_filenames": self.modified_filenames,
            "modified_file_contents": self.modified_file_contents,
            "execution_time_seconds": round(self.execution_time_seconds, 3),
            "dry_run": self.dry_run,
            "backup_path": self.backup_path,
            "path_renames": [
                {
                    "old_path": pr.old_path,
                    "new_path": pr.new_path,
                    "is_directory": pr.is_directory,
                    "success": pr.success,
                    "error": pr.error,
                }
                for pr in self.path_renames
            ],
            "file_results": [
                {
                    "path": fr.path,
                    "replacements": fr.replacements,
                    "modified": fr.modified,
                    "error": fr.error,
                    "size_bytes": fr.size_bytes,
                    "skipped_reason": fr.skipped_reason,
                    "previews": [
                        {
                            "line_number": p.line_number,
                            "old_text": p.old_text,
                            "new_text": p.new_text,
                            "context": p.context,
                        }
                        for p in fr.previews
                    ],
                }
                for fr in self.file_results
                if fr.modified or fr.error or fr.skipped_reason
            ],
        }

    def save(self, path: Path) -> None:
        """Write the report as JSON to the given path.

        Args:
            path: Destination file path.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding=ENCODING) as fh:
            json.dump(self.to_dict(), fh, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------


def setup_logging(
    log_dir: str, log_file: str, *, verbose: bool = False
) -> logging.Logger:
    """Configure application logging to file and console.

    Args:
        log_dir: Directory for the log file.
        log_file: Name of the log file.
        verbose: If True, set console level to DEBUG.

    Returns:
        Configured logger for the application.
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    full_log = log_path / log_file

    logger = logging.getLogger("rename_project")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(full_log, encoding=ENCODING)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_handler.setFormatter(
        logging.Formatter("%(levelname)-8s | %(message)s")
    )
    logger.addHandler(console_handler)

    return logger


# ---------------------------------------------------------------------------
# Core services
# ---------------------------------------------------------------------------


class PathFilter:
    """Determines which paths should be processed or ignored."""

    def __init__(
        self,
        ignore_dirs: Sequence[str],
        supported_extensions: Sequence[str],
    ) -> None:
        """Initialize the filter.

        Args:
            ignore_dirs: Directory names to skip entirely.
            supported_extensions: File extensions that may be processed for content.
        """
        self._ignore_dirs: Set[str] = set(ignore_dirs) | set(PROTECTED_DIR_NAMES)
        self._extensions: Set[str] = {
            ext if ext.startswith(".") else f".{ext}" for ext in supported_extensions
        }

    def is_ignored_dir(self, name: str) -> bool:
        """Return True if the directory name should be ignored.

        Args:
            name: Directory name (not full path).

        Returns:
            True when the directory must be skipped.
        """
        return name in self._ignore_dirs

    def is_supported_file(self, path: Path) -> bool:
        """Return True if the file extension is supported for content processing.

        Args:
            path: Path to the file.

        Returns:
            True when the file may have its content processed.
        """
        return path.suffix.lower() in self._extensions

    def is_binary_extension(self, path: Path) -> bool:
        """Return True if the file has a known binary extension.

        Args:
            path: Path to the file.

        Returns:
            True when the file must never be read as text.
        """
        return path.suffix.lower() in BINARY_EXTENSIONS


class RepositoryScanner:
    """Scans a repository tree and yields candidate files and directories."""

    def __init__(self, root: Path, path_filter: PathFilter) -> None:
        """Initialize the scanner.

        Args:
            root: Repository root directory.
            path_filter: Filter deciding which paths are eligible.
        """
        self.root = root.resolve()
        self.path_filter = path_filter

    def iter_files(self) -> Iterator[Path]:
        """Yield every non-ignored file under the root.

        Yields:
            Absolute Path objects for candidate files (including binary/large).
        """
        for dirpath, dirnames, filenames in os.walk(self.root, topdown=True, followlinks=False):
            dirnames[:] = [
                d for d in dirnames if not self.path_filter.is_ignored_dir(d)
            ]
            current = Path(dirpath)
            for filename in filenames:
                file_path = current / filename
                yield file_path

    def iter_directories(self) -> List[Path]:
        """Collect all non-ignored directories under the root (deepest first).

        Returns:
            List of directory Paths ordered from deepest to shallowest.
        """
        dirs: List[Path] = []
        for dirpath, dirnames, _ in os.walk(self.root, topdown=True, followlinks=False):
            dirnames[:] = [
                d for d in dirnames if not self.path_filter.is_ignored_dir(d)
            ]
            current = Path(dirpath)
            if current != self.root:
                dirs.append(current)
        dirs.sort(key=lambda p: len(p.parts), reverse=True)
        return dirs


class RegexNameReplacer:
    """High-performance regex-based name replacer.

    Patterns are compiled once, ordered longest-first, and matched with
    negative look-behind / look-ahead where appropriate to reduce partial
    matches while still supporting names that contain spaces or hyphens.
    """

    def __init__(self, mappings: Sequence[NameMapping]) -> None:
        """Initialize the replacer and compile all patterns.

        Args:
            mappings: Ordered list of old→new name pairs.
                      Longer keys are applied first.
        """
        ordered = sorted(mappings, key=lambda m: len(m.old), reverse=True)
        self._mappings: List[NameMapping] = ordered
        self._compiled: List[Tuple[re.Pattern[str], str, str]] = []
        for mapping in ordered:
            # Use word-boundary style protection for alphanumeric edges while
            # still allowing the full multi-word / hyphenated names to match.
            escaped = re.escape(mapping.old)
            # Negative look-behind/ahead for word characters reduces partial hits
            # such as matching inside a longer identifier.
            pattern = re.compile(
                rf"(?<![A-Za-z0-9_]){escaped}(?![A-Za-z0-9_])"
            )
            self._compiled.append((pattern, mapping.old, mapping.new))

    def replace(self, content: str) -> Tuple[str, int]:
        """Apply all compiled mappings to the given content.

        Args:
            content: Original file content.

        Returns:
            Tuple of (new_content, total_replacement_count).
        """
        total = 0
        result = content
        for pattern, _old, new in self._compiled:
            result, n = pattern.subn(new, result)
            total += n
        return result, total

    def find_previews(
        self, content: str, *, max_previews: int = MAX_PREVIEWS_PER_FILE
    ) -> List[PreviewEntry]:
        """Locate up to max_previews replacement sites with line context.

        Args:
            content: Original file content.
            max_previews: Maximum number of preview entries to return.

        Returns:
            List of PreviewEntry objects.
        """
        previews: List[PreviewEntry] = []
        lines = content.splitlines()
        for idx, line in enumerate(lines, start=1):
            if len(previews) >= max_previews:
                break
            for pattern, old, new in self._compiled:
                if pattern.search(line):
                    new_line = pattern.sub(new, line)
                    previews.append(
                        PreviewEntry(
                            line_number=idx,
                            old_text=old,
                            new_text=new,
                            context=line.strip()[:200],
                        )
                    )
                    if len(previews) >= max_previews:
                        break
        return previews

    def transform_name(self, name: str) -> Tuple[str, int]:
        """Apply mappings to a file or directory name.

        Args:
            name: Original basename.

        Returns:
            Tuple of (new_name, number_of_replacements).
        """
        return self.replace(name)


class BackupManager:
    """Creates and restores timestamped backups of modified files."""

    def __init__(self, backup_root: Path) -> None:
        """Initialize the backup manager.

        Args:
            backup_root: Base directory that will contain timestamped backups.
        """
        self.backup_root = backup_root
        self._session_dir: Optional[Path] = None

    def create_session(self) -> Path:
        """Create a new timestamped backup directory for the current run.

        Returns:
            Path to the newly created session directory.
        """
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._session_dir = self.backup_root / stamp
        self._session_dir.mkdir(parents=True, exist_ok=True)
        return self._session_dir

    @property
    def session_dir(self) -> Optional[Path]:
        """Return the current session directory if one exists."""
        return self._session_dir

    def backup_file(self, source: Path, root: Path) -> Path:
        """Copy a file into the current backup session preserving relative path.

        Args:
            source: Absolute path of the file to back up.
            root: Repository root used to compute the relative path.

        Returns:
            Path of the backup copy.

        Raises:
            RuntimeError: If no session has been created.
            OSError: On filesystem errors.
        """
        if self._session_dir is None:
            raise RuntimeError("Backup session has not been created")
        rel = source.relative_to(root)
        dest = self._session_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        return dest

    def list_sessions(self) -> List[Path]:
        """Return available backup sessions sorted newest first.

        Returns:
            List of session directory paths.
        """
        if not self.backup_root.is_dir():
            return []
        sessions = [
            p
            for p in self.backup_root.iterdir()
            if p.is_dir() and re.fullmatch(r"\d{8}_\d{6}", p.name)
        ]
        return sorted(sessions, key=lambda p: p.name, reverse=True)

    def undo_latest(self, root: Path) -> Tuple[int, List[str]]:
        """Restore files from the most recent backup session.

        Args:
            root: Repository root where files will be restored.

        Returns:
            Tuple of (files_restored, list_of_errors).
        """
        sessions = self.list_sessions()
        if not sessions:
            return 0, ["No backup sessions found"]
        latest = sessions[0]
        restored = 0
        errors: List[str] = []
        for backup_file in latest.rglob("*"):
            if not backup_file.is_file():
                continue
            rel = backup_file.relative_to(latest)
            target = root / rel
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_file, target)
                restored += 1
            except OSError as exc:
                errors.append(f"{rel}: {exc}")
        return restored, errors


class RenameService:
    """Orchestrates scanning, content replacement, path renaming, backup and reporting."""

    def __init__(
        self,
        config: RenameConfig,
        logger: logging.Logger,
        *,
        colored: bool = True,
    ) -> None:
        """Initialize the service.

        Args:
            config: Runtime configuration.
            logger: Application logger.
            colored: Whether to emit colored console messages.
        """
        self.config = config
        self.logger = logger
        self.colored = colored
        self.root = Path(config.root_dir).resolve()
        self.path_filter = PathFilter(
            config.ignore_dirs, config.supported_extensions
        )
        self.scanner = RepositoryScanner(self.root, self.path_filter)
        self.replacer = RegexNameReplacer(config.mappings)
        self.backup_manager = BackupManager(self.root / config.backup_dir)

    def _print(self, message: str, color: Color = Color.WHITE) -> None:
        """Print a colored message to stdout.

        Args:
            message: Text to print.
            color: Desired color.
        """
        print(colorize(message, color, enabled=self.colored))

    def scan(self) -> RenameReport:
        """Scan the repository and report potential changes without writing.

        Returns:
            RenameReport describing what would change.
        """
        return self._process(dry_run=True, create_backup=False)

    def replace(
        self, *, dry_run: bool = False, create_backup: bool = True
    ) -> RenameReport:
        """Perform name replacements across contents, files and directories.

        Args:
            dry_run: If True, no files or paths are modified.
            create_backup: If True and not dry_run, create a backup first.

        Returns:
            RenameReport with execution statistics.
        """
        return self._process(
            dry_run=dry_run, create_backup=create_backup and not dry_run
        )

    def undo(self) -> RenameReport:
        """Restore the most recent backup.

        Returns:
            RenameReport summarizing the undo operation.
        """
        start = time.perf_counter()
        report = RenameReport(dry_run=False)
        self._print("Starting undo from latest backup…", Color.CYAN)
        restored, errors = self.backup_manager.undo_latest(self.root)
        report.files_modified = restored
        report.total_replacements = restored
        report.errors = errors
        report.execution_time_seconds = time.perf_counter() - start
        if errors:
            for err in errors:
                self.logger.error("Undo error: %s", err)
            self._print(
                f"Undo completed with {len(errors)} error(s).", Color.YELLOW
            )
        else:
            self._print(f"Successfully restored {restored} file(s).", Color.GREEN)
        return report

    def _process(self, *, dry_run: bool, create_backup: bool) -> RenameReport:
        """Internal processing pipeline shared by scan and replace.

        Args:
            dry_run: When True, files and paths are not modified.
            create_backup: When True, a backup session is created.

        Returns:
            Populated RenameReport.
        """
        start = time.perf_counter()
        report = RenameReport(dry_run=dry_run)
        files = list(self.scanner.iter_files())
        report.files_scanned = len(files)

        self._print(
            f"{'Dry-run scan' if dry_run else 'Replace'} – "
            f"{len(files)} candidate file(s) found.",
            Color.CYAN,
        )

        if create_backup and not dry_run:
            session = self.backup_manager.create_session()
            report.backup_path = str(session)
            self.logger.info("Backup session created: %s", session)
            self._print(f"Backup created at: {session}", Color.BLUE)

        progress = ProgressBar(
            total=len(files),
            prefix="Content",
            enabled=self.colored,
        )

        for file_path in files:
            result = self._process_file(file_path, dry_run=dry_run, report=report)
            report.file_results.append(result)
            if result.error:
                report.errors.append(f"{result.path}: {result.error}")
            if result.modified:
                report.files_modified += 1
                report.total_replacements += result.replacements
                report.modified_file_contents.append(result.path)
            progress.update()

        progress.finish()

        # Path renaming (files then directories, deepest first)
        self._rename_paths(report, dry_run=dry_run)

        report.execution_time_seconds = time.perf_counter() - start
        report.finalize_statistics()
        self._print_summary(report)
        if not dry_run and report.files_modified + len(report.path_renames) > 0:
            self._print_git_suggestions()
        return report

    def _process_file(
        self, file_path: Path, *, dry_run: bool, report: RenameReport
    ) -> FileResult:
        """Process a single file: safety checks, read, replace, optionally write.

        Args:
            file_path: Absolute path of the file.
            dry_run: When True, do not write changes.
            report: Report object to update with skip statistics.

        Returns:
            FileResult describing the outcome.
        """
        try:
            rel = str(file_path.relative_to(self.root))
        except ValueError:
            rel = str(file_path)

        # Symlink safety
        if file_path.is_symlink():
            report.skipped_symlinks.append(rel)
            self.logger.debug("Skipping symlink: %s", rel)
            return FileResult(
                path=rel,
                replacements=0,
                modified=False,
                skipped_reason="symlink",
            )

        # Binary extension
        if self.path_filter.is_binary_extension(file_path):
            report.skipped_binary_files.append(rel)
            return FileResult(
                path=rel,
                replacements=0,
                modified=False,
                skipped_reason="binary_extension",
            )

        # Size check
        try:
            size = file_path.stat().st_size
        except OSError as exc:
            self.logger.warning("Cannot stat %s: %s", rel, exc)
            return FileResult(
                path=rel, replacements=0, modified=False, error=str(exc)
            )

        if size > self.config.max_file_size_bytes:
            report.skipped_large_files.append(rel)
            self.logger.info(
                "Skipping large file %s (%d bytes > %d limit)",
                rel,
                size,
                self.config.max_file_size_bytes,
            )
            return FileResult(
                path=rel,
                replacements=0,
                modified=False,
                size_bytes=size,
                skipped_reason="too_large",
            )

        # Only process supported text extensions for content
        if not self.path_filter.is_supported_file(file_path):
            report.ignored_files.append(rel)
            return FileResult(
                path=rel,
                replacements=0,
                modified=False,
                size_bytes=size,
                skipped_reason="unsupported_extension",
            )

        try:
            original = file_path.read_text(encoding=ENCODING)
        except (OSError, UnicodeDecodeError) as exc:
            # Treat decode errors as likely binary
            report.skipped_binary_files.append(rel)
            self.logger.warning("Cannot decode %s as text: %s", rel, exc)
            return FileResult(
                path=rel,
                replacements=0,
                modified=False,
                size_bytes=size,
                skipped_reason="decode_error",
                error=str(exc),
            )

        new_content, count = self.replacer.replace(original)
        previews = (
            self.replacer.find_previews(original) if dry_run and count > 0 else []
        )

        if count == 0:
            return FileResult(
                path=rel, replacements=0, modified=False, size_bytes=size
            )

        if dry_run:
            self.logger.info(
                "[DRY-RUN] Would modify %s (%d replacement(s))", rel, count
            )
            self._print_previews(rel, previews)
            return FileResult(
                path=rel,
                replacements=count,
                modified=True,
                size_bytes=size,
                previews=previews,
            )

        try:
            if self.config.create_backup and self.backup_manager.session_dir:
                self.backup_manager.backup_file(file_path, self.root)
            file_path.write_text(new_content, encoding=ENCODING)
            self.logger.info("Modified content of %s (%d replacement(s))", rel, count)
            return FileResult(
                path=rel, replacements=count, modified=True, size_bytes=size
            )
        except OSError as exc:
            self.logger.error("Failed to write %s: %s", rel, exc)
            return FileResult(
                path=rel,
                replacements=count,
                modified=False,
                size_bytes=size,
                error=str(exc),
            )

    def _print_previews(self, rel: str, previews: List[PreviewEntry]) -> None:
        """Print dry-run previews for a file.

        Args:
            rel: Relative path of the file.
            previews: List of preview entries.
        """
        if not previews:
            return
        self._print(f"  File: {rel}", Color.CYAN)
        for p in previews:
            self._print(f"    Line: {p.line_number}", Color.GRAY)
            self._print(f"    Old:  {p.old_text}", Color.RED)
            self._print(f"    ↓", Color.GRAY)
            self._print(f"    New:  {p.new_text}", Color.GREEN)
            if p.context:
                self._print(f"    Context: {p.context[:120]}", Color.GRAY)
            self._print("", Color.GRAY)

    def _rename_paths(self, report: RenameReport, *, dry_run: bool) -> None:
        """Rename files and directories whose names contain mapped strings.

        Directories are processed deepest-first to preserve hierarchy.

        Args:
            report: Report object to update.
            dry_run: When True, only record intended renames.
        """
        # Files first
        files = list(self.scanner.iter_files())
        for file_path in files:
            if file_path.is_symlink():
                continue
            self._try_rename_path(file_path, report, dry_run=dry_run, is_dir=False)

        # Directories deepest first
        directories = self.scanner.iter_directories()
        for dir_path in directories:
            if dir_path.is_symlink():
                continue
            self._try_rename_path(dir_path, report, dry_run=dry_run, is_dir=True)

    def _try_rename_path(
        self,
        path: Path,
        report: RenameReport,
        *,
        dry_run: bool,
        is_dir: bool,
    ) -> None:
        """Attempt to rename a single file or directory if its name matches.

        Args:
            path: Absolute path to rename.
            report: Report object to update.
            dry_run: When True, do not perform the rename.
            is_dir: True if the path is a directory.
        """
        try:
            rel = str(path.relative_to(self.root))
        except ValueError:
            rel = str(path)

        old_name = path.name
        new_name, count = self.replacer.transform_name(old_name)
        if count == 0 or new_name == old_name:
            return

        new_path = path.with_name(new_name)
        try:
            new_rel = str(new_path.relative_to(self.root))
        except ValueError:
            new_rel = str(new_path)

        if dry_run:
            self.logger.info(
                "[DRY-RUN] Would rename %s → %s", rel, new_rel
            )
            self._print(
                f"  {'Dir' if is_dir else 'File'}: {rel} → {new_rel}",
                Color.YELLOW,
            )
            result = PathRenameResult(
                old_path=rel,
                new_path=new_rel,
                is_directory=is_dir,
                success=True,
            )
            report.path_renames.append(result)
            if is_dir:
                report.modified_directories.append(f"{rel} → {new_rel}")
            else:
                report.modified_filenames.append(f"{rel} → {new_rel}")
            return

        try:
            if new_path.exists():
                raise FileExistsError(f"Target already exists: {new_rel}")
            path.rename(new_path)
            self.logger.info("Renamed %s → %s", rel, new_rel)
            result = PathRenameResult(
                old_path=rel,
                new_path=new_rel,
                is_directory=is_dir,
                success=True,
            )
            report.path_renames.append(result)
            if is_dir:
                report.modified_directories.append(f"{rel} → {new_rel}")
            else:
                report.modified_filenames.append(f"{rel} → {new_rel}")
        except OSError as exc:
            self.logger.error("Failed to rename %s → %s: %s", rel, new_rel, exc)
            result = PathRenameResult(
                old_path=rel,
                new_path=new_rel,
                is_directory=is_dir,
                success=False,
                error=str(exc),
            )
            report.path_renames.append(result)
            report.errors.append(f"Rename {rel} → {new_rel}: {exc}")

    def _print_summary(self, report: RenameReport) -> None:
        """Print a human-readable summary of the report.

        Args:
            report: The completed report.
        """
        self._print("=" * 60, Color.GRAY)
        mode = "DRY-RUN" if report.dry_run else "EXECUTED"
        self._print(f"Summary ({mode})", Color.BOLD)
        self._print(f"  Files scanned           : {report.files_scanned}", Color.WHITE)
        self._print(
            f"  Files modified (content): {report.files_modified}", Color.GREEN
        )
        self._print(
            f"  Total content replacements: {report.total_replacements}", Color.GREEN
        )
        self._print(
            f"  Filenames renamed        : {len(report.modified_filenames)}",
            Color.GREEN,
        )
        self._print(
            f"  Directories renamed      : {len(report.modified_directories)}",
            Color.GREEN,
        )
        self._print(
            f"  Skipped binary files     : {len(report.skipped_binary_files)}",
            Color.YELLOW,
        )
        self._print(
            f"  Skipped large files      : {len(report.skipped_large_files)}",
            Color.YELLOW,
        )
        self._print(
            f"  Skipped symlinks         : {len(report.skipped_symlinks)}",
            Color.YELLOW,
        )
        self._print(
            f"  Errors                   : {len(report.errors)}",
            Color.RED if report.errors else Color.WHITE,
        )
        self._print(
            f"  Avg replacements/file    : {report.average_replacements_per_file:.2f}",
            Color.WHITE,
        )
        if report.largest_modified_file:
            self._print(
                f"  Largest modified file    : {report.largest_modified_file} "
                f"({report.largest_modified_file_size} bytes)",
                Color.WHITE,
            )
        self._print(
            f"  Execution time           : {report.execution_time_seconds:.3f}s",
            Color.WHITE,
        )
        if report.backup_path:
            self._print(f"  Backup path              : {report.backup_path}", Color.BLUE)
        self._print("=" * 60, Color.GRAY)

    def _print_git_suggestions(self) -> None:
        """Print suggested git commands after a successful non-dry-run execution."""
        self._print("", Color.WHITE)
        self._print("Suggested git commands:", Color.CYAN)
        self._print("  git status", Color.WHITE)
        self._print("  git add .", Color.WHITE)
        self._print(
            '  git commit -m "Rename project to Opportunity Intelligence Platform"',
            Color.WHITE,
        )
        self._print("", Color.WHITE)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Construct the command-line argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="rename_project",
        description=(
            "Opportunity Intelligence Platform – Project Rename Utility (v1.1).\n"
            "Scans a repository, replaces project name variants in file contents,\n"
            "renames matching files and directories, creates backups, and supports undo."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python rename_project.py --scan\n"
            "  python rename_project.py --replace --backup\n"
            "  python rename_project.py --replace --dry-run\n"
            "  python rename_project.py --undo\n"
            "  python rename_project.py --report\n"
            "\n"
            "Configuration:\n"
            "  rename_config.yaml (preferred) or rename_config.json\n"
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
    )
    parser.add_argument(
        "--config-dir",
        type=str,
        default=".",
        help="Directory containing rename_config.yaml / rename_config.json (default: .)",
    )
    parser.add_argument(
        "--root",
        type=str,
        default=None,
        help="Repository root directory (overrides config)",
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Scan only – report potential changes with line-level previews",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Perform content and path replacements (creates backup by default)",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Force creation of a backup before replacement",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip backup creation (use with caution)",
    )
    parser.add_argument(
        "--undo",
        action="store_true",
        help="Restore files from the most recent backup session",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Write the JSON report after the operation",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate all changes (content + paths) without writing",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose (DEBUG) logging on console",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored console output",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Application entry point.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code (0 on success, non-zero on error).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if not any([args.scan, args.replace, args.undo, args.report]):
        parser.print_help()
        return 1

    config_dir = Path(args.config_dir).resolve()
    save_default_config(config_dir)
    config = load_config(config_dir)

    if args.root:
        config.root_dir = args.root
    if args.dry_run:
        config.dry_run = True
    if args.no_backup:
        config.create_backup = False
    if args.backup:
        config.create_backup = True
    if args.no_color:
        config.colored_output = False

    logger = setup_logging(config.log_dir, config.log_file, verbose=args.verbose)
    logger.info("Starting rename_project v%s", VERSION)
    logger.debug("Configuration: %s", config.to_dict())

    service = RenameService(
        config=config,
        logger=logger,
        colored=config.colored_output,
    )

    report: Optional[RenameReport] = None
    exit_code = 0

    try:
        if args.undo:
            report = service.undo()
        elif args.scan:
            report = service.scan()
        elif args.replace:
            report = service.replace(
                dry_run=config.dry_run,
                create_backup=config.create_backup,
            )
        else:
            report = RenameReport()
            report.execution_time_seconds = 0.0

        if args.report or args.scan or args.replace or args.undo:
            report_path = Path(config.report_file)
            if report is not None:
                report.save(report_path)
                logger.info("Report written to %s", report_path)
                print(
                    colorize(
                        f"Report saved → {report_path}",
                        Color.MAGENTA,
                        enabled=config.colored_output,
                    )
                )

        if report and report.errors:
            exit_code = 2

    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        print(
            colorize("\nInterrupted.", Color.YELLOW, enabled=config.colored_output)
        )
        exit_code = 130
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unhandled error: %s", exc)
        print(
            colorize(
                f"Fatal error: {exc}", Color.RED, enabled=config.colored_output
            )
        )
        exit_code = 1

    logger.info("Finished with exit code %d", exit_code)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
