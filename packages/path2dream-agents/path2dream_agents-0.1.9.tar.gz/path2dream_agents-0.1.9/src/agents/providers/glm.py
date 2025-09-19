import os
from agents.coding_agent import CodingAgent
from agents.providers.sonnet import ClaudeAgent
from agents.coding_agent import LoggingAgent, WaitingOnLimitAgent
from agents.utils import (
    parse_init_args,
    parse_resume_args,
    parse_call_args,
    build_init_prompt,
    build_logger,
)
from dotenv import load_dotenv


class GLMAgent(ClaudeAgent):
    def get_extra_env_vars(self) -> dict[str, str] | None:
        return {
            "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
            "ANTHROPIC_AUTH_TOKEN": os.environ["GLM_AUTH_TOKEN"],
        }


def build_agent() -> CodingAgent:
    load_dotenv()
    agent = GLMAgent()
    logger = build_logger("./full_agents_log.txt")
    waiting_on_limit_agent = WaitingOnLimitAgent(agent, wait_hours=1, logger=logger)
    logging_agent = LoggingAgent(waiting_on_limit_agent, logger)
    return logging_agent


def call() -> str:
    args = parse_call_args()
    agent = build_agent()
    result = agent.run(args.message, files_to_include=args.files)
    return result


def init() -> str:
    args = parse_init_args()
    prompt = build_init_prompt(args.instructions_path)
    agent = build_agent()
    result = agent.run(prompt, files_to_include=args.files)
    return result


def resume() -> str:
    args = parse_resume_args()
    agent = build_agent()
    result = agent.resume(prompt=args.message, session_id=args.session_id)
    return result
