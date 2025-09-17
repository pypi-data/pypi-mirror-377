from abc import ABC
from logging import Logger
import time

from agents.utils import run_cli


class AuthRequiredError(Exception):
    pass


class LimitExceededError(Exception):
    pass


class NothingToContinueError(Exception):
    pass


class CodingAgent(ABC):
    def run(self, prompt: str, files_to_include: list[str] | None = None) -> str:
        raise NotImplementedError

    def resume(self, prompt: str | None = None, session_id: str | None = None) -> str:
        raise NotImplementedError


class CLIAgent(CodingAgent):
    def __init__(
        self,
        files_to_always_include: list[str] | None = None,
        working_dir: str = "./",
    ):
        self.files_to_always_include: list[str] = files_to_always_include or list()
        self.working_dir = working_dir

    def _build_cmd(self, prompt: str, files_to_include: list[str]) -> list[str]:
        raise NotImplementedError()

    def run(self, prompt: str, files_to_include: list[str] | None = None) -> str:
        cmd = self._build_cmd(prompt, files_to_include)
        return run_cli(cmd, working_dir=self.working_dir)

    def _build_resume_cmd(
        self, prompt: str, session_id: str | None = None
    ) -> list[str]:
        raise NotImplementedError()

    def resume(self, prompt: str | None = None, session_id: str | None = None) -> str:
        cmd = self._build_resume_cmd(prompt or "continue")
        return run_cli(cmd)


class WaitingOnLimitAgent(CodingAgent):
    def __init__(
        self, base_agent: CodingAgent, wait_hours: int = 4, logger: Logger | None = None
    ):
        self.base_agent = base_agent
        self.wait_seconds = wait_hours * 60 * 60
        self.logger = logger

    def run(self, prompt: str, files_to_include: list[str] | None = None) -> str:
        try:
            return self.base_agent.run(prompt, files_to_include)
        except LimitExceededError:
            if self.logger:
                self.logger.info(
                    f"Limit exceeded for {str(self.base_agent)},"
                    " waiting for {self.wait_seconds / 60 / 60} hours before retrying run."
                )
            time.sleep(self.wait_seconds)
            return self.base_agent.run(prompt, files_to_include)

    def resume(self, prompt: str, session_id: str | None = None) -> str:
        try:
            return self.base_agent.resume(prompt, session_id)
        except LimitExceededError:
            if self.logger:
                self.logger.info(
                    f"Limit exceeded for {str(self.base_agent)},"
                    " waiting for {self.wait_seconds / 60 / 60} hours before retrying resume."
                )
            time.sleep(self.wait_seconds)
            return self.base_agent.resume(prompt, session_id)

    def __str__(self) -> str:
        return f"WaitingOnLimitAgent({str(self.base_agent)})"


class FallbackOnLimitAgent(CodingAgent):
    def __init__(
        self,
        base_agent: CodingAgent,
        fallback_agent: CodingAgent,
        logger: Logger | None = None,
    ) -> None:
        self.base_agent = base_agent
        self.fallback_agent = fallback_agent
        self.logger = logger

    def run(self, prompt: str, files_to_include: list[str] | None = None) -> str:
        try:
            return self.base_agent.run(prompt, files_to_include)
        except LimitExceededError:
            if self.logger:
                self.logger.info(
                    f"Limit exceeded for {str(self.base_agent)},"
                    f" falling back to {str(self.fallback_agent)}."
                )
            return self.fallback_agent.run(prompt, files_to_include)

    def resume(self, prompt: str, session_id: str | None = None) -> str:
        try:
            return self.base_agent.resume(prompt, session_id)
        except LimitExceededError:
            if self.logger:
                self.logger.info(
                    f"Limit exceeded for {str(self.base_agent)},"
                    f" falling back to {str(self.fallback_agent)}."
                )
            return self.fallback_agent.resume(prompt, session_id)

    def __str__(self) -> str:
        return (
            f"FallbackOnLimitAgent({str(self.base_agent)}, {str(self.fallback_agent)})"
        )


class LoggingAgent(CodingAgent):
    def __init__(self, base_agent: CodingAgent, logger: Logger) -> None:
        self.base_agent = base_agent
        self.logger = logger

    def run(self, prompt: str, files_to_include: list[str] | None = None) -> str:
        run_id = str(time.time_ns())
        self.logger.info(f"[{run_id}] Running {self.base_agent} with prompt:\n{prompt}")
        result = self.base_agent.run(prompt, files_to_include)
        self.logger.info(f"[{run_id}] Run result:\n{result}")
        return result

    def resume(self, prompt: str, session_id: str | None = None) -> str:
        run_id = str(time.time_ns())
        self.logger.info(
            f"[{run_id}] Resuming {self.base_agent} with prompt:\n{prompt}"
        )
        result = self.base_agent.resume(prompt, session_id)
        self.logger.info(f"[{run_id}] Resume result:\n{result}")
        return result

    def __str__(self) -> str:
        return f"LoggingAgent({str(self.base_agent)})"
