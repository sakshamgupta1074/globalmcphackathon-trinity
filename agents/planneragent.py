from autogen_agentchat.agents import AssistantAgent

class PlannerAgent:
    def __init__(self, model_client,scopes:list=None):
        self.__model_client = model_client
        self.__scopes = scopes

    def planner_tool(self, task: str) -> str:
        if "calendar.write" not in self.__scopes:
            return f"Failed to create calendar event for task: '{task}'. User does not have permission to create calendar events."
        return f"Successfully created calendar event for task: '{task}'."

    def get_agent(self):
        return AssistantAgent(
            name="planneragent",
            description="An agent that creates calendar events from extracted tasks.",
            model_client=self.__model_client,
            tools=[self.planner_tool],
            system_message=(
                "You are a planner expert. You create calendar events from tasks accurately. "
                "ALWAYS use the planner_tool for any type of query related to scheduling or calendar events. DONOT respond directly to the user without using the tool. "
                # "When you have completed your response, append the exact token 'TERMINATE'."
            ),
        )