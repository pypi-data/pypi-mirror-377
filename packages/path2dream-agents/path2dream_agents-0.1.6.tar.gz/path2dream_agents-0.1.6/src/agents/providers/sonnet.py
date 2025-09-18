import sys
import uuid
from agents.coding_agent import CLIAgent, LimitExceededError
from agents.send_email import send_email
from agents.utils import get_file_tags_suffix, parse_common_args, build_prompt

# todo support re-auth

LIMITS_EXCEEDED_ERROR = "5-hour limit reached"


class ClaudeAgent(CLIAgent):
    def __init__(
        self,
        model: str = "sonnet",
        files_to_always_include: list[str] | None = None,
        working_dir: str = "./",
    ):
        super().__init__(files_to_always_include, working_dir)
        self.model = model
        self._new_session_id: str | None = None

    def _build_cmd(self, prompt: str, files_to_include: list[str]) -> list[str]:
        prompt_suffix = get_file_tags_suffix(
            self.files_to_always_include + (files_to_include or []), self.working_dir
        )
        full_prompt = prompt + prompt_suffix

        self._new_session_id = str(uuid.uuid4())

        cmd = [
            "claude",
            "--model",
            self.model,
            "--dangerously-skip-permissions",
            "--print",
            "--session-id",
            self._new_session_id,
            f'"{full_prompt}"',
        ]
        return cmd

    def run(self, prompt: str, files_to_include: list[str] | None = None) -> str:
        content = super().run(prompt, files_to_include)
        if LIMITS_EXCEEDED_ERROR in content:
            raise LimitExceededError

        content += f"\n\nSession id of this conversation: {self._new_session_id}\nUse it to contunie this conversation."

        return content

    def _build_resume_cmd(
        self, prompt: str, session_id: str | None = None
    ) -> list[str]:
        cmd = [
            "claude",
            "--model",
            self.model,
            "--dangerously-skip-permissions",
            "--print",
        ]

        if session_id:
            cmd.append(f"--resume {session_id}")
        else:
            cmd.append("--continue")

        cmd.append(prompt)

        return cmd

    def resume(self, prompt: str | None, session_id: str | None = None) -> str:
        content = super().resume(prompt, session_id)
        if LIMITS_EXCEEDED_ERROR in content:
            raise LimitExceededError
        return content


def main():
    args = parse_common_args()
    prompt = build_prompt(args.instructions, args.message)
    agent = ClaudeAgent()
    try:
        result = agent.run(prompt, files_to_include=args.files)
    except LimitExceededError:
        send_email("claude limits exceeded")
        sys.stdout.write("claude is not available right now")
        sys.exit(1)
    sys.stdout.write(result)
    sys.exit(0)


if __name__ == "__main__":
    main()
