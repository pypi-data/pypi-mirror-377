import os
import sys
from agents.coding_agent import LimitExceededError
from agents.providers.sonnet import ClaudeAgent
from agents.send_email import send_email
from agents.utils import parse_common_args, build_prompt


class GLMAgent(ClaudeAgent):
    def get_extra_env_vars(self) -> dict[str, str] | None:
        return {
            "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
            "ANTHROPIC_AUTH_TOKEN": os.environ["GLM_AUTH_TOKEN"],
        }


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
