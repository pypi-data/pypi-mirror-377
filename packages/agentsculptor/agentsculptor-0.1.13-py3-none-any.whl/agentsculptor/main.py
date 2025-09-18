from agentsculptor.agent.planner import PlannerAgent
from agentsculptor.agent.loop import AgentLoop
from agentsculptor.tools.prepare_context import prepare_context
import sys
from agentsculptor.utils.logging import setup_logging, get_logger

setup_logging("DEBUG")
logger = get_logger()


def cli_agent(project_path, user_request):
    context = prepare_context(project_path)
    planner = PlannerAgent()
    loop = AgentLoop(planner, context, user_request, project_path)  # ✅ Pass project_path here
    loop.run()

def main():  # <-- wrapper for console_scripts
    if len(sys.argv) < 3:
        logger.info("[INFO]: agentsculptor-cli <project_path> '<user_request>'")
        sys.exit(1)
    project_path = sys.argv[1]
    user_request = sys.argv[2]
    cli_agent(project_path, user_request)
