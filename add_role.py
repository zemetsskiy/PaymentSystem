import discord
from logger import logging as logger



async def assign_role_to_user(bot_token, guild_id, MEMBER_NAME, role_name):
    intents = discord.Intents.default()
    intents.members = True

    client = discord.Client(intents=intents)
    async with client:
        await client.login(bot_token)
        guild = await client.fetch_guild(guild_id)
        if not guild:
            logger.info(f"Server with ID {guild_id} not found.")
            return

        member_id = 0

        async for member in guild.fetch_members(limit=1000):
            if member.name == MEMBER_NAME:
                member_id = member.id

        member = await guild.fetch_member(member_id)
        if not member:
            logger.info(f"User with ID {member_id} not found on server '{guild.name}'.")
            return

        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            logger.info(f"Role '{role_name}' not found on server '{guild.name}'.")
            return

        await member.add_roles(role)
        logger.info(f"Role '{role_name}' has been assigned to user '{member.display_name}' on server '{guild.name}'.")