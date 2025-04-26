# main.py

import discord
from discord.ext import commands
from discord.ui import View, button, Button
import json
import asyncio

import config
import database
import controlGames
import functions

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)


# ─── JoinView ────────────────────────────────────────────────────────────────
class JoinView(View):
    def __init__(self, game_name):
        super().__init__(timeout=None)
        self.game_name = game_name

    @button(label="게임 참가", style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: Button):
        user_name = str(interaction.user)
        # 1) 게임 존재 여부 확인 & 현재 참가자 목록 로드
        games = controlGames.read_games()
        for g in games:
            if g[0] == self.game_name:
                players = json.loads(g[3])
                names = [p[0] for p in players]
                # 2) 이미 참가했으면 종료
                if user_name in names:
                    return await interaction.response.send_message(
                        "✅ 이미 참가하셨습니다.", ephemeral=True
                    )
                # 3) 신규 참가 시도
                ok = controlGames.add_player(self.game_name, user_name)
                return await interaction.response.send_message(
                    "🎉 참가 완료!" if ok else "❌ 인원 초과 또는 잘못된 정보입니다.",
                    ephemeral=True
                )
        # 게임 자체가 없다면
        await interaction.response.send_message(
            "❌ 해당 게임을 찾을 수 없습니다.", ephemeral=True
        )


# ─── 봇 준비 완료 ────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f'로그인 성공: {bot.user.name}')


# ─── 일반 유저 커맨드 ───────────────────────────────────────────────────────
@bot.command()
async def 유저등록(ctx, nickname: str, tier: str):
    name = str(ctx.author)
    if tier not in config.TierList:
        return await ctx.send("올바른 티어를 입력해주세요.")
    ok = database.add_user(name, nickname, tier)
    await ctx.send(
        f"{name} {nickname} {tier} 등록되었습니다." if ok else "이미 등록된 유저입니다."
    )

@bot.command()
async def 유저삭제(ctx, nickname: str):
    name = str(ctx.author)
    ok = database.delete_user(name, nickname)
    await ctx.send("삭제되었습니다." if ok else "유저를 찾을 수 없습니다.")

@bot.command()
async def 유저수정(ctx, old_nick: str, new_nick: str, new_tier: str):
    name = str(ctx.author)
    if new_tier not in config.TierList:
        return await ctx.send("올바른 티어를 입력해주세요.")
    ok = database.modify_user(name, old_nick, new_nick, new_tier)
    await ctx.send("수정되었습니다." if ok else "유저를 찾을 수 없습니다.")

@bot.command()
async def 등록확인(ctx):
    rows = database.read_database()
    embed = discord.Embed(title="Users")
    for r in rows:
        embed.add_field(
            name=r[1],
            value=f"Tier: {r[2]} | MMR: {r[3]} | W/L: {r[4]}/{r[5]}",
            inline=False
        )
    await ctx.send(embed=embed)


# ─── 게임 생성 / 참가 / 분배 ─────────────────────────────────────────────────
@bot.command()
async def 게임생성(ctx, game_name: str, t1: int, t2: int):
    ok = controlGames.add_game(game_name, t1, t2)
    if ok:
        view = JoinView(game_name)
        await ctx.send(f"게임 `{game_name}` 생성! 아래 버튼으로 참가하세요.", view=view)
    else:
        await ctx.send("이미 존재하는 게임입니다.")

@bot.command()
async def 팀분배(ctx, game_name: str):
    games = controlGames.read_games()
    for g in games:
        if g[0] == game_name:
            players = json.loads(g[3])
            total = int(g[1]) + int(g[2])
            if len(players) != total:
                return await ctx.send("아직 인원이 덜 찼습니다.")
            pls = [[p[0], int(p[3])] for p in players]
            team1, team2 = functions.make_random_balanced_teams(pls)
            guild = ctx.guild
            role_blue = discord.utils.get(guild.roles, name="blue")
            role_red  = discord.utils.get(guild.roles, name="red")
            for n, _ in team1:
                m = guild.get_member_named(n)
                if m and role_blue:
                    await m.add_roles(role_blue)
            for n, _ in team2:
                m = guild.get_member_named(n)
                if m and role_red:
                    await m.add_roles(role_red)
            await ctx.send(
                f"Team1(Blue): {[n for n,_ in team1]}\n"
                f"Team2(Red): {[n for n,_ in team2]}"
            )
            return
    await ctx.send("게임을 찾을 수 없습니다.")

@bot.command()
async def 게임결과(ctx, game_name: str, result: str, member: discord.Member):
    if result not in ("승", "패"):
        return await ctx.send("‘승’ 또는 ‘패’를 입력해주세요.")
    name = str(member)
    games = controlGames.read_games()
    for g in games:
        if g[0] == game_name:
            players = json.loads(g[3])
            names = [p[0] for p in players]
            if name not in names:
                return await ctx.send("참가자가 아닙니다.")
            if result == "승":
                loser = next(x for x in names if x != name)
                database.record_result(name, loser)
            else:
                winner = next(x for x in names if x != name)
                database.record_result(winner, name)
            return await ctx.send(f"{name}님 {result} 기록 완료!")
    await ctx.send("게임을 찾을 수 없습니다.")


