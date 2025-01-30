import os
from datetime import datetime
import pytz
from supabase import create_client
from dotenv import load_dotenv
from fasthtml.common import *

@@ -10,68 +10,367 @@

MAX_NAME_CHAR = 15
MAX_MESSAGE_CHAR = 500
TIMESTAMP_FMT = "%Y-%m-%d %I:%M:%S %p %Z"  # Updated to include timezone

# Initialize supabase client
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# Create app with a favicon link
app, rt = fast_app(
    hdrs=(Link(rel='icon', type='image/favicon.ico', href="/assets/me.ico"),),
)

def get_ist_time():
    ist_tz = pytz.timezone("Asia/Kolkata")  # IST timezone
    return datetime.now(ist_tz)

def add_message(name, message):
    # Get current time in IST and format it
    timestamp = get_ist_time().strftime(TIMESTAMP_FMT)
    supabase.table("myGuestbook").insert(
        {"name": name, "message": message, "timestamp": timestamp}
    ).execute()

def get_messages():
    # Sort by id in descending order to get the latest messages first
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
@@ -81,75 +380,63 @@ def render_content():
        hx_on__after_request="this.reset()",
    )

    # Add an image using the 'img' tag from FASTHtml with media queries handled in Python
    image_with_link = A(
        Img(
            src="/assets/me.png", 
            alt="Guestbook Image",  
            _class="guestbook-image"  # Add class to image for styling
        ),
        href="https://github.com/sujalkalra",  # Replace with the link you want
        target="_blank"  # Opens the link in a new tab
    )
    # Add inline media query using FASTHtml's Style component
    css_style = Style(
        """
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
                position: static;  /* Remove absolute positioning */
                display: block;
                margin-left: auto;
                margin-right: auto;
                margin-bottom: 10px;  /* Add space between image and heading */
            }
            /* Align header to center on mobile */
            .guestbook-header {
                text-align: center;
            }
        }
        /* Default styling for desktop */
        .guestbook-header {
            text-align: center;
        }
        """
    )

    return Div(
        css_style,  # Apply the CSS for responsiveness
        image_with_link,
        P(Em("Write something nice!")),
        form,
        Div(
            "Made With 💖 by ",
            A("Sujal", href="https://github.com/sujalkalra", target='_blank'),
        ),
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
