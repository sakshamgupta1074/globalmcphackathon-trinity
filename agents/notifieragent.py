from autogen_agentchat.agents import AssistantAgent

class NotifierAgent:
    def __init__(self, model_client):
        self.__model_client = model_client

    def get_agent(self):
        return AssistantAgent(
            name="notifieragent",
            description="An agent that sends reminders via Slack, SMS, or email.",
            model_client=self.__model_client,
            system_message="You are a notifier expert. You send reminders via Slack, SMS, or email accurately.",
        )