# ─── 관리자 전용 커맨드 ────────────────────────────────────────────────────
from discord.ext.commands import has_permissions, MissingPermissions, BadArgument

@bot.command()
@has_permissions(administrator=True)
async def 관리자유저등록(ctx, member: discord.Member, nickname: str, tier: str):
    if tier not in config.TierList:
        return await ctx.send("올바른 티어를 입력해주세요. Ex) 아이언4, 골드1 등")
    ok = database.add_user(str(member), nickname, tier)
    await ctx.send(
        f"{member.mention} 등록 완료!" if ok else "이미 등록된 유저입니다."
    )

@관리자유저등록.error
async def 관리자유저등록_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("❌ 관리자 권한이 필요합니다.")
    elif isinstance(error, BadArgument):
        await ctx.send("❌ 유효한 멤버를 멘션해주세요.")
    else:
        raise error

@bot.command(name="관리자팀참가")
@has_permissions(administrator=True)
async def 관리자_팀참가(ctx, game_name: str, member: discord.Member):
    user_name = str(member)
    games = controlGames.read_games()
    for g in games:
        if g[0] == game_name:
            players = json.loads(g[3])
            names = [p[0] for p in players]
            if user_name in names:
                return await ctx.send(f"{member.mention} 이미 참가 중입니다.")
            ok = controlGames.add_player(game_name, user_name)
            return await ctx.send(
                f"{member.mention} 참가 완료!" if ok
                else "❌ 참가 실패: 인원 초과 또는 잘못된 정보입니다."
            )
    await ctx.send("❌ 해당 게임을 찾을 수 없습니다.")

@관리자_팀참가.error
async def 관리자_팀참가_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("❌ 관리자 권한이 필요합니다.")
    elif isinstance(error, BadArgument):
        await ctx.send("❌ 멤버를 멘션해주세요.")
    else:
        raise error


# ─── 게임 종료 / 후처리 ────────────────────────────────────────────────────
class EndGameView(View):
    def __init__(self, game_name, team1, team2, ctx):
        super().__init__(timeout=None)
        self.game_name = game_name
        self.team1 = [n for n,_ in team1]
        self.team2 = [n for n,_ in team2]
        self.ctx = ctx

    @button(label="Team1 승리", style=discord.ButtonStyle.green)
    async def on_team1_win(self, interaction, button):
        await self._finish(interaction, winners=self.team1, losers=self.team2)

    @button(label="Team2 승리", style=discord.ButtonStyle.red)
    async def on_team2_win(self, interaction, button):
        await self._finish(interaction, winners=self.team2, losers=self.team1)

    async def _finish(self, interaction, winners, losers):
        # 1) 승패 일괄 기록
        database.record_group_result(winners, losers)

        # 2) 역할(blue/red) 제거 (대상 멤버만)
        guild = self.ctx.guild
        role_blue = discord.utils.get(guild.roles, name="blue")
        role_red  = discord.utils.get(guild.roles, name="red")

        to_clean = set()
        if role_blue:
            to_clean.update(role_blue.members)
        if role_red:
            to_clean.update(role_red.members)

        for m in to_clean:
            removing = [r for r in (role_blue, role_red) if r and r in m.roles]
            if removing:
                await m.remove_roles(*removing, reason="게임 종료 후 역할 초기화")
                await asyncio.sleep(0.5)

        # 3) 음성채팅 이동: '내전-대기실'로 이동
        target_vc = discord.utils.get(guild.voice_channels, name="내전-대기실")
        if target_vc:
            for vc in guild.voice_channels:
                for m in vc.members:
                    await m.move_to(target_vc)

        # 4) 버튼 비활성화 & 메시지 수정
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(
            content=f"✅ `{self.game_name}` 종료 처리 완료! 승리팀: {winners}", view=self
        )


@bot.command()
@has_permissions(administrator=True)
async def 게임종료(ctx, game_name: str):
    games = controlGames.read_games()
    for g in games:
        if g[0] == game_name:
            players = json.loads(g[3])
            total = int(g[1]) + int(g[2])
            if len(players) != total:
                return await ctx.send("아직 인원이 덜 찼습니다.")
            pls = [[p[0], int(p[3])] for p in players]
            team1, team2 = functions.make_random_balanced_teams(pls)
            view = EndGameView(game_name, team1, team2, ctx)
            return await ctx.send("어느 팀이 승리했나요?", view=view)
    await ctx.send("❌ 해당 게임을 찾을 수 없습니다.")

@게임종료.error
async def 게임종료_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("❌ 관리자 권한이 필요합니다.")
    else:
        raise error


# ─── 실행 ─────────────────────────────────────────────────────────────────
bot.run(config.Token)
