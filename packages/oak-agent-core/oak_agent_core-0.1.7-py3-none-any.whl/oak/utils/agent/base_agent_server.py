import logging
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Any, Dict, Optional, List
from langchain.agents import initialize_agent, AgentType

from oak.utils.decorators.skill import get_all_skills_info

logger = logging.getLogger(__name__)

class A2AMessage(BaseModel):
    user_id: Optional[str] = None  
    content: Dict[str, Any]
    message_id: str
    conversation_id: str

class BaseAgentServer:
    def __init__(
        self,
        agent_name: str,
        description: str,
        version: str,
        url_base: str,
        llm,
        tools: List,
        capabilities: Optional[Dict[str, Any]] = None,
    ):
        self.agent_name = agent_name
        self.description = description
        self.version = version
        self.url_base = url_base.rstrip("/")
        self.llm = llm
        self.tools = tools
        self.capabilities = capabilities or {}

        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
        )

        self.app = FastAPI()
        self.app.post("/a2a/message")(self.handle_message)
        self.app.get("/agent.json")(self.get_agent_card)

    async def handle_message(self, msg: A2AMessage):
        try:
            user_query = msg.content.get("text", "")
            user_id = msg.content.get("user_id") or msg.user_id or ""

            if not user_query:
                return {
                    "id": msg.message_id,
                    "conversation_id": msg.conversation_id,
                    "content": {
                        "type": "text",
                        "text": "No query text found in message content."
                    },
                    "role": "agent"
                }

            logger.info(f"Handling message for user_id={user_id}, query={user_query}")

            input_payload = {
                "user_id": user_id,
                "input": user_query,
            }

            raw_result = self.agent.invoke(input_payload)

            # Attempt to detect tool used and output type for formatting
            # Example assumes agent returns string; extend as per actual usage
            response_content = {
                "type": "text",
                "text": raw_result,
            }

            # If you have access to tool or output_type from context, adjust content type here

            return {
                "id": msg.message_id,
                "conversation_id": msg.conversation_id,
                "content": response_content,
                "role": "agent"
            }

        except Exception as e:
            logger.error(f"Failed to handle A2A message: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Agent error: {e}")

    def get_agent_card(self):
        return {
            "name": self.agent_name,
            "description": self.description,
            "version": self.version,
            "url": f"{self.url_base}/a2a/message",
            "skills": self._get_skills_info(),
            "capabilities": self.capabilities,
        }

    def _get_skills_info(self):
        return get_all_skills_info()

    def run(self, host: str = "0.0.0.0", port: int = 8001, **uvicorn_kwargs):
        import uvicorn
        logger.info(f"Starting agent server {self.agent_name} on port {port}")
        uvicorn.run(self.app, host=host, port=port, **uvicorn_kwargs)
