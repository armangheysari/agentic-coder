import logging

from agents import Agent, Runner, ModelSettings

from .model_config import model
from .tools.sandbox_tools import sandbox_tools

for name in ("httpx", "httpcore", "httpx2", "httpcore2", "h2", "openai"):
    logging.getLogger(name).setLevel(logging.WARNING)

MAX_TURNS = 10

LEAD_INSTRUCTIONS = """
You are an Engineering Lead for the engineering team, directing the work of the engineers.
You are given high level requirements for a system.
You are responsible for designing the system to achieve the requirements, and assigning work to 3 engineers: backend_engineer, frontend_engineer, and test_engineer.
You should describe the modules, classes, functions to be built. Give function signatures but do not write any code.
All the engineers will have access to a sandbox to write, execute and test code. All files are in the same directory; no subdirectories / packages.
Everything runs in a uv project with gradio installed; no other third-party packages are available.
In your design, include explicit Gradio 6 API guidance for the frontend engineer (correct kwargs, method signatures, where things have changed from earlier versions), since they do not have access to documentation lookup.
Success criteria: the system is successfully built and works.
"""

BACKEND_INSTRUCTIONS = """
You are a Python Backend Engineer who can write code to achieve the design described by the engineering lead.
Use your sandbox tools to write and check python module(s) to achieve the design described by the engineering lead, in order to achieve the requirements.
Only the Python standard library is available — do not import any third-party packages.
Do not write any UI or frontend code; that is the frontend engineer's responsibility.
"""

FRONTEND_INSTRUCTIONS = """
You are a Gradio expert who can write a simple frontend to demonstrate a backend, and can validate that it will open as expected.
Use your sandbox tools to write a gradio UI that demonstrates the given backend, all in one file to be in the same directory as the backend, as described in the design.
Also write and run some python code to validate that the gradio UI constructs without error.
Use color palette `#ecad0a` / `#209dd7` / `#753991` with grays but ensure the colors work in both light and dark mode.
Everything runs in a uv project with gradio installed; gradio is the only third-party package available, so do not import any others.
Success criteria: the gradio UI looks great in light mode and dark mode; the _validate.py script runs well and demonstrates that the gradio UI constructs.
"""

TEST_INSTRUCTIONS = """
You are an engineer with python coding skills who can write unit tests for the given code.
Use your sandbox tools to write unit tests for the backend module, run them and check the results are as expected. Fix any defects and rerun the tests until they pass.
Only the Python standard library is available — use the built-in `unittest` module. Do not use pytest or any other third-party packages.
"""

backend_settings = ModelSettings(tool_choice="auto")

engineering_lead = Agent(
    name="Engineering Lead",
    instructions=LEAD_INSTRUCTIONS,
    model=model,
)

backend_engineer = Agent(
    name="Backend Engineer",
    instructions=BACKEND_INSTRUCTIONS,
    model=model,
    tools=sandbox_tools,
    model_settings=backend_settings,
)

frontend_engineer = Agent(
    name="Frontend Engineer",
    instructions=FRONTEND_INSTRUCTIONS,
    model=model,
    tools=sandbox_tools,
    model_settings=backend_settings,
)

test_engineer = Agent(
    name="Test Engineer",
    instructions=TEST_INSTRUCTIONS,
    model=model,
    tools=sandbox_tools,
    model_settings=backend_settings,
)


async def run(requirements: str):
    design = await Runner.run(
        engineering_lead,
        f"Here are the requirements: {requirements}",
        max_turns=MAX_TURNS,
    )
    design_output = design.final_output

    code = await Runner.run(
        backend_engineer,
        f"Here is the design:\n{design_output}\n\nHere are the requirements: {requirements}",
        max_turns=MAX_TURNS,
    )
    code_output = code.final_output

    frontend = await Runner.run(
        frontend_engineer,
        f"Here is the design:\n{design_output}\n\nHere are the requirements: {requirements}",
        max_turns=MAX_TURNS,
    )
    frontend_output = frontend.final_output

    test = await Runner.run(
        test_engineer,
        f"Here is the design:\n{design_output}\n\nHere are the requirements: {requirements}",
        max_turns=MAX_TURNS,
    )
    test_output = test.final_output

    return {
        "design": design_output,
        "code": code_output,
        "frontend": frontend_output,
        "test": test_output,
    }
