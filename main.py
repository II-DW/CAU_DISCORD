import discord
from discord.ext import commands

import config
import database 
import controlGames
import functions

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'로그인 성공: {bot.user.name}')

@bot.command()
async def 유저등록(ctx, *args):
    try :
        name = str(ctx.author)
        nickname = args[0]
        tier = args[1]
    except IndexError:
        await ctx.send('필요한 입력이 부족합니다.')
        return
    
    if tier not in config.TierList :
        await ctx.send("맞는 티어를 입력해주십시오. (뉴비, 언랭, 아이언, 브론즈, 실버, 골드, 플레티넘, 에메랄드, 다이아, 마스터, 그랜드마스터, 챌린저), Ex) 아이언4")
        return
    
    if database.AddDatabase(name, nickname, tier) :
        await ctx.send(str(name) + " " + str(nickname) + " " + str(tier) + " 등록되었습니다.")
    else :
        await ctx.send("이미 있는 유저입니다.")
    
    
    

@bot.command()
async def 유저삭제(ctx, *args):
    try :
        name = str(ctx.author)
        nickname = args[0]
        tier = args[1]
    except IndexError:
        await ctx.send('필요한 입력이 부족합니다.')
        return
    
    if database.DeleteDatabase(name, nickname, tier) :
        await ctx.send(str(name) + " " + str(nickname) + " " + str(tier) + " 삭제하였습니다.")
    else :
        await ctx.send("해당하는 유저를 찾을 수 없습니다.")
        
        


@bot.command()
async def 유저수정(ctx, *args):
    try :
        name = str(ctx.author)
        nickname = args[0]
        tier = args[1]

        name_new = str(ctx.author)
        nickname_new = args[2]
        tier_new = args[3]

    except IndexError:
        await ctx.send('필요한 입력이 부족합니다.')
        return
    
    if tier not in config.TierList :
        await ctx.send("맞는 티어를 입력해주십시오. (뉴비, 언랭, 아이언, 브론즈, 실버, 골드, 플레티넘, 에메랄드, 다이아, 마스터, 그랜드마스터, 챌린저), Ex) 아이언4")
        return
    
    if database.ModifyDatabase(name, nickname, tier, name_new, nickname_new, tier_new) :
        await ctx.send(str(name) + " " + str(nickname) + " " + str(tier) +  " 을 " + str(name_new) + " " + str(nickname_new) + " " + str(tier_new) +  "으로 고쳤습니다.")
        
    else :
        await ctx.send("해당하는 유저를 찾을 수 없습니다.")
        
    

@bot.command()
async def 등록확인(ctx):
    DataBases = database.ReadDataBase()

    embed = discord.Embed(title="Users", description="이름/닉네임/티어 순")
    for line in DataBases :
        embed.add_field(name=line[0], value=str(line[0]) + "\n" + str(line[1]) + "\n" + str(line[2]) + "\n", inline=True)

    await ctx.send(embed=embed)

@bot.command()
async def 게임생성(ctx, *args):
    try :
        game_name = args[0]
        Num_Of_Team_1 = int(args[1])
        Num_Of_Team_2 = int(args[2])

    except IndexError:
        await ctx.send('필요한 입력이 부족합니다.')
        return
    
    if controlGames.AddDatabase(game_name, Num_Of_Team_1, Num_Of_Team_2) :
        await ctx.send(str(game_name) + "으로 새로운 게임이 생성되었습니다.")

    else :
        await ctx.send("정보가 잘못되었습니다.")
    
@bot.command()
async def 게임참가(ctx, *args):
    try :
        game_name = args[0]
        name = str(ctx.author)

    except IndexError:
        await ctx.send('필요한 입력이 부족합니다.')
        return
    
    if controlGames.AddPlayer(game_name, name) :
        await ctx.send(str(game_name) + "에 " + str(name) + "으로 참가했습니다.")
    else :
        await ctx.send("정보가 잘못되었습니다.")

@bot.command()
async def 게임불참(ctx, *args):
    try :
        game_name = args[0]
        name = str(ctx.author)

    except IndexError:
        await ctx.send('필요한 입력이 부족합니다.')
        return
    
    if controlGames.DeleteUser(game_name, name) :
        await ctx.send(str(game_name) + "에 " + str(name) + "을 삭제했습니다.")
    else :
        await ctx.send("정보가 잘못되었습니다.")

@bot.command()
async def 게임제거(ctx, *args):
    try :
        game_name = args[0]

    except IndexError:
        await ctx.send('필요한 입력이 부족합니다.')
        return
    
    if controlGames.AddDatabase(game_name):
        await ctx.send(str(game_name) + "을 삭제했습니다.")
    else :
        await ctx.send("정보가 잘못되었습니다.")

@bot.command()
async def 팀분배(ctx, *args):
    try :
        game_name = args[0]

    except IndexError:
        await ctx.send('필요한 입력이 부족합니다.')
        return
    
    DataBase = controlGames.ReadDataBase()
    for line in DataBase :
        if line[0] == game_name :
            L = eval(line[3])
            if len(L) == int(line[1]) + int(line[2]) :
                players = [[L[i][0],config.TierList[L[i][2]]] for i in range(len(L))]
                team1, team2 = functions.make_random_balanced_teams(players)
                await ctx.send(str(team1) + "|" + str(team2))
            else :
                await ctx.send("아직 인원이 덜 찼습니다.")
                return
            
    await ctx.send('명령어 응답을 작성해주세요')

bot.run(config.Token)
