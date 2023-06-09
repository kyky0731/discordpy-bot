import discord
from discord.utils import get
import json
from keepalive import keep_alive
from discord import app_commands
import asyncio
import os
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    print("Ready!")

color = discord.Color.from_rgb(99, 127, 66)
@tree.command(name="logisland", description="Logs minutes in Nova Island in your activity.")
@discord.app_commands.describe(date="What is the date of your Island activity session? Format: mm/dd/yyyy", time="What is the time of your Island activity session? Format: XX:XX AM/PM EST.", minutes="Minutes spent at the Island in this session.")
async def logTime(interaction, date:str, time:str, minutes:int):
   id = str(interaction.user.id)
   with open("activity.json", "r", encoding='utf-8') as f:
      data = json.load(f)
   if id in data.keys():
      currentvisits = data[f"{id}"]["Island"]
      data[f"{id}"].update({"Island": currentvisits + int(minutes)})
   else:
      totaldict = {f"{id}": {"Sessions": int(minutes), "Visits": 0, "Island": 0, "Inactive": 0}}
      data.update(totaldict)
   with open("activity.json", "w", encoding='utf-8') as f:
      json.dump(data, f, indent=4, separators=(",",": "))
   await interaction.response.send_message(f"Successfully added {minutes} Island minutes to your activity record.")
@tree.command(name="logsession", description="Logs a training/interview session in your activity.")
@discord.app_commands.describe(date="What is the date of your session? Format: mm/dd/yyyy", time="What is the time of your session? EST time please! Format: XX:XX AM/PM EST.", assembly_type = "Was the session a Training or Interview?")
@discord.app_commands.choices(assembly_type=[
   discord.app_commands.Choice(name="Training Session", value=1),
   discord.app_commands.Choice(name="Interview Session", value=2)
])
async def logSession(interaction, date:str, time:str, assembly_type:discord.app_commands.Choice[int]):
   id = str(interaction.user.id)
   with open("activity.json", "r", encoding='utf-8') as f:
      data = json.load(f)
   if id in data.keys():
      currentvisits = data[f"{id}"]["Sessions"]
      data[f"{id}"].update({"Sessions": currentvisits + 1})
   else:
      totaldict = {f"{id}": {"Sessions": 1, "Visits": 0, "Island": 0, "Inactive": 0}}
      data.update(totaldict)
   with open("activity.json", "w", encoding='utf-8') as f:
      json.dump(data, f, indent=4, separators=(",",": "))
   await interaction.response.send_message(f"Successfully added the {time} {assembly_type.name} session on {date} to your activity record.")
@tree.command(name="logvisit", description="Logs a new alliance visit in your activity.")
@discord.app_commands.describe(affiliate_name="What is the name of the affiliate you visited? If someone visited us, type Nova Hotels.", date_time="What is the date and time that the visit occurred?")
async def logVisit(interaction, affiliate_name:str, date_time:str):
   id = str(interaction.user.id)
   with open("activity.json", "r", encoding='utf-8') as f:
      data = json.load(f)
   if id in data.keys():
      currentvisits = data[f"{id}"]["Visits"]
      data[f"{id}"].update({"Visits": currentvisits + 1})
   else:
      totaldict = {f"{id}": {"Sessions": 0, "Visits": 1, "Island": 0, "Inactive": 0}}
      data.update(totaldict)
   with open("activity.json", "w", encoding='utf-8') as f:
      json.dump(data, f, indent=4, separators=(",",": "))
   await interaction.response.send_message(f"Successfully added the alliance visit to {affiliate_name} at {date_time} to your activity record.")

   
@tree.command(name="resetactivity", description="Resets the activity for the next activity period.")
async def resetActivity(interaction):
   with open("activity.json", "r", encoding='utf-8') as f:
      data = json.load(f)
      new = {}
   with open("activity.json", "w", encoding='utf-8') as f:
      json.dump(new, f, indent=4, separators=(",",": "))
   await interaction.response.send_message("I have successfully reset the activity for the next period.", ephemeral=True)
