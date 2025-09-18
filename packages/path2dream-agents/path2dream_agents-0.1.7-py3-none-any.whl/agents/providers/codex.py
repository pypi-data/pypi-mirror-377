import re
import sys

from agents.coding_agent import AuthRequiredError, CLIAgent, LimitExceededError
from agents.utils import build_prompt, get_files_suffix, parse_common_args
from agents.send_email import send_email

TIMESTAMP_REGEX = re.compile(
    r"\[[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\]"
)
AUTH_ERROR_SNIPPET = "stream error: unexpected status 401 Unauthorized"
LIMITS_EXCEEDED_ERROR = (
    "You exceeded your current quota, please check your plan and billing details"
)


def extract_content_between_last_two_timestamps(
    content: str, timestamp_regex: re.Pattern[str]
) -> str:
    lines = content.splitlines()

    match_line_numbers = []  # 1-based line numbers
    for idx, line in enumerate(lines, start=1):
        if timestamp_regex.search(line):
            match_line_numbers.append(idx)

    if len(match_line_numbers) < 2:
        return content

    prelast_ln = match_line_numbers[-2]
    last_ln = match_line_numbers[-1]

    start_idx = prelast_ln
    end_idx = last_ln - 1

    result = ""
    for line in lines[start_idx:end_idx]:
        result += f"{line}\n"
    return result


class CodexAgent(CLIAgent):
    def _build_cmd(self, prompt: str, files_to_include: list[str]) -> list[str]:
        cmd = [
            "codex",
            "exec",
            "--cd",
            self.working_dir,
            "--dangerously-bypass-approvals-and-sandbox",
        ]

        prompt_suffix = get_files_suffix(
            self.files_to_always_include + (files_to_include or []), self.working_dir
        )
        full_prompt = prompt + prompt_suffix

        cmd.append(f'"{full_prompt}"')
        return cmd

    def run(self, prompt: str, files_to_include: list[str] | None = None) -> str:
        content = super().run(prompt, files_to_include)
        if AUTH_ERROR_SNIPPET in content:
            raise AuthRequiredError
        if LIMITS_EXCEEDED_ERROR in content:
            raise LimitExceededError
        return extract_content_between_last_two_timestamps(content, TIMESTAMP_REGEX)


def main():
    args = parse_common_args()
    prompt = build_prompt(args.instructions, args.message)
    agent = CodexAgent()
    try:
        result = agent.run(prompt, files_to_include=args.files)
    except AuthRequiredError:
        send_email("codex needs re-auth")
        sys.stdout.write("codex is not available right now")
        sys.exit(1)
    except LimitExceededError:
        send_email("codex limits exceeded")
        sys.stdout.write("codex is not available right now")
        sys.exit(1)
    sys.stdout.write(result)
    sys.exit(0)


if __name__ == "__main__":
    main()
