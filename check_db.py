import asyncio
import asyncpg

async def test():
    for pwd in ['postgres', 'password', '', 'admin', '123456', 'root']:
        try:
            conn = await asyncpg.connect(
                host='localhost', port=5432,
                user='postgres', password=pwd,
                database='postgres'
            )
            await conn.close()
            print(f'OK! Password: "{pwd}"')
            return pwd
        except Exception as e:
            print(f'Password "{pwd}": {str(e)[:100]}')
    return None

asyncio.run(test())
