import asyncio
import json
from datetime import date, timedelta
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    print("\n TAABI Query System")
    print("─" * 40)
    print("Type 'exit' to quit\n")

    server_params = StdioServerParameters(
       command="/Users/dr.sinorabanker/Analytics_Bot/.venv/bin/python",
        args=["/Users/dr.sinorabanker/Analytics_Bot/server.py"],
        env={"PYTHONUNBUFFERED": "1"}
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            while True:
                query = input("Query: ").strip()

                if query.lower() in ["exit", "quit"]:
                    print("Goodbye!")
                    break

                if not query:
                    continue

                try:
                    result = await session.call_tool("ask_taabi", arguments={"query": query})

                    if hasattr(result, "content"):
                        content = result.content[0] if isinstance(result.content, list) else result.content
                        if hasattr(content, "text"):
                            data = json.loads(content.text)
                            if data.get("success"):
                                print(f"\n{data.get('result')}\n")
                            else:
                                print(f"\nError: {data.get('error')}\n")

                except Exception as e:
                    print(f"\nError: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())
