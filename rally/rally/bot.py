"""The Discord side of Rally: slash commands, the cards Rally posts, buttons, private forms and reminders.

Privacy rule for this file: anything a person types into a form is answered only with an ephemeral message (only
they see it). Messages to the channel carry counts and option features, never someone's private answers.
"""

from __future__ import annotations

import json
import logging
import math
import re
from datetime import timedelta

import discord
from discord import app_commands
from discord.ext import commands, tasks

from . import config, events, solver
from .db import DB
from .models import Arrival, Event, Prefs
from .parse import parse_arrival, parse_prefs
from .places import load_places
from .timeparse import hhmm, now, parse_when

log = logging.getLogger("rally.bot")

BRAND = discord.Color.from_rgb(140, 29, 64)  # ASU maroon
PRIVATE_NOTE = "Your answers are private. The group only sees counts and options that work for everyone."


class RallyBot(commands.Bot):
    def __init__(self, db: DB):
        intents = discord.Intents.default()
        intents.message_content = True  # to notice Sun Devil Central links pasted in the chat
        super().__init__(command_prefix=commands.when_mentioned, intents=intents)
        self.db = db

    async def setup_hook(self) -> None:
        self.add_dynamic_items(RallyButton)
        self.tree.add_command(rally_group)
        self.tree.add_command(squad_cmd)
        self.tree.add_command(decide_cmd)
        if config.DISCORD_GUILD_ID:
            guild = discord.Object(id=config.DISCORD_GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()
        self.housekeeping.start()

    async def on_ready(self) -> None:
        log.info("Rally is online as %s", self.user)

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or not message.guild:
            return
        url = events.find_event_link(message.content)
        if url and not await self.db.is_paused(message.channel.id):
            event, complete = await events.lookup(url)
            await self.start_squad(message.channel, event, complete, message.author.id)

    # ------------------------------------------------------------ Squad mode

    async def start_squad(self, channel: discord.abc.Messageable, event: Event, complete: bool, starter_id: int | None,
                          shared_by: str | None = None) -> int:
        sid = await self.db.create_session(
            "squad", channel.id, channel.guild.id, starter_id,
            event_json=json.dumps(event.to_json()),
            plan_at=event.starts_at.isoformat() if event.starts_at else None,
        )
        intro = f"**{shared_by}** shared this from Cubbie. Anyone down?" if shared_by else "Anyone down? Tap below."
        embed, view = await self.squad_card(sid)
        msg = await channel.send(content=intro, embed=embed, view=view)
        await self.db.update_session(sid, message_id=msg.id)
        if not complete:
            await channel.send(
                "I couldn't read the full event details from that link (Sun Devil Central may need an ASU login). "
                "Anyone can tap **Edit details** to add the time and place.",
                delete_after=600,
            )
        return sid

    async def squad_card(self, sid: int) -> tuple[discord.Embed, discord.ui.View]:
        s = await self.db.session(sid)
        event = Event.from_json(json.loads(s["event_json"]))
        answers = await self.db.answers(sid)
        arrivals = {uid: Arrival.from_json(a) for uid, a in answers.items()}
        ins = [uid for uid, a in arrivals.items() if a.rsvp == "in"]
        maybes = sum(a.rsvp == "maybe" for a in arrivals.values())
        outs = sum(a.rsvp == "out" for a in arrivals.values())
        locked = s["status"] == "locked"

        embed = discord.Embed(title=event.title, url=event.url or None, color=BRAND)
        when = event.starts_at.strftime("%a %b %-d, ") + hhmm(event.starts_at) if event.starts_at else "Time TBD"
        embed.add_field(name="When", value=when, inline=True)
        embed.add_field(name="Where", value=event.location or "TBD", inline=True)
        going = ", ".join(f"<@{u}>" for u in ins) or "nobody yet"
        embed.add_field(name="Going", value=f"In: {going}\nMaybe: {maybes} · Can't: {outs}", inline=False)
        spot = f"the entrance of {event.location}" if event.location else "the event entrance"
        plan = json.loads(s["plan_json"]) if s["plan_json"] else None
        if locked and plan:
            embed.add_field(name="Locked in", value=plan["text"], inline=False)
        else:
            embed.add_field(name="Suggested plan", value=solver.squad_suggest(list(arrivals.values()), event).summary(spot), inline=False)
        embed.set_footer(text="Arrival times and rides are private. Only Rally sees them.")

        view = discord.ui.View(timeout=None)
        view.add_item(RallyButton("squad", "in", sid, label="I'm in", style=discord.ButtonStyle.success))
        view.add_item(RallyButton("squad", "maybe", sid, label="Maybe", style=discord.ButtonStyle.secondary))
        view.add_item(RallyButton("squad", "out", sid, label="Can't", style=discord.ButtonStyle.danger))
        if not locked:
            view.add_item(RallyButton("squad", "edit", sid, label="Edit details", style=discord.ButtonStyle.secondary))
            view.add_item(RallyButton("squad", "lock", sid, label="Lock it in", style=discord.ButtonStyle.primary))
        return embed, view

    async def refresh_card(self, sid: int) -> None:
        s = await self.db.session(sid)
        channel = self.get_channel(s["channel_id"]) or await self.fetch_channel(s["channel_id"])
        if not s["message_id"]:
            return
        msg = channel.get_partial_message(s["message_id"])
        if s["mode"] == "squad":
            embed, view = await self.squad_card(sid)
        else:
            embed, view = await self.decide_card(sid)
        try:
            await msg.edit(embed=embed, view=view)
        except discord.HTTPException:
            log.warning("could not edit card for session %s", sid)

    async def lock_squad(self, sid: int, channel: discord.abc.Messageable) -> None:
        s = await self.db.session(sid)
        event = Event.from_json(json.loads(s["event_json"]))
        arrivals = [Arrival.from_json(a) for a in (await self.db.answers(sid)).values()]
        spot = f"the entrance of {event.location}" if event.location else "the event entrance"
        plan = solver.squad_suggest(arrivals, event)
        when = plan.meet_at or event.starts_at
        text = plan.summary(spot)
        await self.db.update_session(
            sid, status="locked", plan_json=json.dumps({"text": text}), plan_at=when.isoformat() if when else None
        )
        await self.refresh_card(sid)
        note = await self.create_discord_event(channel.guild, event.title, when, event.location, event.url)
        await channel.send(f"🔒 **Locked in: {event.title}.** {text}{note}")

    # ------------------------------------------------------------ Decide mode

    async def start_decide(self, interaction: discord.Interaction, question: str, kind: str, minutes: int) -> None:
        pick_at = now() + timedelta(minutes=minutes)
        sid = await self.db.create_session(
            "decide", interaction.channel_id, interaction.guild_id, interaction.user.id,
            question=question, kind=kind, pick_at=pick_at.isoformat(),
        )
        embed, view = await self.decide_card(sid)
        await interaction.response.send_message(embed=embed, view=view)
        msg = await interaction.original_response()
        await self.db.update_session(sid, message_id=msg.id)

    async def decide_card(self, sid: int) -> tuple[discord.Embed, discord.ui.View]:
        s = await self.db.session(sid)
        n = len(await self.db.answers(sid))
        embed = discord.Embed(title=f"Deciding: {s['question']}", color=BRAND)
        if s["status"] == "open":
            embed.description = (
                "Tap **Share my preferences** and tell Rally your budget, diet, free time, drinks and vibe.\n"
                f"{PRIVATE_NOTE}"
            )
            embed.add_field(name="Answers so far", value=str(n), inline=True)
            embed.add_field(name="Rally picks at", value=f"{hhmm(_dt(s['pick_at']))} (or tap Pick now)", inline=True)
        else:
            embed.description = f"Answers are in ({n}). The options are below."
        view = discord.ui.View(timeout=None)
        if s["status"] == "open":
            view.add_item(RallyButton("decide", "share", sid, label="Share my preferences", style=discord.ButtonStyle.success))
            view.add_item(RallyButton("decide", "pick", sid, label="Pick now", style=discord.ButtonStyle.primary))
        return embed, view

    async def pick(self, sid: int) -> None:
        s = await self.db.session(sid)
        if s["status"] != "open":
            return
        channel = self.get_channel(s["channel_id"]) or await self.fetch_channel(s["channel_id"])
        group = [Prefs.from_json(a) for a in (await self.db.answers(sid)).values()]
        if not group:
            await self.db.update_session(sid, status="closed")
            await self.refresh_card(sid)
            await channel.send(f"Nobody shared preferences for **{s['question']}**, so I closed it. Start again with `/decide`.")
            return
        result = solver.decide(group, load_places(), s["kind"] or "food")
        options = [
            {"name": o.place.name, "reasons": o.reasons, "link": o.place.link, "area": o.place.area}
            for o in result.options
        ]
        start = max((p.free_from for p in group if p.free_from), default=None)
        await self.db.update_session(
            sid, status="voting", options_json=json.dumps(options), plan_at=start.isoformat() if start else None
        )
        await self.refresh_card(sid)
        if not options:
            await channel.send(result.summary())
            return
        embed, view = await self.options_card(sid, result.summary())
        await channel.send(embed=embed, view=view)

    async def options_card(self, sid: int, summary: str | None = None) -> tuple[discord.Embed, discord.ui.View]:
        s = await self.db.session(sid)
        options = json.loads(s["options_json"])
        tally = await self.db.tally(sid)
        embed = discord.Embed(title=f"Vote: {s['question']}", color=BRAND)
        if summary:
            embed.description = summary
        for i, o in enumerate(options):
            votes = tally.get(i, 0)
            embed.add_field(
                name=f"{i + 1}. {o['name']}  ({votes} vote{'s' if votes != 1 else ''})",
                value="· ".join(o["reasons"]) + (f"\n{o['link']}" if o.get("link") else ""),
                inline=False,
            )
        embed.set_footer(text=f"Lock it in when you're ready ({tally.get(-1, 0)} so far). The top vote wins.")
        view = discord.ui.View(timeout=None)
        if s["status"] == "voting":
            for i, o in enumerate(options):
                view.add_item(RallyButton("decide", "vote", sid, idx=i, label=f"{i + 1}. {o['name'][:70]}", style=discord.ButtonStyle.secondary))
            view.add_item(RallyButton("decide", "lock", sid, label="Lock it in", style=discord.ButtonStyle.primary))
        return embed, view

    async def lock_decide(self, sid: int, interaction: discord.Interaction) -> None:
        s = await self.db.session(sid)
        options = json.loads(s["options_json"])
        tally = await self.db.tally(sid)
        winner_idx = max(range(len(options)), key=lambda i: (tally.get(i, 0), -i))
        winner = options[winner_idx]
        when = _dt(s["plan_at"])
        text = f"{winner['name']}" + (f" at {hhmm(when)}" if when else "")
        await self.db.update_session(sid, status="locked", plan_json=json.dumps({"text": text}))
        embed, view = await self.options_card(sid)
        await interaction.message.edit(embed=embed, view=view)
        note = await self.create_discord_event(interaction.guild, f"{s['question']}: {winner['name']}", when, winner.get("area", ""), winner.get("link", ""))
        await interaction.channel.send(f"🔒 **Locked in: {text}.**{note}")

    # ------------------------------------------------------------ shared helpers

    async def create_discord_event(self, guild: discord.Guild, name: str, when, location: str, url: str) -> str:
        """Create a Discord scheduled event. Returns a short note for the channel message."""
        if not when or when <= now():
            return ""
        try:
            await guild.create_scheduled_event(
                name=name[:100],
                start_time=when,
                end_time=when + timedelta(hours=2),
                entity_type=discord.EntityType.external,
                privacy_level=discord.PrivacyLevel.guild_only,
                location=(location or "See chat")[:100],
                description=url or "Planned with Rally",
            )
            return "\nI added it to this server's Events, and I'll check in an hour before."
        except discord.HTTPException:
            log.warning("could not create scheduled event (does Rally have Manage Events?)")
            return "\nI'll check in an hour before."

    @tasks.loop(seconds=30)
    async def housekeeping(self) -> None:
        for s in await self.db.due_picks():
            try:
                await self.pick(s["id"])
            except Exception:
                log.exception("auto-pick failed for session %s", s["id"])
        for s in await self.db.due_reminders():
            if await self.db.is_paused(s["channel_id"]):
                continue
            await self.db.update_session(s["id"], reminded=1)
            channel = self.get_channel(s["channel_id"])
            if not channel:
                continue
            plan = json.loads(s["plan_json"] or "{}").get("text", "the plan")
            view = discord.ui.View(timeout=None)
            if s["mode"] == "squad":
                view.add_item(RallyButton("squad", "still", s["id"], label="Still in", style=discord.ButtonStyle.success))
                view.add_item(RallyButton("squad", "out", s["id"], label="Can't make it", style=discord.ButtonStyle.danger))
            await channel.send(f"⏰ Starting in about an hour: {plan}\nStill coming?", view=view)
        await self.db.purge_old_answers()

    @housekeeping.before_loop
    async def _wait_ready(self) -> None:
        await self.wait_until_ready()

    # ------------------------------------------------------------ called by the web API (Cubbie)

    async def share_from_cubbie(self, code: str, event: Event, shared_by: str | None) -> int | None:
        row = await self.db.channel_for_code(code)
        if not row or row["paused"]:
            return None
        channel = self.get_channel(row["channel_id"]) or await self.fetch_channel(row["channel_id"])
        complete = event.starts_at is not None
        if event.url and not complete:
            looked_up, complete = await events.lookup(event.url)
            event = Event(
                title=event.title if event.title != "Event" else looked_up.title,
                url=event.url,
                starts_at=event.starts_at or looked_up.starts_at,
                ends_at=event.ends_at or looked_up.ends_at,
                location=event.location or looked_up.location,
                note=event.note,
            )
        await self.start_squad(channel, event, complete, None, shared_by=shared_by or "Someone")
        return row["channel_id"]


def _dt(value):
    from datetime import datetime

    return datetime.fromisoformat(value) if value else None


# ================================================================ buttons


class RallyButton(discord.ui.DynamicItem[discord.ui.Button], template=r"rally:(?P<mode>squad|decide):(?P<action>[a-z]+):(?P<sid>\d+)(?::(?P<idx>\d+))?"):
    """One button class for every Rally card. The custom_id carries the session, so buttons survive restarts."""

    def __init__(self, mode: str, action: str, sid: int, idx: int | None = None, *, label: str = "",
                 style: discord.ButtonStyle = discord.ButtonStyle.secondary, item: discord.ui.Button | None = None):
        custom_id = f"rally:{mode}:{action}:{sid}" + (f":{idx}" if idx is not None else "")
        super().__init__(item or discord.ui.Button(label=label or action, style=style, custom_id=custom_id))
        self.mode, self.action, self.sid, self.idx = mode, action, sid, idx

    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item: discord.ui.Button, match: re.Match[str], /):
        idx = int(match["idx"]) if match["idx"] else None
        return cls(match["mode"], match["action"], int(match["sid"]), idx, item=item)

    async def callback(self, interaction: discord.Interaction) -> None:
        bot: RallyBot = interaction.client  # type: ignore[assignment]
        s = await bot.db.session(self.sid)
        if s is None or s["status"] in ("closed", "purged"):
            await interaction.response.send_message("This plan has ended.", ephemeral=True)
            return
        handler = getattr(self, f"_{self.mode}_{self.action}", None)
        if handler:
            await handler(bot, interaction, s)

    # ---- squad

    async def _squad_in(self, bot, interaction, s):
        await interaction.response.send_modal(ArrivalModal(self.sid, "in"))

    async def _squad_maybe(self, bot, interaction, s):
        await interaction.response.send_modal(ArrivalModal(self.sid, "maybe"))

    async def _squad_out(self, bot, interaction, s):
        await bot.db.save_answer(self.sid, interaction.user.id, Arrival(rsvp="out").to_json())
        await interaction.response.send_message("Got it, you can't make it. Maybe next time!", ephemeral=True)
        await bot.refresh_card(self.sid)

    async def _squad_still(self, bot, interaction, s):
        answers = await bot.db.answers(self.sid)
        a = Arrival.from_json(answers.get(interaction.user.id, {"rsvp": "in"}))
        a.rsvp = "in"
        await bot.db.save_answer(self.sid, interaction.user.id, a.to_json())
        await interaction.response.send_message("Great, see you there!", ephemeral=True)
        await bot.refresh_card(self.sid)

    async def _squad_edit(self, bot, interaction, s):
        await interaction.response.send_modal(EventModal(self.sid, Event.from_json(json.loads(s["event_json"]))))

    async def _squad_lock(self, bot, interaction, s):
        if s["status"] == "locked":
            await interaction.response.send_message("This plan is already locked in.", ephemeral=True)
            return
        answers = await bot.db.answers(self.sid)
        ins = [uid for uid, a in answers.items() if a.get("rsvp") == "in"]
        if interaction.user.id not in ins:
            await interaction.response.send_message("Tap **I'm in** first, then you can vote to lock it in.", ephemeral=True)
            return
        await bot.db.vote(self.sid, interaction.user.id, -1)
        lock_votes = (await bot.db.tally(self.sid)).get(-1, 0)
        needed = max(1, math.ceil(len(ins) / 2))
        if lock_votes >= needed:
            await interaction.response.send_message("Locking it in.", ephemeral=True)
            await bot.lock_squad(self.sid, interaction.channel)
        else:
            await interaction.response.send_message(
                f"Your vote is in. {lock_votes} of {needed} needed to lock it in.", ephemeral=True
            )

    # ---- decide

    async def _decide_share(self, bot, interaction, s):
        if s["status"] != "open":
            await interaction.response.send_message("Answers are closed for this one.", ephemeral=True)
            return
        await interaction.response.send_modal(PrefsModal(self.sid))

    async def _decide_pick(self, bot, interaction, s):
        if not await bot.db.answers(self.sid):
            await interaction.response.send_message("Nobody has shared preferences yet.", ephemeral=True)
            return
        await interaction.response.send_message("Picking now.", ephemeral=True)
        await bot.pick(self.sid)

    async def _decide_vote(self, bot, interaction, s):
        if s["status"] != "voting":
            await interaction.response.send_message("Voting is closed.", ephemeral=True)
            return
        await bot.db.vote(self.sid, interaction.user.id, self.idx)
        name = json.loads(s["options_json"])[self.idx]["name"]
        embed, view = await bot.options_card(self.sid)
        await interaction.response.edit_message(embed=embed, view=view)
        await interaction.followup.send(f"You voted for {name}.", ephemeral=True)

    async def _decide_lock(self, bot, interaction, s):
        if s["status"] != "voting":
            await interaction.response.send_message("This is already locked in.", ephemeral=True)
            return
        tally = await bot.db.tally(self.sid)
        if not any(tally.get(i, 0) for i in range(len(json.loads(s["options_json"])))):
            await interaction.response.send_message("Vote for an option first.", ephemeral=True)
            return
        await bot.db.vote(self.sid, interaction.user.id, -1)
        tally = await bot.db.tally(self.sid)
        people = len(await bot.db.answers(self.sid))
        needed = max(1, math.ceil(people / 2))
        if tally.get(-1, 0) >= needed:
            await interaction.response.defer()
            await bot.lock_decide(self.sid, interaction)
        else:
            embed, view = await bot.options_card(self.sid)
            await interaction.response.edit_message(embed=embed, view=view)
            await interaction.followup.send(f"Your lock vote is in. {tally.get(-1, 0)} of {needed} needed.", ephemeral=True)


