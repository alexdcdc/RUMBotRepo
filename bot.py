import discord
from discord.utils import get
import asyncio
import os
import random
import collections
import datetime
import math
import traceback
import inspect
from discord.ext import commands
import ast
 


###---------------------------------------------------------------------------- GAME STUFF
amazonlinks = ['https://www.amazon.com/dp/B01JKD4HYC/',
               'https://www.amazon.com/dp/B07QTHK8K9/',
               'https://www.amazon.com/dp/045149492X/',
               'https://www.amazon.com/dp/1091069387/',
               'https://www.amazon.com/dp/B00MRJ8GXK/',
               'https://www.amazon.com/dp/B071CFZ4BD/',
               'https://www.amazon.com/dp/B01GSOTFMA/',
               'https://www.amazon.com/dp/B07HGYVM55/',
               'https://www.amazon.com/dp/B001K3A45M/',
               'https://www.amazon.com/dp/B07CVKHCLR/',
               'https://www.amazon.com/dp/B07SHP29DM/',
               'https://www.amazon.com/dp/B075KTTKXS/',
               'https://www.amazon.com/dp/B01I2NXNE6/',
               'https://www.amazon.com/dp/B074RCV4HQ/',
               'https://www.amazon.com/dp/B072L3GMZV/',
               'https://www.amazon.com/dp/B07HKSTWBX/',
               'https://www.amazon.com/dp/B0837JN2FC/']

embarrass = ['I pissed the bed last night!',
             'I listen to 100 gecs!',
             'I have a iphone 5s!',
             'I love Sword Art Online!',
             'I play sexual vr games!',
             'I Googled myself!',
             'I said you too when a staff worker told me to enjoy the movie!',
             'I take rewear filthy clothes from my hamper',
             'I do not brush my teeth!',
             'I think that big chungus is funny!',
             'I like to pretend that I am apart of a different culture to make myself look cool!',
             'I say pog irl unironically!',
             'I still say cringy unironically!',
             'I say and type XD unironically']
###---------------------------------------------------------------------------- END OF GAME STUFF

prefix = "r?"

randNum = random.random()
bot = commands.Bot(command_prefix="r?", help_command=None, case_insensitive=True)
 
# Activity 
async def checkSuggestions():
    await bot.wait_until_ready()
    while True:
        async for message in bot.get_channel(737807052625412208).history(oldest_first=True):
            if get(message.reactions, emoji="✅") and get(message.reactions, emoji="❌"):
                approvalsObject=get(message.reactions, emoji="✅")
                denialsObject=get(message.reactions, emoji="❌")
                approvals=approvalsObject.count-(bot.user in set(await approvalsObject.users().flatten()))      #gets # of yes reactions that isn't the bot
                denials=denialsObject.count-(bot.user in set(await denialsObject.users().flatten()))            #gets # of no reactions that isn't the bot
                timeLimit=datetime.timedelta(seconds=6*3600*(1-(approvals+denials)/bot.memberCount))            #math to figure out the time limit of the suggestion - 0 people reacted yet=6 hrs
                if (message.created_at.utcnow()-message.created_at)>timeLimit:
                    if approvals>denials:
                        embedVar = discord.Embed(title="✅ Approved", description = message.content , color=0x00FF04)
                        print("✅ Approved: \n" + message.content)
                    else:
                        embedVar = discord.Embed(title="❌ Denied", description = message.content , color=0xFF0000)
                        print("❌ Denied: \n" + message.content)
                    embedVar.add_field(name="Suggested by:", value = message.author.mention, inline=False)
                    embedVar.add_field(name="Votes:", value = "✅ " + str(approvals) + " ❌ " + str(denials) , inline=False)
                    embedVar.set_footer(text="Suggested at " + str(message.created_at.strftime("%b %d %Y %H:%M:%S")))
                    files = []
                    for each in message.attachments:
                        files.append(await each.to_file())
                    if len(files) > 0:
                        fileMessage = await bot.get_guild(700359436203458581).get_channel(718277944153210961).send(files=files)
                        embedVar.set_image(url = fileMessage.attachments[0].url)
                    await bot.get_channel(739172158948900925).send(embed=embedVar)
                    await message.delete()
        await asyncio.sleep(5)


@bot.event
async def on_ready():
    # Set Status
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Republic of United Members"))
    bot.memberCount=len([m for m in bot.get_guild(736306540671271036).members if not m.bot])
    bot.loop.create_task(checkSuggestions())
    # Send bot online notices
    print(("\n" * 5) + "Bot is online. Instance ID is " + str(randNum))
    embedVar=discord.Embed(title=":green_circle: Bot is online", color=0x00ff62)
    embedVar.add_field(name="Instance ID:", value= randNum, inline=True)
    await bot.get_channel(740049560591925362).send(embed=embedVar)

