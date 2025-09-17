import os
from unittest.mock import patch

from sqlmodel import col, select

from planar.ai import models as m
from planar.ai.agent import Agent
from planar.ai.pydantic_ai import ModelRunResponse
from planar.workflows.decorators import workflow
from planar.workflows.execution import execute
from planar.workflows.models import StepType, WorkflowStep


async def test_agent_tool_step_has_display_name(session):
    async def add(a: int, b: int) -> int:
        return a + b

    # Prepare mocked model responses: first triggers a tool call, then returns final content
    first = ModelRunResponse[str](
        response=m.CompletionResponse[str](
            content=None,
            tool_calls=[
                m.ToolCall(id="call_1", name="add", arguments={"a": 2, "b": 3})
            ],
            text_content="",
            reasoning_content=None,
        ),
        extra_turns_used=0,
    )
    second = ModelRunResponse[str](
        response=m.CompletionResponse[str](
            content="5",
            tool_calls=[],
            text_content="5",
            reasoning_content=None,
        ),
        extra_turns_used=0,
    )

    responses = [first, second]

    async def fake_model_run(*args, **kwargs):
        assert responses, "No more fake responses configured"
        return responses.pop(0)

    # Patch the model run to avoid any network/model dependency
    # Use unittest.mock.patch context managers to ensure cleanup
    with (
        patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False),
        patch("planar.ai.agent.model_run", side_effect=fake_model_run),
    ):
        agent = Agent[str, str](
            name="test_agent",
            system_prompt="",
            user_prompt="",
            model="openai:gpt-4o-mini",
            tools=[add],
            max_turns=3,
        )

        @workflow()
        async def run_agent():
            result = await agent("please add")
            return result.output

        wf = await run_agent.start()
        result = await execute(wf)
    assert result == "5"

    steps = (
        await session.exec(select(WorkflowStep).order_by(col(WorkflowStep.step_id)))
    ).all()
    # Ensure there is a tool call step with the display name set to the tool name
    tool_steps = [s for s in steps if s.step_type == StepType.TOOL_CALL]
    assert tool_steps, "Expected at least one TOOL_CALL step recorded"
    assert any(s.display_name == "add" for s in tool_steps), (
        f"Expected a TOOL_CALL step with display_name 'add', got {[s.display_name for s in tool_steps]}"
    )