# ================================================================ private forms


class ArrivalModal(discord.ui.Modal):
    arrive = discord.ui.TextInput(label="When can you get there?", placeholder="6:30pm, or 'on time'", required=False, max_length=40)
    leave = discord.ui.TextInput(label="When do you need to leave? (optional)", placeholder="9pm", required=False, max_length=40)
    other = discord.ui.TextInput(label="Need a ride, or can you drive? (optional)", placeholder="need a ride / can drive", required=False, max_length=100)

    def __init__(self, sid: int, rsvp: str):
        super().__init__(title="You're in! (only Rally sees this)" if rsvp == "in" else "Maybe (only Rally sees this)")
        self.sid, self.rsvp = sid, rsvp

    async def on_submit(self, interaction: discord.Interaction) -> None:
        bot: RallyBot = interaction.client  # type: ignore[assignment]
        s = await bot.db.session(self.sid)
        event = Event.from_json(json.loads(s["event_json"]))
        day = event.starts_at.date() if event.starts_at else None
        arrive = "" if self.arrive.value.strip().lower() in ("on time", "ontime") else self.arrive.value
        a = parse_arrival(self.rsvp, arrive, self.leave.value, self.other.value, day)
        await bot.db.save_answer(self.sid, interaction.user.id, a.to_json())
        bits = []
        if a.earliest:
            bits.append(f"there by {hhmm(a.earliest)}")
        if a.latest:
            bits.append(f"leaving by {hhmm(a.latest)}")
        if a.ride:
            bits.append("needs a ride" if a.ride == "need" else "can drive")
        await interaction.response.send_message(
            f"Got it, you're **{'in' if self.rsvp == 'in' else 'a maybe'}**"
            + (f" ({', '.join(bits)})" if bits else "") + ". Only Rally sees your times.",
            ephemeral=True,
        )
        await bot.refresh_card(self.sid)


