import os
import sys
from agents.coding_agent import LimitExceededError
from agents.providers.sonnet import ClaudeAgent
from agents.send_email import send_email
from agents.utils import parse_init_args, parse_resume_args, build_init_prompt
from dotenv import load_dotenv


class GLMAgent(ClaudeAgent):
    def get_extra_env_vars(self) -> dict[str, str] | None:
        return {
            "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
            "ANTHROPIC_AUTH_TOKEN": os.environ["GLM_AUTH_TOKEN"],
        }


def init():
    load_dotenv()
    args = parse_init_args()
    prompt = build_init_prompt(args.instructions_path)
    agent = GLMAgent()
    try:
        result = agent.run(prompt, files_to_include=args.files)
    except LimitExceededError:
        send_email("glm limits exceeded")
        sys.stdout.write("glm is not available right now")
        sys.exit(1)
    sys.stdout.write(result)
    sys.exit(0)


def resume():
    load_dotenv()
    args = parse_resume_args()
    agent = GLMAgent()
    try:
        result = agent.resume(prompt=args.message, session_id=args.session_id)
    except LimitExceededError:
        send_email("glm limits exceeded")
        sys.stdout.write("glm is not available right now")
        sys.exit(1)
    sys.stdout.write(result)
    sys.exit(0)
