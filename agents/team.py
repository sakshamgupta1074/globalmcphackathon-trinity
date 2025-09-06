import asyncio
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from dotenv import load_dotenv
import os
from .notifieragent import NotifierAgent
from .planneragent import PlannerAgent

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

        self.__termination = TextMentionTermination("TERMINATE")

        # No persistent chat/team state; each request creates its own group chat

    def initialize_queue(self):
        """No-op kept for backward compatibility."""
        return

    async def run_once(self, user_text: str):
        # Construct a fresh team bound to the current request's event loop
        agent1 = PlannerAgent(model_client=self.__model_client).get_agent()
        agent2 = NotifierAgent(model_client=self.__model_client).get_agent()
        team = SelectorGroupChat(
            [agent1, agent2],
            model_client=self.__model_client,
            termination_condition=self.__termination,
        )
        async for msg in team.run_stream(task=user_text):
            yield msg

    async def shutdown(self):
        return