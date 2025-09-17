import argparse
import logging
from logging import Logger
from dotenv import load_dotenv
from agents.coding_agent import FallbackOnLimitAgent, LoggingAgent, WaitingOnLimitAgent
from agents.providers.glm import GLMAgent
from agents.providers.sonnet import ClaudeAgent


def parse_init_args() -> argparse.Namespace:
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


def main():
    load_dotenv()
    sonnet_agent = ClaudeAgent()
    glm_agent = GLMAgent()
    fallback_agent = FallbackOnLimitAgent(sonnet_agent, glm_agent)
    waiting_agent = WaitingOnLimitAgent(fallback_agent, wait_hours=2)
    # Configure a logger that writes to ./full_agents_log.txt
    logger: Logger = logging.getLogger("agents.full")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        file_handler = logging.FileHandler("./full_agents_log.txt", encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    logger.propagate = False
    logging_agent = LoggingAgent(waiting_agent, logger)

    args = parse_init_args()
    result = logging_agent.resume(prompt=args.message, session_id=args.session_id)
    return result


if __name__ == "__main__":
    main()