@tree.command(name="activity", description="Checks the activity of the given user.")
@discord.app_commands.describe(user_id="What is the Discord User ID of the user you want to check?")
async def activityCheck(interaction, user_id:str):
   guild = interaction.user.guild
   user = user_id
   with open("activity.json", "r", encoding='utf-8') as f:
      data = json.load(f)
   if user in data.keys():
        sessions = data[user]["Sessions"]
        island = data[user]["Island"]
        visits = data[user]["Visits"]
        ina = data[user]["Inactive"]
        check = get(guild.emojis, name="NovaCheck")
        warning = get(guild.emojis, name="NovaWarning")
        no = get(guild.emojis, name="NovaCross")
        user = await guild.fetch_member(int(user_id))
        if ina == 0:
            ina = "No."
            if sessions > 0 or island > 0 or visits > 0:
                emoji = warning
                woah = "In Progress!"
            if sessions >= 2: 
                if island >= 60:
                    if visits >= 1:
                        emoji = check
                        woah = "Completed!"
            else:
                emoji = no
                woah = "Not yet started."
            user = await guild.fetch_member(int(interaction.user.id))
            embed = discord.Embed(description=f"""**Island Time (Minutes)** 
{island} / 60 minute(s)
**Sessions** 
{sessions} / 2 session(s)
**Alliance Visits** 
{visits} / 1 visit(s)
**Requirements status** 
{emoji} {woah}
**Inactivity Notice?**
{ina}""", color=color)
            pfp = user.avatar
            embed.set_author(name=f"{user}", icon_url=pfp)
            embed.set_footer(text="Nova Relations Assistant | Developed by Jake (BearxTeqrs) and Kyle (DoctorStrange1368) | Version 1.")
            await interaction.response.send_message(embed=embed)
        if ina == 0.5:
            ina = "Yes, half requirements."
            if sessions > 0 or island > 0 or visits > 0:
                emoji = warning
                woah = "In Progress!"
            elif sessions >= 1: 
                if island >= 30:
                    if visits >= 1:
                        emoji = check
                        woah = "Completed!"
            else:
                emoji = no
                woah = "Not yet started."
            user = await guild.fetch_member(int(interaction.user.id))
            embed = discord.Embed(description=f"""**Island Time (Minutes)** 
{island} / 30 minutes
**Sessions** 
{sessions} / 1 session(s)
**Alliance Visits** 
{visits} / 0 visit(s)
**Requirements status** 
{emoji} {woah}
**Inactivity Notice?**
{ina}""", color=color)
            pfp = user.avatar
            embed.set_author(name=f"{user}", icon_url=pfp)
            embed.set_footer(text="Nova Relations Assistant | Developed by Jake (BearxTeqrs) and Kyle (DoctorStrange1368) | Version 1.")
            await interaction.response.send_message(embed=embed)
        if ina == 1:
            ina = "Yes, full excusal."
            embed = discord.Embed(description=f"""**Island Time (Minutes)** 
{island} / 0 minute(s)
**Sessions** 
{sessions} / 0 session(s)
**Alliance Visits** 
{visits} / 0 visit(s)
**Requirements status** 
{warning} Excused!
**Inactivity Notice?**
{ina}""", color=color)
            embed.set_footer(text="Nova Relations Assistant | Developed by Jake (BearxTeqrs) and Kyle (DoctorStrange1368) | Version 1.")
            user = await guild.fetch_member(int(interaction.user.id))
            pfp = user.avatar
            embed.set_author(name=f"{user}", icon_url=pfp)
            await interaction.response.send_message(embed=embed)
   else:
        no = get(guild.emojis, name="NovaCross")
        user = await guild.fetch_member(int(user_id))
        embed = discord.Embed(description=f"""**Island Time (Minutes)** 
0 / 60 minute(s)
**Sessions** 
0 / 2 session(s)
**Alliance Visits** 
0 / 1 visit(s)
**Requirements status** 
{no} Not yet started.
**Inactivity Notice?**
No.""", color=color)
        embed.set_footer(text="Nova Relations Assistant | Developed by Jake (BearxTeqrs) and Kyle (DoctorStrange1368) | Version 1.")
        pfp = user.avatar
        embed.set_author(name=f"{user}", icon_url=pfp)
        await interaction.response.send_message(embed=embed)