class EventModal(discord.ui.Modal, title="Event details"):
    name = discord.ui.TextInput(label="Event name", max_length=100)
    when = discord.ui.TextInput(label="When", placeholder="today 7pm, fri 8pm, 10/30 6:30pm", max_length=40, required=False)
    where = discord.ui.TextInput(label="Where", placeholder="Memorial Union, Ventana Ballroom", max_length=100, required=False)

    def __init__(self, sid: int, event: Event):
        super().__init__()
        self.sid, self.event = sid, event
        self.name.default = event.title if event.title != "Shared event" else ""
        self.where.default = event.location

    async def on_submit(self, interaction: discord.Interaction) -> None:
        bot: RallyBot = interaction.client  # type: ignore[assignment]
        starts = parse_when(self.when.value) or self.event.starts_at
        if self.when.value and not parse_when(self.when.value):
            await interaction.response.send_message("I couldn't read that time. Try something like `fri 8pm`.", ephemeral=True)
            return
        ev = Event(title=self.name.value, url=self.event.url, starts_at=starts, location=self.where.value, note=self.event.note)
        await bot.db.update_session(self.sid, event_json=json.dumps(ev.to_json()), plan_at=starts.isoformat() if starts else None)
        await interaction.response.send_message("Updated the event details.", ephemeral=True)
        await bot.refresh_card(self.sid)


