import sys

from agents.coding_agent import AuthRequiredError, CLIAgent, LimitExceededError
from agents.utils import build_prompt, get_file_tags_suffix, parse_common_args
from agents.send_email import send_email

AUTH_ERROR_SNIPPET = "Please visit the following URL to authorize the application"
LIMITS_EXCEEDED_ERROR = "Error when talking to Gemini API"


class GeminiAgent(CLIAgent):
    def _build_cmd(self, prompt: str, files_to_include: list[str]) -> list[str]:
        prompt_suffix = get_file_tags_suffix(
            self.files_to_always_include + (files_to_include or []), self.working_dir
        )
        full_prompt = prompt + prompt_suffix

        cmd = [
            "gemini",
            "-m",
            "gemini-2.5-pro",
            "--yolo",
            "--prompt",
            f'"{full_prompt}"',
        ]
        return cmd

    def run(self, prompt: str, files_to_include: list[str] | None = None) -> str:
        content = super().run(prompt, files_to_include)
        if AUTH_ERROR_SNIPPET in content:
            raise AuthRequiredError
        if LIMITS_EXCEEDED_ERROR in content:
            raise LimitExceededError
        return content


def main():
    args = parse_common_args()
    prompt = build_prompt(args.instructions, args.message)
    agent = GeminiAgent()
    try:
        result = agent.run(prompt, files_to_include=args.files)
    except AuthRequiredError:
        send_email("gemini needs re-auth")
        sys.stdout.write("gemini is not available right now")
        sys.exit(1)
    except LimitExceededError:
        send_email("gemini limits exceeded")
        sys.stdout.write("gemini is not available right now")
        sys.exit(1)
    sys.stdout.write(result)
    sys.exit(0)


if __name__ == "__main__":
    main()
