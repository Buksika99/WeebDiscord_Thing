import discord
from discord.ext import commands
from discord.ext.commands import Context
from mysql.connector import Error
from main import connect_to_database, close_database_connection
from fuzzywuzzy import fuzz
import shlex
import os
from dotenv import load_dotenv

# Load environment variables from credentials.env
load_dotenv(".env")
# Access the BOT_TOKEN environment variable
bot_token = os.getenv("BOT_TOKEN")

# Define the intents your bot needs
intents = discord.Intents.default()
intents.typing = False  # Disable typing event (optional)
intents.message_content = True # Enable message content intent

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')


@bot.command(name="print_hello")
async def print_hello(ctx: Context):
    print("Bot received the !print_hello command!")
    await ctx.send("Hello, I've printed something for you!")


@bot.command(name="how_to_use")
async def bot_help(ctx: commands.Context):
    help_message = "To get information about an anime, use the following command:\n"
    help_message += "!get_anime <anime_identifier> [<field1> <field2> ...]\n\n"
    help_message += "Example:\n"
    help_message += "!get_anime \"Attack on Titan\" tags duration finish_year\n"
    help_message += "Please note, that you have to put the Title between \" \" (quotation marks), if the title" \
                    " is more than one word! \n\n"
    help_message += "Available fields you can request:\n"
    help_message += "- Title\n"
    help_message += "- id\n"
    help_message += "- mediaType\n"
    help_message += "- episodes\n"
    help_message += "- duration\n"
    help_message += "- ongoing\n"
    help_message += "- start_year\n"
    help_message += "- finish_year\n"
    help_message += "- Season_of_Release\n"
    help_message += "- description\n"
    help_message += "- studios\n"
    help_message += "- tags\n"
    help_message += "- content_warning\n"
    help_message += "- watched\n"
    help_message += "- watching\n"
    help_message += "- want_to_watch\n"
    help_message += "- dropped\n"
    help_message += "- rating\n"
    help_message += "- votes\n"

    await ctx.send(help_message)


@bot.command(name="get_anime")
async def get_anime(ctx: commands.Context, *, args: str):
    connection = connect_to_database()
    if not connection:
        await ctx.send("Database connection error")
        return

    try:
        cursor = connection.cursor(dictionary=True)
        anime = None

        # Split the input into separate arguments while preserving quoted phrases
        arg_list = shlex.split(args)

        # The first argument should be the anime title
        anime_identifier = arg_list[0]

        # Check if the input is a valid integer (anime ID)
        if anime_identifier.isdigit():
            query = "SELECT * FROM animetrying WHERE id = %s"  # Use the new table name
            cursor.execute(query, (int(anime_identifier),))
            anime = cursor.fetchone()

        # If not a valid ID or anime not found, try to find an exact title match
        if not anime:
            query = "SELECT * FROM animetrying WHERE Title = %s"  # Use the new table name
            cursor.execute(query, (anime_identifier,))
            anime = cursor.fetchone()

        # If no exact match found, try to find a close match by title
        if not anime:
            query = "SELECT * FROM animetrying"  # Use the new table name
            cursor.execute(query)
            anime_titles = [row['Title'] for row in cursor.fetchall()]

            # Use fuzzy matching to find the closest title
            highest_ratio = -1
            closest_match = None
            for title in anime_titles:
                ratio = fuzz.ratio(anime_identifier.lower(), title.lower())
                if ratio > highest_ratio:
                    highest_ratio = ratio
                    closest_match = title

            if closest_match and highest_ratio >= 40:  # Adjust the threshold as needed
                query = "SELECT * FROM animetrying WHERE Title = %s"  # Use the new table name
                cursor.execute(query, (closest_match,))
                anime = cursor.fetchone()

        if anime:
            response_message = f"Title: {anime['Title']}\n"
            default_fields = ['episodes']  # Fields to print by default

            # Check if any additional fields were specified
            if len(arg_list) > 1:
                fields = arg_list[1:]

                for field in fields:
                    field = field.lower()
                    if field == "all":
                        # Include all other fields in the "all" response
                        for column_name, column_value in anime.items():
                            if column_name not in ['Title']:
                                response_message += f"{column_name}: {column_value}\n"
                    elif field == "episodes":
                        default_fields.remove("episodes")  # Remove "episodes" from default fields
                        response_message += f"{field}: {anime[field]}\n"
                    elif field in anime:
                        response_message += f"{field}: {anime[field]}\n"
                    else:
                        await ctx.send(f"Field '{field}' not found")
                        return

            # Add default fields if they haven't been explicitly requested
            for default_field in default_fields:
                response_message += f"{default_field}: {anime[default_field]}\n"

            await ctx.send(response_message)
        else:
            await ctx.send("Anime not found")
    except Error as e:
        print("Error querying database:", e)
        await ctx.send("Database query error")
    finally:
        close_database_connection(connection)




bot.run(bot_token)


