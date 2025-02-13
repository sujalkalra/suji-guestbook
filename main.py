import os
from datetime import datetime
import pytz
from supabase import create_client
from dotenv import load_dotenv
from fasthtml.common import *
from fasthtml.server import fast_app  # Added missing import
import time

# Load environment variables
load_dotenv()

MAX_NAME_CHAR = 15
MAX_MESSAGE_CHAR = 500
TIMESTAMP_FMT = "%Y-%m-%d %I:%M:%S %p %Z"

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase URL or API Key")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app, rt = fast_app(hdrs=[Link(rel='icon', type='image/x-icon', href="/assets/me.ico")])

def get_ist_time():
    ist_tz = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist_tz)

def add_message(name, message):
    if not name.strip() or not message.strip():
        return
    timestamp = get_ist_time().strftime(TIMESTAMP_FMT)
    supabase.table("myGuestbook").insert(
        {"name": name, "message": message, "timestamp": timestamp}
    ).execute()

def get_messages():
    response = (
        supabase.table("myGuestbook").select("*").order("id", desc=True).execute()
    )
    return response.data if response and hasattr(response, 'data') else []

def render_message(entry):
    return Article(
        Header(f"Name: {entry.get('name', 'Unknown')}"),
        P(entry.get('message', '')),
        Footer(Small(Em(f"Posted: {entry.get('timestamp', 'Unknown')}")))
    )

def render_message_list():
    messages = get_messages()
    return Div(
        *(render_message(entry) for entry in messages),
        id="message-list"
    )

def render_content():
    preloader = Div(
        Div(
            Div(_class="hamster-container",
                Div(_class="hamster",
                    Div(_class="hamster-body",
                        Div(_class="hamster-eye"),
                        Div(_class="hamster-ear"),
                        Div(_class="hamster-nose"),
                        Div(_class="hamster-front-leg"),
                        Div(_class="hamster-back-leg"),
                        Div(_class="hamster-tail"),
                    ),
                ),
                Div(_class="hamster-wheel"),
            ),
            P("Loading...", _class="loading-text"),
            _class="preloader-content"
        ),
        _class="preloader"
    )

    form = Form(
        Fieldset(
            Input(
                type="text",
                name="name",
                placeholder="Name",
                required=True,
                maxlength=MAX_NAME_CHAR,
            ),
            Input(
                type="text",
                name="message",
                placeholder="Message",
                required=True,
                maxlength=MAX_MESSAGE_CHAR,
            ),
            Button("Submit", type="submit"),
            role="group",
        ),
        method="post",
        hx_post="/submit-message",
        hx_target="#message-list",
        hx_swap="outerHTML",
        hx_on_after_request="this.reset()"  # Fixed HTMX attribute ordering
    )

    main_content = Div(
        P(Em("Write something nice!")),
        form,
        Div(
            "Made With 💖 by ",
            A("Sujal", href="https://github.com/sujalkalra", target='_blank'),
        ),
        Hr(),
        render_message_list(),
        id="main-content",
        style="display: none;"
    )

    script = Script(
        """
        document.addEventListener("DOMContentLoaded", function() {
            setTimeout(function() {
                document.querySelector(".preloader").style.display = "none";
                document.querySelector("#main-content").style.display = "block";
            }, 3000);
        });
        """
    )
    
    return Div(preloader, main_content, script)

@rt('/')
def get():
    return Titled("Suji's Guestbook 📚", render_content())

@rt("/submit-message", methods=["post"])
def post(name: str, message: str):
    add_message(name, message)
    return render_message_list()

serve()
