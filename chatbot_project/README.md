# Django + ChatterBot Terminal Chat Client

A terminal client, built with Django and ChatterBot, that lets you chat with
a machine-learning powered bot directly from the command line.

ChatterBot is a machine-learning based conversational dialog engine: it
learns from a collection of known conversations and generates its replies by
finding the closest known statement to whatever you just typed and
returning the response that historically followed it.

## Project layout

```
chatbot_project/
├── manage.py                  # Django's command-line utility
├── requirements.txt           # Manifest of required Python packages
├── screenshot.png             # Sample terminal session
├── chatbot_project/
│   ├── settings.py            # Django settings + CHATTERBOT configuration
│   ├── urls.py
│   └── wsgi.py / asgi.py
└── chatbot/                   # The Django app containing the chat client
    ├── models.py
    ├── apps.py
    └── management/
        └── commands/
            └── chat.py        # The terminal chat loop (the actual client)
```

## 1. Set up your environment

```bash
# (Recommended) create a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install Django, ChatterBot, and their dependencies
pip install -r requirements.txt
```

> **Note on ChatterBot versions:** The original `chatterbot` package on PyPI
> has been unmaintained since 2020 and will not install on modern Python. This
> project uses the actively maintained fork published under the same
> `chatterbot` PyPI name (`ChatterBot==1.2.14`), which keeps the same public
> API (`ChatBot`, `chatterbot.trainers.ChatterBotCorpusTrainer`, etc.)
> documented at https://chatterbot.readthedocs.io/.

## 2. Prepare the database

ChatterBot stores what it learns in the same SQLite database Django uses.

```bash
python manage.py migrate
```

## 3. Train the bot (first run only)

The `--train` flag trains the bot on ChatterBot's bundled English corpus
(everyday small talk, greetings, etc.) so it has something to draw replies
from the first time you chat with it. You only need to do this once — the
learned conversations are saved to `db.sqlite3` and reused on future runs.

```bash
python manage.py chat --train
```

## 4. Chat with the bot

On every future run you can skip `--train` (though re-running it is
harmless — it just re-trains on the same corpus):

```bash
python manage.py chat
```

Type any message and press Enter to see the bot's reply. Type `quit`,
`exit`, `bye`, or `goodbye` (or press Ctrl+C / Ctrl+D) to end the session.

### Sample session

```
DjangoBot is online! Type 'quit' to end the conversation.
user: Hello
bot: Hi
user: How are you doing?
bot: I am doing well.
user: What is your name?
bot: I am still young by your standards.
user: Are you a robot?
bot: Yes I am.
user: Thank you
bot: Right this way.
user: quit
bot: Goodbye!
```

See `screenshot.png` for a captured terminal session.

## How it works

- **`chatbot_project/settings.py`** — adds the `chatbot` app to
  `INSTALLED_APPS` and defines a `CHATTERBOT` settings dictionary (bot name,
  storage adapter, logic adapters, tagger) that keeps all bot configuration
  in one central place.
- **`chatbot/management/commands/chat.py`** — a Django *management command*
  (the standard Django mechanism for command-line utilities that need access
  to the project's settings and database). It:
  1. Builds a `ChatBot` instance using the settings above.
  2. Optionally trains it on ChatterBot's English corpus (`--train`).
  3. Runs a `while True` loop that reads a line from the terminal, sends it
     to `chatbot.get_response()`, and prints the bot's reply — until an exit
     keyword is typed or the user presses Ctrl+C / Ctrl+D.
- ChatterBot's `SQLStorageAdapter` persists every statement/response pair it
  learns (from training or from live chats) into `db.sqlite3` via
  SQLAlchemy, so the bot keeps its "memory" between runs.

## Coding practices followed

- Every module/function has a docstring explaining *why*, not just *what*.
- Inline comments explain non-obvious configuration choices (e.g. why
  `LowercaseTagger` is used instead of the default POS tagger).
- Configuration (bot name, storage, adapters) is centralized in
  `settings.py` rather than hard-coded inside the command.
- Input is validated (blank lines are ignored) and exceptions from
  Ctrl+C/Ctrl+D are handled gracefully instead of crashing.
- Dependencies are pinned in `requirements.txt` for reproducible installs.