async def getLine(fileName,lineNum):
    fh=open(fileName)
    for i, row in enumerate(fh): 
        if i+1==lineNum: 
            return row
def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


@bot.command(name="eval")
async def eval_fn(ctx, *, cmd):
    if not ctx.author.id == 369988289354006528:
        return
    """Evaluates input.
    Input is interpreted as newline seperated statements.
    If the last statement is an expression, that is the return value.
    Usable globals:
      - `bot`: the bot instance
      - `discord`: the discord module
      - `commands`: the discord.ext.commands module
      - `ctx`: the invokation context
      - `__import__`: the builtin `__import__` function
    Such that `>eval 1 + 1` gives `2` as the result.
    The following invokation will cause the bot to send the text '9'
    to the channel of invokation and return '3' as the result of evaluating
    >eval ```
    a = 1 + 2
    b = a * 2
    await ctx.send(a + b)
    a
    ```
    """
    fn_name = "_eval_expr"

    cmd = cmd.strip("` ")

    # add a layer of indentation
    cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

    # wrap in async def body
    body = f"async def {fn_name}():\n{cmd}"

    parsed = ast.parse(body)
    body = parsed.body[0].body

    insert_returns(body)

    env = {
        'bot': ctx.bot,
        'discord': discord,
        'commands': commands,
        'ctx': ctx,
        '__import__': __import__
    }
    exec(compile(parsed, filename="<ast>", mode="exec"), env)

    result = (await eval(f"{fn_name}()", env))
    await ctx.send(f"```{result}```")

@bot.command(name='test')
async def test(ctx):
    print("Test Called")
    embedVar=discord.Embed(title="[ID]", description= str(randNum), color=0x00ff62)
    files = []
    for each in ctx.message.attachments:
        files.append(await each.to_file())
    if len(files) > 0:
        fileMessage = await bot.get_guild(700359436203458581).get_channel(718277944153210961).send(files=files)
        embedVar.set_image(url = fileMessage.attachments[0].url)        
    await ctx.send(embed=embedVar)

@bot.command(name='info')
async def info(ctx):
    print("Info Called")
    embedVar =discord.Embed(title="RUM Bot", description="Custom bot developed for the Republic of United Members discord server.", color=0xd400ff)
    embedVar.set_thumbnail(url="https://cdn.discordapp.com/attachments/738951182969602078/740711482391658567/botpic_2.png")
    embedVar.add_field(name="Version -", value="1.1.3", inline=True)
    embedVar.add_field(name="Contributors -", value="evalyn#8883, pupo#0001, MrMeme#5096", inline=True)
    embedVar.set_footer(text="Any questions? DM one of the contributors!")
    await ctx.send(embed=embedVar)

@bot.command(name="server")
async def server(ctx):    
    print("Server Called")
    embedVar=discord.Embed(title="Republic of United Members", description="Casual server focused around fairness and democracy. ")
    embedVar.set_thumbnail(url="https://cdn.discordapp.com/attachments/738951182969602078/740711351152017458/e20176f3cfe1fc2d0edc24005d749a8b_2.png")
    embedVar.add_field(name="Creation Date:", value= ctx.guild.created_at.strftime("%b %d, %Y"), inline=True)
    embedVar.add_field(name="Server Age:", value= str((ctx.channel.guild.created_at.utcnow() - ctx.channel.guild.created_at).days) + " Days", inline=True)
    embedVar.add_field(name="Member Count:", value= ctx.guild.member_count, inline=True)
    embedVar.add_field(name="Current Consuls:", value="RaccWillAttacc#3661, FlobbsterBisque#5674", inline=True)
    await ctx.send(embed=embedVar)

