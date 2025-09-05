import asyncio
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from dotenv import load_dotenv
import os
from .notifieragent import NotifierAgent
from .planneragent import PlannerAgent
from .userproxyagent import UserAgent

load_dotenv("model_client.env")

class Team():
    def __init__(self):
        self.__model_client = AzureOpenAIChatCompletionClient(
            model=os.getenv("MODEL"),
            azure_endpoint=os.getenv("AZURE_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_DEPLOYMENT"),
            api_version=os.getenv("API_VERSION"),
            api_key=os.getenv("API_KEY")
        )

        self.__agent1 = PlannerAgent(model_client=self.__model_client)
        self.__agent2 = NotifierAgent(model_client=self.__model_client)
        self.__user_agent = UserAgent()

        self.__termination = TextMentionTermination("TERMINATE")

        self.__team = SelectorGroupChat(
            [self.__agent1.get_agent(), self.__agent2.get_agent(), self.__user_agent.get_agent()],
            model_client=self.__model_client,
            termination_condition=self.__termination,
        )

        self._messages = None
        self._messages_loop = None  # Track the event loop for the queue
        self.__runner_task = None
        self.__started = False   # Track if first message started run_stream

    def initialize_queue(self):
        """No-op: queue will be initialized in async context."""
        self._messages = None
        self._messages_loop = None

    async def _ensure_queue(self):
        """Ensure the queue is bound to the current event loop."""
        current_loop = asyncio.get_running_loop()
        if self._messages is None or self._messages_loop != current_loop:
            self._messages = asyncio.Queue()
            self._messages_loop = current_loop

    async def _runner(self, first_query: str):
        try:
            async for msg in self.__team.run_stream(task=first_query):
                await self._messages.put(msg)
        except asyncio.CancelledError:
            pass

    async def send(self, user_text: str):
        await self._ensure_queue()
        if not self.__started:
            # First message starts run_stream
            self.__started = True
            self.__runner_task = asyncio.create_task(self._runner(user_text))
        else:
            # Later messages go to UserAgent
            await self.__user_agent.add_user_input(user_text)

    async def stream_responses(self):
        await self._ensure_queue()
        while True:
            msg = await self._messages.get()

            # Skip echo of user input
            if msg.source == "user":
                self._messages.task_done()
                continue

            if msg.type == "UserInputRequestedEvent":
                self._messages.task_done()
                break

            yield msg
            self._messages.task_done()