class PrefsModal(discord.ui.Modal, title="Your preferences (only Rally sees this)"):
    budget = discord.ui.TextInput(label="Budget per person", placeholder="$15, or 'broke till Friday'", required=False, max_length=60)
    diet = discord.ui.TextInput(label="Diet or foods you can't eat", placeholder="vegetarian, no pork, gluten-free", required=False, max_length=120)
    free = discord.ui.TextInput(label="When are you free?", placeholder="after 7, or 6-9pm", required=False, max_length=60)
    drinks_vibe = discord.ui.TextInput(
        label="Drinks and vibe", placeholder="chill, no drinks / down to party / under 21", required=False, max_length=120
    )
    extra = discord.ui.TextInput(
        label="Craving anything? Anything to veto?", placeholder="tacos, not Chipotle again", required=False, max_length=120
    )

    def __init__(self, sid: int):
        super().__init__()
        self.sid = sid

    async def on_submit(self, interaction: discord.Interaction) -> None:
        bot: RallyBot = interaction.client  # type: ignore[assignment]
        await interaction.response.defer(ephemeral=True, thinking=True)
        p = await parse_prefs(self.budget.value, self.diet.value, self.free.value, self.drinks_vibe.value, self.extra.value)
        await bot.db.save_answer(self.sid, interaction.user.id, p.to_json())
        await interaction.followup.send(f"Got it. Here's what I understood:\n{_describe(p)}\n\n{PRIVATE_NOTE}", ephemeral=True)
        await bot.refresh_card(self.sid)


