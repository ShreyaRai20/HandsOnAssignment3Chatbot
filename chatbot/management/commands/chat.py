"""
Django management command: chat

This command is the terminal client for the assignment. Running

    python manage.py chat

starts an interactive, text-based conversation loop in the terminal between
the user and a ChatterBot instance. ChatterBot is a machine-learning based
conversational engine: it looks at a database of known statement/response
pairs, finds the closest match to whatever the user just typed, and returns
the response that historically followed that statement.

Why a Django *management command* instead of a plain script?
--------------------------------------------------------------
Management commands are the standard Django way to run one-off or
interactive tasks (like this terminal chat session) while still having
access to the full Django project configuration (settings.py, installed
apps, and -- most importantly here -- the CHATTERBOT settings dictionary and
Django's database connection, which ChatterBot reuses for storage).
"""

from django.conf import settings
from django.core.management.base import BaseCommand

from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.tagging import LowercaseTagger


class Command(BaseCommand):
    # Short description shown when the user runs `python manage.py help`
    help = "Start an interactive terminal chat session with the ChatterBot bot."

    def add_arguments(self, parser):
        """
        Register optional command-line flags for this management command.

        --train : if passed, the bot will (re)train itself on the built-in
                  English conversation corpus before the chat loop starts.
                  This is useful the very first time the app is run, since a
                  freshly created database has no prior conversations for
                  the bot to draw responses from.
        """
        parser.add_argument(
            "--train",
            action="store_true",
            help="Train the bot on the ChatterBot English corpus before chatting.",
        )

    def handle(self, *args, **options):
        """
        Entry point Django calls when `python manage.py chat` is executed.
        """

        # ------------------------------------------------------------------
        # 1. Create the ChatBot instance.
        #    We pull its configuration (name, storage adapter, logic
        #    adapters) from settings.CHATTERBOT so that the bot's setup
        #    lives in one central place (settings.py) rather than being
        #    hard-coded here.
        # ------------------------------------------------------------------
        chatbot = ChatBot(
            settings.CHATTERBOT["name"],
            storage_adapter=settings.CHATTERBOT["storage_adapter"],
            database_uri=settings.CHATTERBOT["database_uri"],
            logic_adapters=settings.CHATTERBOT["logic_adapters"],
            # LowercaseTagger avoids requiring a separately downloaded
            # spaCy language model (see comment in settings.py).
            tagger=LowercaseTagger,
        )

        # ------------------------------------------------------------------
        # 2. Optionally train the bot.
        #    ChatterBotCorpusTrainer loads a bundled set of example English
        #    conversations (greetings, small talk, etc.) and stores them via
        #    the configured storage adapter, so the bot has something to
        #    match against right away.
        # ------------------------------------------------------------------
        if options["train"]:
            self.stdout.write(self.style.WARNING("Training bot on English corpus..."))
            trainer = ChatterBotCorpusTrainer(chatbot)
            trainer.train("chatterbot.corpus.english")
            self.stdout.write(self.style.SUCCESS("Training complete.\n"))

        # ------------------------------------------------------------------
        # 3. Run the interactive terminal chat loop.
        #    We keep reading lines from the user, feed each one to the bot,
        #    and print the bot's generated reply, until the user types an
        #    exit keyword or presses Ctrl+C / Ctrl+D.
        # ------------------------------------------------------------------
        exit_words = {"quit", "exit", "bye", "goodbye"}

        self.stdout.write(self.style.SUCCESS(
            f"\n{settings.CHATTERBOT['name']} is online! "
            f"Type 'quit' to end the conversation.\n"
        ))

        while True:
            try:
                # Prompt the user and read one line of input from the terminal.
                user_input = input("user: ").strip()
            except (EOFError, KeyboardInterrupt):
                # Gracefully handle Ctrl+D / Ctrl+C instead of a stack trace.
                self.stdout.write("\nbot: Goodbye!")
                break

            if not user_input:
                # Ignore blank lines instead of sending them to the bot.
                continue

            if user_input.lower() in exit_words:
                self.stdout.write("bot: Goodbye!")
                break

            # Ask ChatterBot to generate a response to what the user typed.
            response = chatbot.get_response(user_input)

            # ChatterBot's Statement object stringifies to just the reply
            # text, so we can print it directly.
            self.stdout.write(f"bot: {response}")