@bot.command(name="help")
async def serverHelp(ctx):
    print("Help Called")
    embedVar=discord.Embed(title="RUM Bot Command List", description="List containing all bot commands.", color=0xfb00ff)
    embedVar.set_thumbnail(url="https://cdn.discordapp.com/attachments/738951182969602078/740711482391658567/botpic_2.png")
    num_lines = sum(1 for line in open('help.txt'))
    for helpNum in range((num_lines//2)):
        embedVar.add_field(name=await getLine('help.txt',2*helpNum+1), value=await getLine('help.txt',2*helpNum+2), inline=True)
    embedVar.set_footer(text="Any questions? Ask one of the contributors! Any Suggestions? Put them in #suggestions!")
    await ctx.send(embed=embedVar)

@bot.command(name="coinflip", aliases=['cf'])
async def coinflip(ctx):
    flipside = bool(random.getrandbits(1))
    if (flipside):
        flipside = "Heads"
    else:
        flipside = "Tails"
    print("Coin Flipped and Landed on {}".format(flipside))
    await ctx.send("> The coin flipped and landed on {}".format(flipside))

@bot.command(name="rule")
async def rule(ctx, ruleNum : int):
    print("Rule {} Called".format(str(ruleNum)))
    if 1<=ruleNum<=9:
        embedVar = discord.Embed(title=await getLine("rules.txt",2*ruleNum-1), description=await getLine("rules.txt",2*ruleNum), color=0xEC00FF)
        await ctx.send(embed=embedVar)
    else:
        await ctx.send("Invalid Rule Number")

@bot.command(name="bubblewrap", aliases=['bw'])
async def bubbbleWrap(ctx, bubbleContents):
    bubble = f"||{bubbleContents}||"
    maxSize = 12
    dimensions = math.floor(math.sqrt(2000/len(bubble))) - 2
    if dimensions > maxSize:
        dimensions = maxSize
    bubbleGrid = ((bubble * dimensions) + "\n") * (dimensions)
    await ctx.send(bubbleGrid, allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))

@bot.command(name="warn", aliases=["strike", "addwarn", "addstrike"])
async def warn(ctx):
    warnmember = ctx.message.mentions[0]
    if ctx.guild.get_role(736316470098657342) in ctx.author.roles or ctx.author.id == 369988289354006528:
        # If has 4 give 5 and warn
        if warnmember.guild.get_role(742954033115037807) in warnmember.roles:
            await warnmember.add_roles(warnmember.guild.get_role(742954067642548285))
            await ctx.send("{} now has 5 strikes".format(warnmember.mention))
        # If has 3 give 4
        elif warnmember.guild.get_role(742953961014689842) in warnmember.roles:
            await warnmember.add_roles(warnmember.guild.get_role(742954033115037807))
            await ctx.send("{} now has 4 strikes".format(warnmember.mention))
            # If has 2 give 3
        elif warnmember.guild.get_role(742953920225214584) in warnmember.roles:
            await warnmember.add_roles(warnmember.guild.get_role(742953961014689842))
            await ctx.send("{} now has 3 strikes".format(warnmember.mention))
        # If has 1 give 2
        elif warnmember.guild.get_role(742953865439215656) in warnmember.roles:
            await warnmember.add_roles(warnmember.guild.get_role(742953920225214584))
            await ctx.send("{} now has 2 strikes".format(warnmember.mention))
        # If none give one
        else:
            await warnmember.add_roles(warnmember.guild.get_role(743205924059086918))
            await warnmember.add_roles(warnmember.guild.get_role(742953865439215656))
            await ctx.send("{} now has 1 strike".format(warnmember.mention))

@bot.command(name="removewarn", aliases=["removestrike"])
async def removewarn(ctx):
    warnmember = ctx.message.mentions[0]
    if ctx.guild.get_role(736316470098657342) in ctx.author.roles or ctx.author.id == 369988289354006528:
        # If has 5 remove 5
        if warnmember.guild.get_role(742954067642548285) in warnmember.roles:
            await warnmember.remove_roles(warnmember.guild.get_role(742954067642548285))
            await ctx.send("{} now has 4 strikes".format(warnmember.mention))
        # If has 4 remove 4
        elif warnmember.guild.get_role(742954033115037807) in warnmember.roles:
            await warnmember.remove_roles(warnmember.guild.get_role(742954033115037807))
            await ctx.send("{} now has 3 strikes".format(warnmember.mention))
        # If has 3 remove 3
        elif warnmember.guild.get_role(742953961014689842) in warnmember.roles:
            await warnmember.remove_roles(warnmember.guild.get_role(742953961014689842))
            await ctx.send("{} now has 2 strikes".format(warnmember.mention))
        # If has 2 remove 2
        elif warnmember.guild.get_role(742953920225214584) in warnmember.roles:
            await warnmember.remove_roles(warnmember.guild.get_role(742953920225214584))
            await ctx.send("{} now has 1 strikes".format(warnmember.mention))
        # If has 1 remove 1
        elif warnmember.guild.get_role(742953865439215656) in warnmember.roles:
            await warnmember.remove_roles(warnmember.guild.get_role(743205924059086918))
            await warnmember.remove_roles(warnmember.guild.get_role(742953865439215656))
            await ctx.send("{} now has no strikes".format(warnmember.mention))
        else:
            await ctx.send("{} had no strikes".format(warnmember.mention))

@bot.command(name="addrole")
async def addrole(ctx, *roles):
    if ctx.guild.get_role(736316470098657342) in ctx.author.roles or ctx.author.id == 369988289354006528:
        await ctx.send("Starting...")
        for role in roles:
            for member in ctx.guild.members:
                if not member.bot and not role in member.roles:
                    await member.add_roles(ctx.guild.get_role(int(role)))
        await ctx.send("Done!")

@bot.command(name="rockpaperscissors", aliases=["rps"])
async def rps(ctx):
    if len(ctx.message.mentions) > 0:
        opponent=ctx.message.mentions[0]
        msg = await ctx.author.send("Choose Rock, Paper, Or Scissors")
        await msg.add_reaction("✊")
        await msg.add_reaction("🖐️")
        await msg.add_reaction("✌️")
        msg = await opponent.send("Choose Rock, Paper, Or Scissors")
        await msg.add_reaction("✊")
        await msg.add_reaction("🖐️")
        await msg.add_reaction("✌️")
        notResponded = [ctx.author, opponent]
        responses={ctx.author: "", opponent: ""}
        def check(reaction, user):
            if (reaction.emoji in ["✊", "🖐️", "✌️"]): return (user in notResponded)
        while notResponded:
            reaction, user = await bot.wait_for("reaction_add",timeout=60,check=check)
            notResponded.remove(user)
            responses[user] = reaction.emoji
        outcome = {"✊": {"🖐️": True, "✌️": False, "✊": "Tie"}, "🖐️": {"🖐️": "Tie", "✌️": True, "✊": False}, "✌️": {"🖐️": False, "✌️": "Tie", "✊": True}}
        result = outcome[responses[ctx.author]][responses[opponent]]
        print(result)
        if result == True:
            await ctx.send(f"{ctx.author.mention} Won!")
            return
        if result == False:
            await ctx.send(f"{opponent.mention} Won!")
            return
        else:
            await ctx.send("Its a tie")
            return
    else:
        msg = await ctx.send("Choose Rock, Paper, Or Scissors")
        await msg.add_reaction("✊")
        await msg.add_reaction("🖐️")
        await msg.add_reaction("✌️")
        def check(reaction, user):
            return (reaction.emoji in ["✊", "🖐️", "✌️"]) and (user == ctx.author)
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
        rand = random.randint(0,2)
        if rand == 1:
            await ctx.send("You Win!")
        elif rand == 2:
            await ctx.send("You Lose!")
        else:
            await ctx.send("You Tied!")

@bot.command(name="guess")
async def guess(ctx):
    await ctx.send("Guess the number between 0-10 by typing it! (it will end once you guess correctly)")
    number = str(random.randint(1,10))
    def check(m):
        return m.content == number and m.channel == ctx.channel
    msg = await bot.wait_for('message', check=check)
    await ctx.send("Correct answer {.author}!".format(msg))

@bot.command(name="amazon")
async def amazon(ctx):
    await ctx.send(random.choice(amazonlinks))

@bot.command(name="embarrasme", aliases=["embarras"])
async def embarrasMe(ctx):
    await ctx.send(f"{random.choice(embarrass)} from {ctx.author.mention}")

@bot.event
async def on_message(message):
    # Add reaction to the suggestions
    if message.channel.id == 737807052625412208:
        await message.add_reaction("✅")
        await message.add_reaction("❌")
        print("New Suggestion: " + message.content)

    await bot.process_commands(message)

@bot.event
async def on_reaction_add(reaction, user):
    # Remove reaction to make suggestion value accurate
    if reaction.message.channel.id == 737807052625412208 and user != bot.user:
        if reaction.emoji == "✅":
            await reaction.message.remove_reaction("✅", bot.user)
        elif reaction.emoji == "❌":
            await reaction.message.remove_reaction("❌", bot.user)

@bot.event
async def on_reaction_remove(reaction, user):
    # Re-add reaction if there is none
    if reaction.message.channel.id == 737807052625412208:
        if get(reaction.message.reactions, emoji="✅") is None:
            await reaction.message.add_reaction("✅")
        elif get(reaction.message.reactions, emoji="❌") is None:
            await reaction.message.add_reaction("❌")

@bot.event
async def on_member_join(member):
    # Ping welcomer and consulate when a new member joins the server
    if member.bot == False:
        await member.guild.get_channel(739647916905332846).send("{} has joined.\n{}".format(member.mention, member.guild.get_role(736316470098657342).mention))
        with open("roles.txt") as file_in:
            for line in file_in:
                await member.add_roles(member.guild.get_role(int(line)))
        bot.memberCount+=1
    print(member.name + " Joined")

@bot.event
async def on_member_leave(member):
    # Ping welcomer and consulate when a new member joins the server
    if member.bot == False:
        bot.memberCount-=1
    print(member.nick + " Left")



# Reads the enviorment variable token for the token value
# To set it on windows do set TOKEN=token
# U can also make that permanent by using Windows search and searching for environment variables and adding it as one
# linux u can set it with export TOKEN=token
# Macos is probs the same as linux

token = str(os.getenv('TOKEN'))
bot.run(token)
