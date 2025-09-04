import asyncio
from autogen_agentchat.agents import UserProxyAgent

class UserAgent:
    def __init__(self):
        self.__user_input_queue = asyncio.Queue()

    async def add_user_input(self, user_input: str):
        await self.__user_input_queue.put(user_input)

    async def __user_proxy_input_func(self, query: str = "", cancellation_token: any = None) -> str:
        if cancellation_token:
            cancellation_token.add_callback(lambda: self.__handle_cancel())
        user_input = await self.__user_input_queue.get()
        return user_input
        
    def __handle_cancel(self):
        self.reset_queue()

    def get_agent(self):
        return UserProxyAgent(
            name="userproxy",
            input_func=self.__user_proxy_input_func,
        )
    
    def reset_queue(self):
        self.__user_input_queue = asyncio.Queue()