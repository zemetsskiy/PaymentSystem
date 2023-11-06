import discord
import asyncio

from config import TOKEN, GUILD_ID, ROLE_NAME, MEMBER_ID

TOKEN = TOKEN
GUILD_ID = GUILD_ID
ROLE_NAME = ROLE_NAME
MEMBER_ID = MEMBER_ID

async def assign_role_to_user(bot_token, guild_id, member_id, role_name):
    client = discord.Client()
    async with client:
        await client.login(bot_token)
        guild = await client.fetch_guild(guild_id)
        if not guild:
            print(f"Server with ID {guild_id} not found.")
            return

        member = await guild.fetch_member(member_id)
        if not member:
            print(f"User with ID {member_id} not found on server '{guild.name}'.")
            return

        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            print(f"Role '{role_name}' not found on server '{guild.name}'.")
            return

        await member.add_roles(role)
        print(f"Role '{role_name}' has been assigned to user '{member.display_name}' on server '{guild.name}'.")

if __name__ == '__main__':
    asyncio.run(assign_role_to_user(TOKEN, GUILD_ID, MEMBER_ID, ROLE_NAME))
