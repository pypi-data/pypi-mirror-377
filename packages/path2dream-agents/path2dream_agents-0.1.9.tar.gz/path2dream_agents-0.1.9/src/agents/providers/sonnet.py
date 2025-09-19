import uuid
from agents.coding_agent import CLIAgent, LimitExceededError
from agents.utils import (
    get_file_tags_suffix,
    build_logger,
    parse_call_args,
    parse_init_args,
    parse_resume_args,
    build_init_prompt,
)
from dotenv import load_dotenv
from agents.coding_agent import LoggingAgent, WaitingOnLimitAgent
from agents.coding_agent import CodingAgent

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


def build_agent() -> CodingAgent:
    load_dotenv()
    agent = ClaudeAgent()
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
