from db import db
import asyncio

async def run_test():
    try:
        result = await db.get_violation_reports(limit=1)
        print("Connected successfully ✔")
        print(result)
    except Exception as e:
        print("Connection failed ❌")
        print(e)

asyncio.run(run_test())
