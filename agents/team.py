import asyncio
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination, TextMessageTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from dotenv import load_dotenv
import os
from .notifieragent import NotifierAgent
from .planneragent import PlannerAgent
from .userproxyagent import UserAgent
import streamlit as st

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

        self._messages = asyncio.Queue()
        self.__runner_task = None
        self.__started = False   # track if first message started run_stream

    async def _runner(self, first_query: str):
        try:
            async for msg in self.__team.run_stream(task=first_query):
                await self._messages.put(msg)
        except asyncio.CancelledError:
            pass

    async def send(self, user_text: str):
        if not self.__started:
            # first message starts run_stream
            self.__started = True
            self.__runner_task = asyncio.create_task(self._runner(user_text))
        else:
            # later messages go to UserAgent
            await self.__user_agent.add_user_input(user_text)

    async def stream_responses(self):
        while True:
            msg = await self._messages.get()

            # skip echo of user input
            if msg.source == "user":
                continue

            if msg.type == "UserInputRequestedEvent":
                break
            yield msg