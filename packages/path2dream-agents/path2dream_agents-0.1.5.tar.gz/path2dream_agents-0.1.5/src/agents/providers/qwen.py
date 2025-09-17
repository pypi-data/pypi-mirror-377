import sys

from agents.coding_agent import AuthRequiredError, CLIAgent
from agents.utils import build_prompt, get_file_tags_suffix, parse_common_args
from agents.send_email import send_email

# todo support working dirs
# todo remove thoughts from output
# todo support limit processing

AUTH_ERROR_SNIPPET = "Please set an Auth method"


class QwenAgent(CLIAgent):
    def _build_cmd(self, prompt: str, files_to_include: list[str]) -> list[str]:
        prompt_suffix = get_file_tags_suffix(
            self.files_to_always_include + (files_to_include or []), self.working_dir
        )
        full_prompt = prompt + prompt_suffix

        cmd = ["qwen", "--yolo", "--prompt", f'"{full_prompt}"']
        return cmd

    def run(self, prompt: str, files_to_include: list[str] | None = None) -> str:
        content = super().run(prompt, files_to_include)
        if AUTH_ERROR_SNIPPET in content:
            raise AuthRequiredError
        return content


def main():
    args = parse_common_args()
    prompt = build_prompt(args.instructions, args.message)
    agent = QwenAgent()
    try:
        result = agent.run(prompt, files_to_include=args.files)
    except AuthRequiredError:
        send_email("qwen needs re-auth")
        sys.stdout.write("qwen is not available right now")
        sys.exit(1)
    sys.stdout.write(result)
    sys.exit(0)


if __name__ == "__main__":
    main()
