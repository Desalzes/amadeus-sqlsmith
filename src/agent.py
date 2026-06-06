import json

from a2a.server.tasks import TaskUpdater
from a2a.types import Message, TaskState, Part, TextPart
from a2a.utils import get_message_text, new_agent_text_message

from messenger import Messenger
from sqlsmith import SQLSmithController


class Agent:
    def __init__(self):
        self.messenger = Messenger()
        self.controller = SQLSmithController()

    async def run(self, message: Message, updater: TaskUpdater) -> None:
        """Implement your agent logic here.

        Args:
            message: The incoming message
            updater: Report progress (update_status) and results (add_artifact)

        Use self.messenger.talk_to_agent(message, url) to call other agents.
        """
        input_text = get_message_text(message)

        await updater.update_status(
            TaskState.working, new_agent_text_message("Solving SQL task...")
        )
        result = self.controller.solve(input_text)
        await updater.add_artifact(
            parts=[Part(root=TextPart(text=json.dumps(result, sort_keys=True)))],
            name="sqlsmith-result",
        )