@tree.command(name="ping", description="Ping pong! What is the client latency?")
async def ping(interaction):
   latency = client.latency * 1000
   latency = round(latency, 2)
   await interaction.response.send_message(f"🏓 Pong! `Latency: {latency}ms`", ephemeral=True)
@tree.command(name="spamping", description="😏😏😏 You know what this is.")
@discord.app_commands.describe(userid="Who to spam ping...")
async def spam(interaction, userid:str):
   listofids = [735954466368389121, 796465682408800276]
   user = int(interaction.user.id)
   guild = interaction.user.guild
   if user in listofids:
      user = await guild.fetch_member(int(userid))
      await interaction.response.send_message(f"I have spam pinged the user with the ID {userid} 10 times.", ephemeral=True)
      await user.send(user.mention)
      await user.send(user.mention)
      await user.send(user.mention)
      await asyncio.sleep(1)
      await user.send(user.mention)
      await user.send(user.mention)
      await user.send(user.mention)
      await asyncio.sleep(1)
      await user.send(user.mention)
      await user.send(user.mention)
      await user.send(user.mention)
      await asyncio.sleep(1)
      await user.send(user.mention)
   else:
      await interaction.response.send_message("Do it yourself you lazy bum.", ephemeral=True)
@tree.command(name="say", description="Send a message through the bot in a channel.")
@discord.app_commands.describe(channel_id="What channel do you want the bot to send the message in?", message="What message do you want the bot to send?")
async def sendMessage(interaction, channel_id:str, message:str):
   listofids = [735954466368389121, 796465682408800276]
   user = int(interaction.user.id)
   guild = interaction.user.guild
   if user in listofids:
      try:
         channelID = int(channel_id)
         channel = await guild.fetch_channel(channelID)
         embed = discord.Embed(description=f"""{message}""")
         embed.set_footer(text="Nova Relations Assistant | Developed by Jake (BearxTeqrs) and Kyle (DoctorStrange1368) | Version 1.")
         pfp = interaction.user.avatar
         embed.set_author(icon_url=pfp, name=f"{interaction.user}")
         await channel.send(embed=embed)
         await interaction.response.send_message(f"I have sent your message to {channel.mention}. Check it out!", ephemeral=True)
      except:
         await interaction.response.send_message("That is not a valid channel ID. Please try again.", ephemeral=True)
   else:
      await interaction.response.send_message("You do not have that permission!", ephemeral=True)

