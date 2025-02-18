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
    # Preloader
    preloader = Div(
        Div(_class="spinner"),  # Spinner animation
        _class="preloader",
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

    # Image with link
    image_with_link = A(
        Img(
            src="/assets/me.png",
            alt="Guestbook Image",
            _class="guestbook-image"
        ),
        href="https://github.com/sujalkalra",
        target="_blank"
    )

    # Floating neon button
    floating_button = A(
        "Try New Version",
        href="https://sujiguestbook2.vercel.app",  # Replace with actual link
        _class="floating-neon-button"
    )

    # JavaScript to hide the preloader
    js_script = Script(
        """
        window.addEventListener("load", function () {
            document.querySelector(".preloader").style.display = "none";
            document.querySelector(".content").style.display = "block";
        });
        """
    )

    # CSS Styling
    css_style = Style(
        """
        /* Preloader Styling */
        .preloader {
            position: fixed;
            width: 100%;
            height: 100%;
            background: black;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }

        .spinner {
            width: 50px;
            height: 50px;
            border: 5px solid rgba(255, 255, 255, 0.3);
            border-top: 5px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* Default styling for desktop and larger screens */
        .guestbook-image {
            width: 50px;
            height: 50px;
            position: absolute;
            top: 20px;
            right: 40px;
        }

        /* Center the image and make it larger on mobile */
        @media (max-width: 600px) {
            .guestbook-image {
                width: 100px;
                height: 100px;
                position: static;
                display: block;
                margin-left: auto;
                margin-right: auto;
                margin-bottom: 10px;
            }
            .guestbook-header {
                text-align: center;
            }
        }

        /* Floating Neon Button */
        .floating-neon-button {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: linear-gradient(90deg, #ff00ff, #00ffff);
            color: white;
            font-family: 'Orbitron', sans-serif;
            font-size: 14px;
            padding: 12px 20px;
            border: 2px solid white;
            border-radius: 8px;
            text-decoration: none;
            box-shadow: 0 0 10px #ff00ff, 0 0 20px #00ffff;
            transition: all 0.3s ease-in-out;
        }

        .floating-neon-button:hover {
            box-shadow: 0 0 20px #ff00ff, 0 0 30px #00ffff;
            transform: scale(1.1);
        }

        /* Hide content initially */
        .content {
            display: none;
        }
        """
    )

    return Div(
        css_style,
        preloader,  # Add preloader
        js_script,  # Add JavaScript
        Div(
            image_with_link,
            floating_button,  # Add floating button
            P(Em("Write something nice!")),
            form,
            Div(
                "Made With 💖 by ",
                A("Sujal", href="https://github.com/sujalkalra", target='_blank'),
            ),
            Hr(),
            render_message_list(),
            _class="content"  # Wrapped in a hidden div
        ),
    )

@rt('/')
def get():
    return Titled("Suji's Guestbook 📖", render_content()),

@rt("/submit-message", methods=["post"])
def post(name: str, message: str):
    add_message(name, message)
    return render_message_list()

@rt('/main-content')
def main_content():
    return HTMLResponse(content=open("main_content.html").read()),  # Serve your main content here

# Serve the application
serve()
