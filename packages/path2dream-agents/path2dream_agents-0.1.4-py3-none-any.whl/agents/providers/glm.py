import os
import sys
from agents.coding_agent import LimitExceededError
from agents.providers.sonnet import ClaudeAgent
from agents.send_email import send_email
from agents.utils import parse_common_args, build_prompt


class GLMAgent(ClaudeAgent):
    def __init__(
        self,
        model: str = "sonnet",
        files_to_always_include: list[str] | None = None,
        working_dir: str = "./",
    ):
        super().__init__(model, files_to_always_include, working_dir)
        self.glm_cmd = [
            "ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic",
            f"ANTHROPIC_AUTH_TOKEN={os.environ['GLM_AUTH_TOKEN']}",
        ]

    def _build_cmd(self, prompt: str, files_to_include: list[str]) -> list[str]:
        claude_cmd = super()._build_cmd(prompt)
        return self.glm_cmd + claude_cmd

    def _build_resume_cmd(self, prompt: str) -> list[str]:
        claude_cmd = super()._build_resume_cmd(prompt)
        return self.glm_cmd + claude_cmd


def main():
    args = parse_common_args()
    prompt = build_prompt(args.instructions, args.message)
    agent = GLMAgent()
    try:
        result = agent.run(prompt, files_to_include=args.files)
    except LimitExceededError:
        send_email("glm limits exceeded")
        sys.stdout.write("glm is not available right now")
        sys.exit(1)
    sys.stdout.write(result)
    sys.exit(0)


if __name__ == "__main__":
    main()