def _describe(p: Prefs) -> str:
    """Read someone's own answers back to them (ephemeral only)."""
    lines = []
    if p.budget_max is not None:
        lines.append(f"- Budget: up to ${p.budget_max:g}")
    if p.diets:
        lines.append("- Diet: " + ", ".join(d.replace("_", "-") for d in p.diets))
    if p.avoid:
        lines.append("- Avoid: " + ", ".join(p.avoid))
    if p.free_from or p.free_until:
        lines.append(f"- Free: {hhmm(p.free_from) if p.free_from else 'now'} to {hhmm(p.free_until) if p.free_until else 'late'}")
    if p.under_21:
        lines.append("- No 21+ places")
    if p.sober:
        lines.append("- No bars or drinking-focused places")
    elif p.wants_drinks:
        lines.append("- Somewhere with drinks would be nice")
    if p.vibe is not None:
        lines.append("- Vibe: " + ("chill" if p.vibe < 0.35 else "party" if p.vibe > 0.65 else "in between"))
    if p.cravings:
        lines.append("- Craving: " + ", ".join(p.cravings))
    if p.veto:
        lines.append(f"- Veto: {p.veto}")
    return "\n".join(lines) or "- No limits, you're easy to please!"


# ================================================================ slash commands

rally_group = app_commands.Group(name="rally", description="Rally settings for this channel")