@tree.command(name="inactivenote", description="Puts someone on inactivity notice.")
@discord.app_commands.describe(user="The Discord User ID of the user going on IN.", requirements="How much reqs?")
@discord.app_commands.choices(requirements=[
   discord.app_commands.Choice(name="Complete all requirements.", value=1),
   discord.app_commands.Choice(name="Complete half requirements.", value=2),
   discord.app_commands.Choice(name="Complete no Requirements.", value=3)
])
async def inactivity_notice(interaction, user:str, requirements:discord.app_commands.Choice[int]):
    listofids = [735954466368389121, 796465682408800276]
    user = int(interaction.user.id)
    guild = interaction.user.guild
    if user in listofids:
        totaldict = {f"{user}": {"Sessions": 0, "Visits": 0, "Island": 0, "Inactive": 0}}
        with open("activity.json", "r", encoding='utf-8') as f:
            data = json.load(f)
        if user not in data.keys():
            data.update(totaldict)
        if requirements.value == 1: 
            data[f"{user}"].update({"Inactive": 0})
        if requirements.value == 2:
            data[f"{user}"].update({"Inactive": 0.5})
        if requirements.value == 3:
            data[f"{user}"].update({"Inactive": 1})
        
        with open("activity.json", "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4, separators=(",",": "))
        await interaction.response.send_message(f"I have put the user with the ID of {user} on Inactivity Notice.", ephemeral=True)
    else:
       await interaction.response.send_message("You do not have permission to run this command!", ephemeral=True)
      
@tree.command(name="myactivity", description="Shows your activity logging.")
async def checkactivity(interaction):
   guild = interaction.user.guild
   user = str(interaction.user.id)
   with open("activity.json", "r", encoding='utf-8') as f:
      data = json.load(f)
   if user in data.keys():
        sessions = data[user]["Sessions"]
        island = data[user]["Island"]
        visits = data[user]["Visits"]
        ina = data[user]["Inactive"]
        check = get(guild.emojis, name="NovaCheck")
        warning = get(guild.emojis, name="NovaWarning")
        no = get(guild.emojis, name="NovaCross")
        if ina == 0:
            ina = "No."
            if sessions >= 1:
                emoji = warning
                woah = "In Progress!"
            elif visits >= 1:
               emoji = warning
               woah = "In Progress!"
            elif island >= 1:
               emoji = warning
               woah = "In Progress!"
            if sessions >= 2: 
                print("1")
                if island >= 60:
                    print("2")
                    if visits >= 1:
                        print("???")
                        emoji = check
                        woah = "Completed!"
            elif sessions == 0:
                emoji = no
                woah = "Not yet started."
            user = await guild.fetch_member(int(interaction.user.id))
            embed = discord.Embed(description=f"""**Island Time (Minutes)** 
{island} / 60 minute(s)
**Sessions** 
{sessions} / 2 session(s)
**Alliance Visits** 
{visits} / 1 visit(s)
**Requirements status** 
{emoji} {woah}
**Inactivity Notice?**
{ina}""", color=color)
            pfp = user.avatar
            embed.set_author(name=f"{user}", icon_url=pfp)
            embed.set_footer(text="Nova Relations Assistant | Developed by Jake (BearxTeqrs) and Kyle (DoctorStrange1368) | Version 1.")
            await interaction.response.send_message(embed=embed)
        if ina == 0.5:
            ina = "Yes, half requirements."
            if sessions > 0:
                emoji = warning
                woah = "In Progress!"
            elif island > 0:
               emoji = warning
               woah = "In Progress!"
            elif visits > 0:
               emoji = warning
               woah = "In Progress!"
            if sessions >= 1: 
                if island >= 30:
                    if visits >= 1:
                        emoji = check
                        woah = "Completed!"
            else:
                emoji = no
                woah = "Not yet started."
            user = await guild.fetch_member(int(interaction.user.id))
            embed = discord.Embed(description=f"""**Island Time (Minutes)** 
{island} / 30 minute(s)
**Sessions** 
{sessions} / 1 session(s)
**Alliance Visits** 
{visits} / 0 visit(s)
**Requirements status** 
{emoji} {woah}
**Inactivity Notice?**
{ina}""", color=color)
            pfp = user.avatar
            embed.set_author(name=f"{user}", icon_url=pfp)
            embed.set_footer(text="Nova Relations Assistant | Developed by Jake (BearxTeqrs) and Kyle (DoctorStrange1368) | Version 1.")
            await interaction.response.send_message(embed=embed)
        if ina == 1:
            ina = "Yes, full excusal."
            embed = discord.Embed(description=f"""**Island Time (Minutes)** 
{island} / 0 minute(s)
**Sessions** 
{sessions} / 0 session(s)
**Alliance Visits** 
{visits} / 0 visit(s)
**Requirements status** 
{warning} Excused!
**Inactivity Notice?**
{ina}""", color=color)
            user = await guild.fetch_member(int(interaction.user.id))
            pfp = user.avatar
            embed.set_author(name=f"{user}", icon_url=pfp)
            embed.set_footer(text="Nova Relations Assistant | Developed by Jake (BearxTeqrs) and Kyle (DoctorStrange1368) | Version 1.")
            await interaction.response.send_message(embed=embed)
   else:
        no = get(guild.emojis, name="NovaCross")
        user = await guild.fetch_member(int(interaction.user.id))
        embed = discord.Embed(title=f"Displaying {user}'s Activity Report", description=f"""**Island Time (Minutes)** 
0 / 60 minute(s)
**Sessions** 
0 / 2 session(s)
**Alliance Visits** 
0 / 1 visit(s)
**Requirements status** 
{no} Not yet started.
**Inactivity Notice?**
No.""", color=color)
        embed.set_footer(text="Nova Relations Assistant | Developed by Jake (BearxTeqrs) and Kyle (DoctorStrange1368) | Version 1.")
        user = await guild.fetch_member(int(interaction.user.id))
        pfp = user.avatar
        embed.set_author(name=f"{user}", icon_url=pfp)
        await interaction.response.send_message(embed=embed)


@tree.command(name="removeally", description="Removes an alliance from the #nova-affiliates.")
@discord.app_commands.describe(name="Full name of the alliance.", confirmation="Type 'Yes' to confirm.")
async def delalliance(interaction, name:str, confirmation:str):
   guild = interaction.user.guild
   if confirmation.lower() == "yes":
      with open("links.json", "r", encoding='utf-8') as f:
        data = json.load(f)
        if str(name) not in data.keys():
            await interaction.response.send_message("This alliance does not exist. Add it by stating /newalliance!", ephemeral=True)
        else:
            channel = data[f"{name}"]["Channel"]
            channel = await guild.fetch_channel(int(channel))
            info = data[f"{name}"]["Message"]
            msg = await channel.fetch_message(int(info))
            await msg.delete()
            await interaction.response.send_message(f"I have successfully removed {name} as an alliance.", ephemeral=True)
@tree.command(name="editalliance", description="Edits alliance information.")
async def editalliance(interaction, name:str, newname:str, image_link:str, roblox_link:str, discord_link:str, nova_rep_1:str, nova_rep_2:str, their_rep_1:str, their_rep_2:str):
    guild = interaction.user.guild
    with open("links.json", "r", encoding='utf-8') as f:
        data = json.load(f)
    if str(name) not in data.keys():
       await interaction.response.send_message("This alliance does not exist. Add it by stating /newalliance!", ephemeral=True)
    else:
       channel = data[f"{name}"]["Channel"]
       channel = await guild.fetch_channel(int(channel))
       info = data[f"{name}"]["Message"]
       msg = await channel.fetch_message(int(info))
       embed = discord.Embed(title=f"{newname}", description=f"""** [Roblox]({roblox_link}) **
** [Discord]({discord_link}) **

__ Our Representatives __
{nova_rep_1}
{nova_rep_2}

__ Their Representatives __
{their_rep_1}
{their_rep_2}""", color=color)
    embed.set_thumbnail(url=image_link)
    embed.set_footer(text="Nova Relations Assistant | Developed by Jake (BearxTeqrs) and Kyle (DoctorStrange1368) | Version 1.")
    await msg.edit(embed=embed)
    await interaction.response.send_message("Succesfully updated alliance.", ephemeral=True)
@tree.command(name="newalliance", description="Lists a new alliance.")
@discord.app_commands.describe(name="The full group name of the alliance.", image_link="The image URL of the group icon.", roblox_link="The full Roblox link of the group, starting with https://roblox.com/groups.", discord_link="An non-expiring Discord Link to their server. Starts with https://discord.gg/.", nova_rep_1="The first representative from our PR. Format: [Roblox Username] | Discord Username & Tag | Discord ID.", nova_rep_2="The second representative from our PR. Format: [Roblox Username] | Discord Username & Tag | Discord ID.", their_rep_1="The firstrepresentative from their PR. Format: [Roblox Username] | Discord Username & Tag | Discord ID.", their_rep_2="The second representative from their PR. Format: [Roblox Username] | Discord Username & Tag | Discord ID.")
async def newalliance(interaction, name:str, image_link:str, roblox_link:str, discord_link:str, nova_rep_1:str, nova_rep_2:str, their_rep_1:str, their_rep_2:str):
   guild = interaction.user.guild
   guildid = guild.id
   embed = discord.Embed(title=f"{name}", description=f"""** [Roblox]({roblox_link}) **
** [Discord]({discord_link}) **

__ Our Representatives __
{nova_rep_1}
{nova_rep_2}

__ Their Representatives __
{their_rep_1}
{their_rep_2}""", color=color)
   embed.set_footer(text="Nova Relations Assistant | Developed by Jake (BearxTeqrs) and Kyle (DoctorStrange1368) | Version 1.")
   embed.set_thumbnail(url=image_link)
   guild = await client.fetch_guild(764599045091098644)
   channel = await guild.fetch_channel(1027491609505443873)
   await channel.send(embed=embed)
   await interaction.response.send_message(f"I have added the new alliance in {channel.mention}! Go check it out!", ephemeral=True)
   x = await interaction.original_response()
   x = x.jump_url
   info = x.split(f"https://discord.com/channels/{guildid}")[1]
   x = info.split("/")[1]
   print(x)
   y = info.split("/")[2]
   print(x)
   print(y)
   with open("links.json", "r", encoding='utf-8') as f:
     data = json.load(f)
     data.update({f"{name}": {"Channel": f"{x}", "Message": f"{y}"}})
   with open("links.json", "w", encoding='utf-8') as f:
     json.dump(data, f, indent=4, separators=(",",": "))

@tree.command(name="activitystrike", description="Strikes a user for inactivity.")
@discord.app_commands.describe(user_id="The Discord User ID of the user you wish to strike for activity.", activity_link="The link to the activity spreadsheet.", activity_period="The activity period that they were inactive in.", strike_number="Which strike is this for them?")
async def activitystrike(interaction, user_id:str, activity_link:str, activity_period:str, strike_number:int):
    listofids = [735954466368389121, 796465682408800276]
    user = int(interaction.user.id)
    guild = interaction.user.guild
    warning = discord.utils.get(guild.emojis, name="NovaWarning")
    member = discord.utils.get(guild.emojis, name="PR_Member")
    if user in listofids:
        asdf = await guild.fetch_member(int(user_id))
        embed = discord.Embed(title=f"__Public Relations | Department Strike {strike_number}__", description=f"""Greetings, {asdf.mention}!

We hope this message finds you well. We are writing to inform you that a strike has been issued to you in the Public Relations Department. **The reason for this strike is your failure to meet the Nova Public Relations Department requirements during the period of {activity_period}.**

> {warning} We kindly remind you that this is your first strike, and it serves as a formal warning. It is important to note that accumulating three strikes will result in your removal from the department. To provide transparency and evidence of this strike, we have included a link to the supporting documentation.

🔗[|Activity Sheet|]({activity_link})

We understand that you may have questions or concerns regarding this strike, and we encourage you to reach out to us without hesitation. We are here to address any queries or provide further clarification on the matter. 

*Best regards,
**{member} BearxTeqrs.**
Head of the Public Relations Department.*""")
        embed.set_footer(text="Nova Relations Assistant | Developed by Jake (BearxTeqrs) and Kyle (DoctorStrange1368) | Version 1.")
        await asdf.send(embed=embed)
        await interaction.response.send_message(f"Successfully activity-striked the user with the ID of {user_id}.", ephemeral=True)

@tree.command(name="warn", description="Warns a user.")
@discord.app_commands.describe(user_id="The Discord User ID of the individual you want to warn.", reason="The reason you are warning them.")
async def warn(interaction, user_id:str, reason:str):
  listofids = [735954466368389121, 796465682408800276]
  user = int(interaction.user.id)
  guild = interaction.user.guild
  warning = discord.utils.get(guild.emojis, name="NovaWarning")
  member = discord.utils.get(guild.emojis, name="PR_Member")
  if user in listofids:
    asdf = await guild.fetch_member(int(user_id))
    embed = discord.Embed(title="Nova Hotels Public Relations Department | Warning", description=f"""Greetings, {asdf.mention}.

[Insert warn format]
Reason: {reason}""", color=color)
    embed.set_footer(text="Nova Relations Assistant | Developed by Jake (BearxTeqrs) and Kyle (DoctorStrange1368) | Version 1.")
    await asdf.send(embed=embed)
    x = await interaction.response.send_message(f"Successfully warned user with ID {user_id}.", ephemeral=True)
    
@tree.command(name="depremove", description="Removes a user from the Public Relations Department.")
@discord.app_commands.describe(user_id="The Discord User ID of the individual you want to remove.", reason="The reason you are removing them.")
async def depremove(interaction, user_id:str, reason:str):
  listofids = [735954466368389121, 796465682408800276]
  user = int(interaction.user.id)
  guild = interaction.user.guild
  warning = discord.utils.get(guild.emojis, name="NovaWarning")
  member = discord.utils.get(guild.emojis, name="PR_Member")
  if user in listofids:
    asdf = await guild.fetch_member(int(user_id))
    embed = discord.Embed(title="Public Relations | Department Removal", description=f"""Greetings, {asdf.mention}!

We hope this message finds you well. We would like to address a matter concerning your involvement in the Public Relations department. We regret to inform you that, after careful consideration and evaluation of your performance and contribution to the Public Relations team, a decision has been made to remove you from your current role within the department, effective immediately.

We want to assure you that this decision was not taken lightly, and we recognize the value you brought during your time in the Public Relations team. Although this removal may seem final, we encourage you to view it as an opportunity for growth and self-reflection. It is possible to reapply for a position in the future should you regain the necessary dedication and availability.

> {warning} If you believe this decision is unfair or if you have any questions, we kindly request that you reach out to any Senior+ member of the Public Relations team. They will be more than willing to provide clarification and address any concerns you may have.
We thank you for your past contributions and wish you the best in your future! 

*Sincerely,
**{member} BearxTeqrs**,
Head of the Public Relations Department.*""", color=color)
    embed.set_footer(text="Nova Relations Assistant | Developed by Jake (BearxTeqrs) and Kyle (DoctorStrange1368) | Version 1.")
    await asdf.send(embed=embed)
    role = get(guild.roles, id=1087737259907883109)
    role2 = get(guild.roles, id=874073433158352978)
    await asdf.edit(roles=[role, role2])
    await interaction.response.send_message(f"Successfully removed user with ID {user_id} from the Public Relations Department.", ephemeral=True)
@tree.command(name="strike", description="Strikes a user.")
@discord.app_commands.describe(user_id="The Discord User ID of the individual you want to strike.", strike_number="Which strike number is this for them?", reason="The reason you are striking them.")
async def strike(interaction, user_id:str, strike_number:int, reason:str, proof: discord.Attachment):
  listofids = [735954466368389121, 796465682408800276]
  user = int(interaction.user.id)
  guild = interaction.user.guild
  warning = discord.utils.get(guild.emojis, name="NovaWarning")
  member = discord.utils.get(guild.emojis, name="PR_Member")
  if user in listofids:
    asdf = await guild.fetch_member(int(user_id))
    embed = discord.Embed(title=f"Public Relations | Department Strike {strike_number}", description=f"""Greetings, {asdf.mention}!

We hope this message finds you well. We are writing to inform you that a strike has been issued to you in the Public Relations Department. **The reason for this strike is due to {reason}.**

> {warning} We kindly remind you that you have accumulated {strike_number} strikes, and these serve as a formal warning. It is important to note that accumulating three strikes will result in your removal from the department. To provide transparency and evidence of this strike, we have included a link to the supporting documentation.

🔗|Evidence attached below.|

We understand that you may have questions or concerns regarding this strike, and we encourage you to reach out to us without hesitation. We are here to address any queries or provide further clarification on the matter. 

*Best regards,
**{member} BearxTeqrs**.
Head of the Public Relations Department.*""", color=color)
    embed.set_image(url=proof)
    embed.set_footer(text="Nova Relations Assistant | Developed by Jake (BearxTeqrs) and Kyle (DoctorStrange1368) | Version 1.")
    await asdf.send(embed=embed)
    await interaction.response.send_message(f"Successfully striked user with ID {user_id}.", ephemeral=True)

keep_alive()
client.run(os.getenviron["DISCORD_TOKEN"])
