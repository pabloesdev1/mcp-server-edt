from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from mcp.types import CallToolResult, GetPromptResult
import asyncio

transport = StreamableHttpTransport(
    url="https://mcp-server-demo1.fastmcp.app/mcp",
    headers={"Authorization": "Bearer my-secret-token"},
)

client = Client(transport=transport)

async def test_call_tool(name: str):
    async with client:
        result = await client.call_tool(
            name,
            {
                "to": "pabloespanab@outlook.com",
                "subject": "Test Email",
                "body": "This is a test email sent from the MCP server."
            }
        )
        return result

# tool_response: CallToolResult = asyncio.run(test_call_tool("send_email"))
# print("Tool Response:", tool_response.structured_content)


async def test_get_prompt():
    async with client:
        result = await client.get_prompt("client_info", {"message": "Hola, mi nombre es Pablo y mi email es pabloespanab@outlook.com"})
        return result
    
prompt_response: GetPromptResult = asyncio.run(test_get_prompt())
print("Prompt Response:", prompt_response.messages[0].content.text)