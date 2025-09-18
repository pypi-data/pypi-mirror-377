import argparse
import os
import re
import subprocess
import glob
import tempfile


# todo I am still not sure that termination works properly


def run_cli_and_capture_output(
    cmd: list[str],
    output_path: str,
    extra_env_vars: dict[str, str] = None,
    working_dir: str | None = None,
) -> int:
    """Run a CLI command, capturing output, and cleanly tear down on signals.

    - Spawns the child in its own process group so signals reach the whole tree.
    - On SIGINT/SIGTERM/SIGHUP, sends SIGTERM then escalates to SIGKILL after 5s.
    - Restores previous signal handlers before returning.
    - Captures stdout and stderr to the specified output file.

    Returns the child's exit code. May raise KeyboardInterrupt if not handled.
    """
    extended_env = os.environ.copy()
    if extra_env_vars:
        extended_env.update(extra_env_vars)

    with open(output_path, "w", encoding="utf-8", errors="replace") as out:
        proc = subprocess.Popen(
            cmd,
            stdout=out,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            env=extended_env,
            cwd=working_dir,
        )
        return proc.wait()


def run_cli(
    cmd: list[str],
    working_dir: str | None = None,
    extra_env_vars: dict[str, str] = None,
) -> str:
    with tempfile.NamedTemporaryFile() as tmp_file:
        run_cli_and_capture_output(cmd, tmp_file.name, working_dir=working_dir)
        content = tmp_file.read().decode("utf-8")
    return content


def gather_files(all_files_to_include: list[str], working_dir: str) -> list[str]:
    """Expand a list of file/dir patterns into concrete file paths.

    Supports:
    - Globs (e.g., "src/**/*.py") resolved relative to `working_dir` if not absolute.
    - Literal file or directory paths. If a directory, include all files under it.
    - Regex directories via prefix "re:". The regex matches relative dir paths; all files
      within matching directories are included.

    Raises FileNotFoundError if any pattern yields no matches.
    Returns a de-duplicated list preserving first-seen order.
    """
    matched_files: list[str] = []

    for pattern in all_files_to_include:
        if not pattern:
            continue

        # Regex directory selection via prefix "re:"
        if pattern.startswith("re:"):
            regex = pattern[3:]
            try:
                rx = re.compile(regex)
            except re.error as e:
                raise ValueError(f"Invalid regex in pattern '{pattern}': {e}") from e

            found_any = False
            for dirpath, dirnames, filenames in os.walk(working_dir):
                rel_dir = os.path.relpath(dirpath, working_dir)
                if rel_dir == ".":
                    rel_dir = ""
                if rx.search(rel_dir):
                    for fn in filenames:
                        matched_files.append(os.path.join(dirpath, fn))
                        found_any = True
            if not found_any:
                raise FileNotFoundError(
                    f"Requested directory regex matched nothing: {pattern}"
                )
            continue

        # Resolve non-absolute patterns relative to working_dir
        base_pattern = pattern
        if not os.path.isabs(base_pattern):
            base_pattern = os.path.join(working_dir, base_pattern)

        has_wildcard = any(ch in base_pattern for ch in ["*", "?", "["])
        if has_wildcard:
            matches = glob.glob(base_pattern, recursive=True)
            # If any match is a directory, include all files under it
            expanded: list[str] = []
            for m in matches:
                if os.path.isdir(m):
                    for dirpath, _, filenames in os.walk(m):
                        for fn in filenames:
                            expanded.append(os.path.join(dirpath, fn))
                else:
                    expanded.append(m)
            if not expanded:
                raise FileNotFoundError(f"Requested file not found: {pattern}")
            matched_files.extend(expanded)
        else:
            if not os.path.exists(base_pattern):
                raise FileNotFoundError(f"Requested file not found: {pattern}")
            if os.path.isdir(base_pattern):
                for dirpath, _, filenames in os.walk(base_pattern):
                    for fn in filenames:
                        matched_files.append(os.path.join(dirpath, fn))
            else:
                matched_files.append(base_pattern)

    # Deduplicate while preserving order
    seen = set()
    unique_files: list[str] = []
    for f in matched_files:
        if f not in seen:
            seen.add(f)
            unique_files.append(f)
    return unique_files


def get_files_suffix(all_files_to_include: list[str], working_dir: str) -> str:
    """Build a prompt suffix that inlines the contents of matched files.

    Wraps each file in START/END markers with a path relative to `working_dir`.
    """
    files = gather_files(all_files_to_include, working_dir)
    if not files:
        return ""

    parts: list[str] = ["\n\nContext files:\n\n"]
    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as fh:
                content = fh.read()
        except OSError as e:
            raise FileNotFoundError(f"Unable to read file: {file_path}") from e

        display_path = os.path.relpath(file_path, working_dir)
        parts.append(
            f"<=START OF FILE {display_path}=>\n\n{content}\n\n<=END OF FILE {display_path}=>\n\n"
        )

    return "".join(parts)


def get_file_tags_suffix(all_files_to_include: list[str], working_dir: str) -> str:
    files = gather_files(all_files_to_include, working_dir)
    if not files:
        return ""

    parts: list[str] = ["\nContext files:"]
    for file_path in files:
        parts.append(f"@{file_path}")

    return "\n".join(parts)


def parse_common_args() -> argparse.Namespace:
    """Parse shared CLI args: --instructions and --message.

    Returns an argparse.Namespace with attributes: instructions, message.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--instructions",
        required=False,
        help="Path to system instructions file",
        default=None,
    )
    parser.add_argument(
        "--files",
        required=False,
        help="Extra file pathes for agent to read before starting work",
        nargs="+",
        default=[],
    )
    parser.add_argument(
        "--message", required=True, help="Message to send after instructions"
    )
    return parser.parse_args()


def build_prompt(instructions_path: str | None, message: str) -> str:
    prompt = ""
    if instructions_path:
        prompt += f"You instructions are stored in file @{instructions_path}. Read it fully and strictly follow them!\n\n"
    prompt += f"New message from user: {message}"
    return prompt


def parse_init_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--instructions_path", required=True, help="Path to system instructions file"
    )
    parser.add_argument(
        "--files",
        required=False,
        help="Extra file pathes for agent to read before starting work",
        nargs="+",
        default=[],
    )
    return parser.parse_args()


def build_init_prompt(instructions_path: str) -> str:
    return f"""You instructions are stored in file @{instructions_path}. 
        Read it fully and strictly follow them!
        After reading, please, introduce yourself and tell what can you do?"""


def parse_resume_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--session-id",
        required=True,
        help="Session ID (valid UUID), to get it run init of the agent first.",
    )
    parser.add_argument(
        "--message", required=True, help="Message to send to the agent."
    )
    return parser.parse_args()
