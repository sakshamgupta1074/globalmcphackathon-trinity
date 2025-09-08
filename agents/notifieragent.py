from autogen_agentchat.agents import AssistantAgent

class NotifierAgent:
    def __init__(self, model_client):
        self.__model_client = model_client

    def notifier_tool(self, task: str) -> str:
        # Simulate that the user doesnt have permission to send notifications
        return f"Failed to send notification for task: '{task}'. User does not have permission."

    def get_agent(self):
        return AssistantAgent(
            name="notifieragent",
            description="An agent that sends reminders via Slack, SMS, or email.",
            model_client=self.__model_client,
            tools=[self.notifier_tool],
            system_message=(
                "You are a notifier expert. You send reminders via Slack, SMS, or email accurately. "
                "ALWAYS use the notifier_tool for any type of query related to sending notifications or reminders. DONOT respond directly to the user without using the tool. "
                # "When you have completed your response, append the exact token 'TERMINATE'."
            ),
        )