@rally_group.command(name="link", description="Get a code to connect this channel to CampusCue on Cubbie")
async def rally_link(interaction: discord.Interaction) -> None:
    bot: RallyBot = interaction.client  # type: ignore[assignment]
    code = await bot.db.link_code(interaction.channel_id, interaction.guild_id)
    await interaction.response.send_message(
        f"Text this to Cubbie to connect CampusCue to this channel:\n`connect Rally {code}`\n\n"
        "After that, when CampusCue suggests an event, reply \"share with my friends\" and it shows up here. "
        "Keep the code to your group: anyone with it can share events here. `/rally unlink` turns it off.",
        ephemeral=True,
    )


@rally_group.command(name="unlink", description="Turn off the Cubbie link code for this channel")
async def rally_unlink(interaction: discord.Interaction) -> None:
    bot: RallyBot = interaction.client  # type: ignore[assignment]
    await bot.db.unlink(interaction.channel_id)
    await interaction.response.send_message("The link code is turned off. `/rally link` makes a new one.", ephemeral=True)


@rally_group.command(name="pause", description="Stop Rally from reacting to links and sending reminders here")
async def rally_pause(interaction: discord.Interaction) -> None:
    bot: RallyBot = interaction.client  # type: ignore[assignment]
    await bot.db.set_paused(interaction.channel_id, interaction.guild_id, True)
    await interaction.response.send_message("Rally is paused in this channel. `/rally resume` turns it back on.")


