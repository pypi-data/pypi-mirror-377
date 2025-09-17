import time
from agents.coding_agent import (
    CodingAgent,
    LimitExceededError,
    WaitingOnLimitAgent,
    FallbackOnLimitAgent,
)


class MockSuccessAgent(CodingAgent):
    def __init__(self, response: str = "success"):
        self.response = response

    def run(self, prompt: str, files_to_include: list[str] | None = None) -> str:
        return self.response

    def resume(self, prompt: str, session_id: str | None = None) -> str:
        return self.response


class MockLimitExceededAgent(CodingAgent):
    def run(self, prompt: str, files_to_include: list[str] | None = None) -> str:
        raise LimitExceededError("Rate limit exceeded")

    def resume(self, prompt: str, session_id: str | None = None) -> str:
        raise LimitExceededError("Rate limit exceeded")


class MockFlipFlopAgent(CodingAgent):
    def __init__(self):
        self.run_count = 0
        self.resume_count = 0

    def run(self, prompt: str, files_to_include: list[str] | None = None) -> str:
        self.run_count += 1
        if self.run_count == 1:
            raise LimitExceededError("First attempt failed")
        return "success on retry"

    def resume(self, prompt: str, session_id: str | None = None) -> str:
        self.resume_count += 1
        if self.resume_count == 1:
            raise LimitExceededError("First resume failed")
        return "resume success on retry"


class TestWaitingOnLimitAgent:
    def test_successful_run_no_wait(self):
        """Test that successful runs don't trigger waiting"""
        base_agent = MockSuccessAgent("test response")
        waiting_agent = WaitingOnLimitAgent(base_agent, wait_hours=1)

        result = waiting_agent.run("test prompt")
        assert result == "test response"

    def test_successful_resume_no_wait(self):
        """Test that successful resumes don't trigger waiting"""
        base_agent = MockSuccessAgent("resume response")
        waiting_agent = WaitingOnLimitAgent(base_agent, wait_hours=1)

        result = waiting_agent.resume("resume prompt")
        assert result == "resume response"

    def test_run_with_limit_exceeded_waits_and_retries(self, monkeypatch):
        """Test that limit exceeded triggers wait and retry for run"""
        # Track sleep calls
        sleep_calls = []

        def mock_sleep(seconds):
            sleep_calls.append(seconds)

        monkeypatch.setattr(time, "sleep", mock_sleep)

        base_agent = MockFlipFlopAgent()
        waiting_agent = WaitingOnLimitAgent(base_agent, wait_hours=2)

        result = waiting_agent.run("test prompt")

        # Should have called sleep with 2 hours in seconds
        assert sleep_calls == [2 * 60 * 60]
        assert result == "success on retry"
        assert base_agent.run_count == 2  # Failed once, succeeded on retry

    def test_resume_with_limit_exceeded_waits_and_retries(self, monkeypatch):
        """Test that limit exceeded triggers wait and retry for resume"""
        sleep_calls = []

        def mock_sleep(seconds):
            sleep_calls.append(seconds)

        monkeypatch.setattr(time, "sleep", mock_sleep)

        base_agent = MockFlipFlopAgent()
        waiting_agent = WaitingOnLimitAgent(base_agent, wait_hours=1)

        result = waiting_agent.resume("resume prompt")

        assert sleep_calls == [1 * 60 * 60]
        assert result == "resume success on retry"
        assert base_agent.resume_count == 2


class TestFallbackOnLimitAgent:
    def test_successful_run_uses_base_agent(self):
        """Test that successful runs use base agent"""
        base_agent = MockSuccessAgent("base response")
        fallback_agent = MockSuccessAgent("fallback response")
        fallback_wrapper = FallbackOnLimitAgent(base_agent, fallback_agent)

        result = fallback_wrapper.run("test prompt")
        assert result == "base response"

    def test_successful_resume_uses_base_agent(self):
        """Test that successful resumes use base agent"""
        base_agent = MockSuccessAgent("base resume")
        fallback_agent = MockSuccessAgent("fallback resume")
        fallback_wrapper = FallbackOnLimitAgent(base_agent, fallback_agent)

        result = fallback_wrapper.resume("resume prompt")
        assert result == "base resume"

    def test_run_with_limit_exceeded_uses_fallback(self):
        """Test that limit exceeded in run triggers fallback"""
        base_agent = MockLimitExceededAgent()
        fallback_agent = MockSuccessAgent("fallback response")
        fallback_wrapper = FallbackOnLimitAgent(base_agent, fallback_agent)

        result = fallback_wrapper.run("test prompt")
        assert result == "fallback response"

    def test_resume_with_limit_exceeded_uses_fallback(self):
        """Test that limit exceeded in resume triggers fallback"""
        base_agent = MockLimitExceededAgent()
        fallback_agent = MockSuccessAgent("fallback resume")
        fallback_wrapper = FallbackOnLimitAgent(base_agent, fallback_agent)

        result = fallback_wrapper.resume("resume prompt")
        assert result == "fallback resume"

    def test_run_with_files_to_include(self):
        """Test that files_to_include parameter is passed through correctly"""
        base_agent = MockLimitExceededAgent()
        fallback_agent = MockSuccessAgent("fallback with files")
        fallback_wrapper = FallbackOnLimitAgent(base_agent, fallback_agent)

        result = fallback_wrapper.run("test prompt", ["file1.py", "file2.py"])
        assert result == "fallback with files"
