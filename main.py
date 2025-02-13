import os
from datetime import datetime
import pytz
from supabase import create_client
from dotenv import load_dotenv
from fasthtml.common import *
import time

# Load environment variables
load_dotenv()

MAX_NAME_CHAR = 15
MAX_MESSAGE_CHAR = 500
TIMESTAMP_FMT = "%Y-%m-%d %I:%M:%S %p %Z"

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app, rt = fast_app(
    hdrs=(Link(rel='icon', type='image/favicon.ico', href="/assets/me.ico"),),
)

def get_ist_time():
    ist_tz = pytz.timezone("Asia/Kolkata")
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
    # Custom Preloader (Hamster Wheel Animation)
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
        hx_on__after_request="this.reset()",
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
            }, 7000);
        });
        """
    )

    css_style = Style(
        """
        .preloader {
            position: fixed;
            width: 100%;
            height: 100%;
            background: black;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            flex-direction: column;
        }
        .preloader-content {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .hamster-container {
            position: relative;
            width: 80px;
            height: 80px;
        }
        .hamster {
            position: absolute;
            width: 50px;
            height: 30px;
            background: orange;
            border-radius: 50%;
            animation: run 1s linear infinite;
        }
        .hamster-eye, .hamster-ear, .hamster-nose {
            position: absolute;
            width: 5px;
            height: 5px;
            background: white;
            border-radius: 50%;
        }
        .hamster-eye { top: 5px; left: 35px; }
        .hamster-ear { top: -5px; left: 20px; background: pink; }
        .hamster-nose { top: 15px; left: 48px; }
        .hamster-wheel {
            position: absolute;
            width: 80px;
            height: 80px;
            border: 5px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        @keyframes run {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }
        """
    )
    
    return Div(css_style, preloader, main_content, script)

@rt('/')
def get():
    return Titled("Suji's Guestbook 📚", render_content())

@rt("/submit-message", methods=["post"])
def post(name: str, message: str):
    add_message(name, message)
    return render_message_list()

serve()
