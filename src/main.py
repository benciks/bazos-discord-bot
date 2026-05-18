import asyncio
import logging
from datetime import datetime

import discord
from discord.ext import commands, tasks

from .config import config
from .offers_storage import OffersStorage
from .part_offer import PartOffer
from .scrapers.scraper_bazos import ScraperBazos

logging.basicConfig(
    level=logging.DEBUG if config.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

storage: OffersStorage | None = None
scraper: ScraperBazos | None = None
first_run = True


def create_embed(offer: PartOffer) -> discord.Embed:
    embed = discord.Embed(
        title=offer.title[:256],
        url=offer.link,
        description=offer.description[:400] if offer.description else None,
        color=0x001E50,  # VW Blue
    )

    embed.add_field(name="💰 Price", value=offer.price, inline=True)
    embed.add_field(name="📍 Location", value=offer.location, inline=True)
    embed.add_field(name="🔍 Query", value=offer.search_query, inline=True)

    if offer.image_url:
        embed.set_thumbnail(url=offer.image_url)

    if offer.date_posted:
        embed.set_footer(text=f"Posted: {offer.date_posted}")

    return embed


async def send_offers_to_channel(channel: discord.TextChannel, offers: list[PartOffer]):
    batch_size = 10

    for i in range(0, len(offers), batch_size):
        batch = offers[i : i + batch_size]
        embeds = [create_embed(offer) for offer in batch]

        try:
            await channel.send(embeds=embeds)
        except discord.HTTPException as e:
            logger.error(f"Failed to send embeds: {e}")
            for embed in embeds:
                try:
                    await channel.send(embed=embed)
                except discord.HTTPException as e2:
                    logger.error(f"Failed to send single embed: {e2}")

        if i + batch_size < len(offers):
            await asyncio.sleep(1)


@tasks.loop(minutes=config.refresh_interval_minutes)
async def check_offers():
    global first_run, storage, scraper

    if storage is None or scraper is None:
        return

    logger.info("Checking for new offers...")

    try:
        all_offers = await asyncio.get_event_loop().run_in_executor(None, scraper.get_latest_offers)
    except Exception as e:
        logger.error(f"Failed to fetch offers: {e}")
        return

    new_offers = [o for o in all_offers if not storage.contains(o)]

    logger.info(f"Found {len(all_offers)} total, {len(new_offers)} new")

    if first_run:
        logger.info(f"First run - saving {len(all_offers)} offers without sending")
        storage.save(all_offers)
        first_run = False

        channel = bot.get_channel(config.discord.channel_id)
        if channel and isinstance(channel, discord.TextChannel):
            await channel.send(
                f"🚗 **Golf 5 Parts Bot started!**\n"
                f"Watching queries: {', '.join(config.search_queries)}\n"
                f"Loaded {len(all_offers)} existing listings.\n"
                f"Checking every {config.refresh_interval_minutes} minutes."
            )
        return

    if new_offers:
        channel = bot.get_channel(config.discord.channel_id)
        if channel and isinstance(channel, discord.TextChannel):
            await channel.send(f"🆕 **{len(new_offers)} new listing{'s' if len(new_offers) != 1 else ''}!**")
            await send_offers_to_channel(channel, new_offers)
            storage.save(new_offers)

            try:
                await channel.edit(topic=f"Last check: {datetime.now().strftime('%d.%m. %H:%M')}")
            except discord.Forbidden:
                pass


@bot.event
async def on_ready():
    global storage, scraper

    logger.info(f"Logged in as {bot.user}")

    storage = OffersStorage(config.found_offers_file)
    scraper = ScraperBazos(config.search_queries)

    logger.info(f"Storage loaded with {storage.count()} known offers")
    logger.info(f"Monitoring queries: {config.search_queries}")

    check_offers.start()


@bot.command(name="status")
async def status(ctx):
    if storage:
        await ctx.send(
            f"📊 **Status**\n"
            f"Known listings: {storage.count()}\n"
            f"Watched queries: {len(config.search_queries)}\n"
            f"Check interval: {config.refresh_interval_minutes} min"
        )


@bot.command(name="check")
async def force_check(ctx):
    await ctx.send("🔄 Running check...")
    await check_offers()


def main():
    logger.info("Starting Golf 5 Parts Bot...")
    bot.run(config.discord.token)


if __name__ == "__main__":
    main()
