from autogen_agentchat.agents import AssistantAgent

class PlannerAgent:
    def __init__(self, model_client):
        self.__model_client = model_client

    def get_agent(self):
        return AssistantAgent(
            name="planneragent",
            description="An agent that creates calendar events from extracted tasks.",
            model_client=self.__model_client,
            system_message="You are a planner expert. You create calendar events from tasks accurately.",
        )