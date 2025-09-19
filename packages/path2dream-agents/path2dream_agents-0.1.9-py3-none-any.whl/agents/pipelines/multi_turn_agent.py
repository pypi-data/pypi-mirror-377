from dotenv import load_dotenv
from agents.coding_agent import (
    CodingAgent,
    FallbackOnLimitAgent,
    LoggingAgent,
    WaitingOnLimitAgent,
)
from agents.providers.glm import GLMAgent
from agents.providers.sonnet import ClaudeAgent
from agents.utils import (
    parse_init_args,
    parse_resume_args,
    build_init_prompt,
    parse_call_args,
    build_logger,
)


def build_agent() -> CodingAgent:
    load_dotenv()
    sonnet_agent = ClaudeAgent()
    glm_agent = GLMAgent()

    logger = build_logger("./full_agents_log.txt")
    fallback_agent = FallbackOnLimitAgent(sonnet_agent, glm_agent, logger)
    waiting_agent = WaitingOnLimitAgent(fallback_agent, logger=logger, wait_hours=1)
    logging_agent = LoggingAgent(waiting_agent, logger)
    return logging_agent


def call() -> str:
    agent = build_agent()
    args = parse_call_args()
    result = agent.run(
        prompt=args.message,
        files_to_include=args.files,
    )
    return result


def init() -> str:
    agent = build_agent()
    args = parse_init_args()
    result = agent.run(
        prompt=build_init_prompt(args.instructions_path),
        files_to_include=args.files,
    )
    return result


def resume() -> str:
    agent = build_agent()
    args = parse_resume_args()
    result = agent.resume(prompt=args.message, session_id=args.session_id)
    return result