@rally_group.command(name="resume", description="Turn Rally back on in this channel")
async def rally_resume(interaction: discord.Interaction) -> None:
    bot: RallyBot = interaction.client  # type: ignore[assignment]
    await bot.db.set_paused(interaction.channel_id, interaction.guild_id, False)
    await interaction.response.send_message("Rally is back on.")


@rally_group.command(name="help", description="How Rally works")
async def rally_help(interaction: discord.Interaction) -> None:
    await interaction.response.send_message(
        "**Rally turns \"anyone down?\" into a plan.**\n"
        "- Paste a Sun Devil Central link, or use `/squad`, to start an event plan: tap In, Maybe or Can't, "
        "add your arrival time privately, then **Lock it in**.\n"
        "- `/decide dinner tonight?` collects everyone's budget, diet, free time, drinks and vibe privately, "
        "then puts only options that work for everyone up for a vote.\n"
        "- `/rally link` connects CampusCue on Cubbie so you can share events here from iMessage.\n"
        "- `/rally pause` stops Rally in this channel.\n\n"
        f"{PRIVATE_NOTE}",
        ephemeral=True,
    )


@app_commands.command(name="squad", description="Start an event plan: who's in, when to meet, lock it in")
@app_commands.describe(event="A Sun Devil Central link or the event name", when="e.g. fri 8pm", where="e.g. Memorial Union")
async def squad_cmd(interaction: discord.Interaction, event: str, when: str | None = None, where: str | None = None) -> None:
    bot: RallyBot = interaction.client  # type: ignore[assignment]
    await interaction.response.defer(ephemeral=True)
    url = events.find_event_link(event) or (event if event.startswith("http") else "")
    if url:
        ev, complete = await events.lookup(url)
    else:
        ev, complete = Event(title=event), False
    if when:
        ev.starts_at = parse_when(when) or ev.starts_at
    if where:
        ev.location = where
    await bot.start_squad(interaction.channel, ev, complete or ev.starts_at is not None, interaction.user.id)
    await interaction.followup.send("Posted. Tap **I'm in** on the card to join your own plan.", ephemeral=True)


@app_commands.command(name="decide", description="Decide something as a group, with everyone's limits kept private")
@app_commands.describe(question="What you're deciding, e.g. dinner tonight?", kind="What kind of options", minutes="Minutes to collect answers")
@app_commands.choices(kind=[
    app_commands.Choice(name="Food", value="food"),
    app_commands.Choice(name="Something to do", value="activity"),
    app_commands.Choice(name="Anything (night out)", value="any"),
])
async def decide_cmd(interaction: discord.Interaction, question: str, kind: app_commands.Choice[str] | None = None,
                     minutes: app_commands.Range[int, 1, 120] | None = None) -> None:
    bot: RallyBot = interaction.client  # type: ignore[assignment]
    await bot.start_decide(interaction, question, kind.value if kind else "food", minutes or config.DECIDE_DEFAULT_MINUTES)
