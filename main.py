import os
from datetime import datetime
import pytz
from supabase import create_client
from dotenv import load_dotenv
from fasthtml.common import *

# Load environment variables
load_dotenv()

MAX_NAME_CHAR = 15
MAX_MESSAGE_CHAR = 500
TIMESTAMP_FMT = "%Y-%m-%d %I:%M:%S %p %Z"  # Updated to include timezone

# Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Create app with a favicon link
app, rt = fast_app(
    hdrs=(Link(rel='icon', type='image/favicon.ico', href="/assets/me.ico"),),
)

def get_ist_time():
    ist_tz = pytz.timezone("Asia/Kolkata")  # IST timezone
    return datetime.now(ist_tz)

def add_message(name, message):
    timestamp = get_ist_time().strftime(TIMESTAMP_FMT)
    supabase.table("myGuestbook").insert(
        {"name": name, "message": message, "timestamp": timestamp}
    ).execute()

def get_messages():
    response = (
        supabase.table("myGuestbook").select("*").order("id", desc=True).execute()
    )
    return response.data

def render_message(entry):
    return (
        Article(
            Header(f"Name: {entry['name']}"),
            P(entry['message']),
            Footer(Small(Em(f"Posted: {entry['timestamp']}"))),
        )
    )

def render_message_list():
    messages = get_messages()
    return Div(
        *[render_message(entry) for entry in messages],
        id="message-list",
    )

def render_content():
    preloader = Div("", id="preloader")
    
    script = Script(
        """
        window.onload = function() {
            document.getElementById('preloader').style.display = 'none';
        }
        """
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
        hx_on__after_request="this.reset()",
    )

    css_style = Style(
        """
        #preloader {
            position: fixed;
            width: 100%;
            height: 100%;
            background: #000;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        #preloader::after {
            content: '';
            width: 50px;
            height: 50px;
            border: 5px solid white;
            border-top-color: transparent;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        """
    )
    
    return Div(
        css_style,
        preloader,
        script,
        P(Em("Write something nice!")),
        form,
        Hr(),
        render_message_list(),
    )

@rt('/')
def get():
    return Titled("Suji's Guestbook 📖", render_content()),

@rt("/submit-message", methods=["post"])
def post(name: str, message: str):
    add_message(name, message)
    return render_message_list()

# Serve the application
serve()
