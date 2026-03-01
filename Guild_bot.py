import discord
from discord.ext import commands

# 1. बॉट सेटअप और Intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# डेटा स्टोर करने के लिए (अभी यह अस्थायी है, बॉट बंद होने पर डेटा हट जाएगा)
# भविष्य में हम इसे फाइल में सेव करना सीखेंगे
player_data = {} # {member_id: {"ff_id": "123", "glory": 500}}

@bot.event
async def on_ready():
    print(f'{bot.user.name} ऑनलाइन है!')
    await bot.change_presence(activity=discord.Game(name="Free Fire - Tracking Glory"))

# --- फीचर्स ---

# 1. प्लेयर रजिस्ट्रेशन (!register 123456789)
@bot.command()
async def register(ctx, ff_id: str):
    user_id = ctx.author.id
    if user_id not in player_data:
        player_data[user_id] = {"ff_id": ff_id, "glory": 0}
        await ctx.send(f"✅ {ctx.author.mention}, आपकी FF ID: `{ff_id}` रजिस्टर हो गई है!")
    else:
        player_data[user_id]["ff_id"] = ff_id
        await ctx.send(f"🔄 {ctx.author.mention}, आपकी FF ID अपडेट होकर `{ff_id}` हो गई है।")

# 2. ग्लोरी जोड़ना (!addglory @user 500) - केवल ऑफिसर या लीडर के लिए
@bot.command()
@commands.has_permissions(manage_messages=True) # जिन्हें मैसेज डिलीट करने की परमिशन है वही चला पाएंगे
async def addglory(ctx, member: discord.Member, points: int):
    if member.id in player_data:
        player_data[member.id]["glory"] += points
        total = player_data[member.id]["glory"]
        await ctx.send(f"🔥 {member.display_name} को {points} ग्लोरी मिली! कुल ग्लोरी: `{total}`")
    else:
        await ctx.send(f"❌ {member.display_name} ने अभी तक `!register` नहीं किया है।")

# 3. अपना स्टेटस चेक करना (!myinfo)
@bot.command()
async def myinfo(ctx):
    user_id = ctx.author.id
    if user_id in player_data:
        data = player_data[user_id]
        embed = discord.Embed(title="Player Info", color=discord.Color.orange())
        embed.add_field(name="Name", value=ctx.author.name, inline=True)
        embed.add_field(name="FF ID", value=data["ff_id"], inline=True)
        embed.add_field(name="Total Glory", value=data["glory"], inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("आपने अभी तक रजिस्टर नहीं किया है। टाइप करें: `!register [आपकी_ID]`")

# 4. गिल्ड वॉर के लिए सबको बुलाना (!war)
@bot.command()
async def war(ctx):
    await ctx.send(f"⚔️ **GUILD WAR ALERT!** ⚔️\n@everyone जल्दी गेम में आओ, वार शुरू हो गया है! अपनी ग्लोरी बढ़ाओ!")

# 5. लीडरबोर्ड (!leaderboard)
@bot.command()
async def leaderboard(ctx):
    if not player_data:
        return await ctx.send("अभी कोई डेटा उपलब्ध नहीं है।")
    
    # ग्लोरी के हिसाब से सॉर्ट करना
    sorted_players = sorted(player_data.items(), key=lambda x: x[1]['glory'], reverse=True)
    
    lb_text = "🏆 **Guild Leaderboard** 🏆\n"
    for i, (uid, data) in enumerate(sorted_players[:10], 1): # टॉप 10
        user = bot.get_user(uid)
        name = user.name if user else "Unknown"
        lb_text += f"{i}. {name} - {data['glory']} Glory\n"
    
    await ctx.send(lb_text)

# एरर हैंडलिंग (अगर कोई बिना परमिशन के कमांड चलाए)
@addglory.error
async def addglory_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ भाई, ये कमांड केवल गिल्ड ऑफिसर्स के लिए है!")

# अपना टोकन यहाँ डालें
bot.run('MTQ3NzUwMzIwODk1MDg2MTgzNA.Gz0-En.nXLQyssi-rUFrxOgGvCA3lZZFn8wcPBEFfoyrc')
