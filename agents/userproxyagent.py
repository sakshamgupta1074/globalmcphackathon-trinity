import asyncio
from autogen_agentchat.agents import UserProxyAgent

class UserAgent:
    def __init__(self):
        self.__user_input_queue = asyncio.Queue()
        self.TERMINATION_TOKEN = "TERMINATE"

    async def add_user_input(self, user_input: str):
        await self.__user_input_queue.put(user_input)

    async def __user_proxy_input_func(self, query: str = "", cancellation_token: any = None) -> str:
        if cancellation_token:
            cancellation_token.add_callback(lambda: self.__handle_cancel())
        try:
            user_input = await self.__user_input_queue.get()
        except asyncio.CancelledError:
            return self.TERMINATION_TOKEN
        return user_input
        
    def __handle_cancel(self):
        try:
            self.__user_input_queue.put_nowait(self.TERMINATION_TOKEN)
        except Exception:
            pass

    def get_agent(self):
        return UserProxyAgent(
            name="userproxy",
            input_func=self.__user_proxy_input_func,
        )
    
    def reset_queue(self):
        self.__user_input_queue = asyncio.Queue()