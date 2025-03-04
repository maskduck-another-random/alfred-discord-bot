import assets
import External_functions as ef
from nextcord.ext import commands

# Use nextcord.slash_command()

def requirements():
    return []

class Automoderate(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def moderation_rules(self, ctx):
        a = await ctx.guild.fetch_automod_rules()
        embeds = []
        for i in a:
            embed = ef.cembed(
                title=i.name, 
                description=f"Enabled: {i.enabled}", 
                color=self.client.re[8],
                author = i.creator
            )
            embeds.append(embed)
        if not embeds:
            return await ctx.send("Empty")
        await assets.pa(ctx, embeds)


def setup(client,**i):
    client.add_cog(Automoderate(client,**i))
