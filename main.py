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
    # Preloader HTML
    preloader_html = Div(
        """
        <!-- From Uiverse.io by Nawsome --> 
        <div aria-label="Orange and tan hamster running in a metal wheel" role="img" class="wheel-and-hamster">
            <div class="wheel"></div>
            <div class="hamster">
                <div class="hamster__body">
                    <div class="hamster__head">
                        <div class="hamster__ear"></div>
                        <div class="hamster__eye"></div>
                        <div class="hamster__nose"></div>
                    </div>
                    <div class="hamster__limb hamster__limb--fr"></div>
                    <div class="hamster__limb hamster__limb--fl"></div>
                    <div class="hamster__limb hamster__limb--br"></div>
                    <div class="hamster__limb hamster__limb--bl"></div>
                    <div class="hamster__tail"></div>
                </div>
            </div>
            <div class="spoke"></div>
        </div>
        """,
        _id="preloader"
    )

    # CSS for preloader
    preloader_css = Style(
        """
        /* From Uiverse.io by Nawsome */ 
        .wheel-and-hamster {
            --dur: 1s;
            position: relative;
            width: 12em;
            height: 12em;
            font-size: 14px;
        }

        .wheel,
        .hamster,
        .hamster div,
        .spoke {
            position: absolute;
        }

        .wheel,
        .spoke {
            border-radius: 50%;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }

        .wheel {
            background: radial-gradient(100% 100% at center,hsla(0,0%,60%,0) 47.8%,hsl(0,0%,60%) 48%);
            z-index: 2;
        }

        .hamster {
            animation: hamster var(--dur) ease-in-out infinite;
            top: 50%;
            left: calc(50% - 3.5em);
            width: 7em;
            height: 3.75em;
            transform: rotate(4deg) translate(-0.8em,1.85em);
            transform-origin: 50% 0;
            z-index: 1;
        }

        .hamster__head {
            animation: hamsterHead var(--dur) ease-in-out infinite;
            background: hsl(30,90%,55%);
            border-radius: 70% 30% 0 100% / 40% 25% 25% 60%;
            box-shadow: 0 -0.25em 0 hsl(30,90%,80%) inset,
                        0.75em -1.55em 0 hsl(30,90%,90%) inset;
            top: 0;
            left: -2em;
            width: 2.75em;
            height: 2.5em;
            transform-origin: 100% 50%;
        }

        .hamster__ear {
            animation: hamsterEar var(--dur) ease-in-out infinite;
            background: hsl(0,90%,85%);
            border-radius: 50%;
            box-shadow: -0.25em 0 hsl(30,90%,55%) inset;
            top: -0.25em;
            right: -0.25em;
            width: 0.75em;
            height: 0.75em;
            transform-origin: 50% 75%;
        }

        .hamster__eye {
            animation: hamsterEye var(--dur) linear infinite;
            background-color: hsl(0,0%,0%);
            border-radius: 50%;
            top: 0.375em;
            left: 1.25em;
            width: 0.5em;
            height: 0.5em;
        }

        .hamster__nose {
            background: hsl(0,90%,75%);
            border-radius: 35% 65% 85% 15% / 70% 50% 50% 30%;
            top: 0.75em;
            left: 0;
            width: 0.2em;
            height: 0.25em;
        }

        .hamster__body {
            animation: hamsterBody var(--dur) ease-in-out infinite;
            background: hsl(30,90%,90%);
            border-radius: 50% 30% 50% 30% / 15% 60% 40% 40%;
            box-shadow: 0.1em 0.75em 0 hsl(30,90%,55%) inset,
                        0.15em -0.5em 0 hsl(30,90%,80%) inset;
            top: 0.25em;
            left: 2em;
            width: 4.5em;
            height: 3em;
            transform-origin: 17% 50%;
            transform-style: preserve-3d;
        }

        .hamster__limb--fr,
        .hamster__limb--fl {
            clip-path: polygon(0 0,100% 0,70% 80%,60% 100%,0% 100%,40% 80%);
            top: 2em;
            left: 0.5em;
            width: 1em;
            height: 1.5em;
            transform-origin: 50% 0;
        }

        .hamster__limb--fr {
            animation: hamsterFRLimb var(--dur) linear infinite;
            background: linear-gradient(hsl(30,90%,80%) 80%,hsl(0,90%,75%) 80%);
            transform: rotate(15deg) translateZ(-1px);
        }

        .hamster__limb--fl {
            animation: hamsterFLLimb var(--dur) linear infinite;
            background: linear-gradient(hsl(30,90%,90%) 80%,hsl(0,90%,85%) 80%);
            transform: rotate(15deg);
        }

        .hamster__limb--br,
        .hamster__limb--bl {
            border-radius: 0.75em 0.75em 0 0;
            clip-path: polygon(0 0,100% 0,100% 30%,70% 90%,70% 100%,30% 100%,40% 90%,0% 30%);
            top: 1em;
            left: 2.8em;
            width: 1.5em;
            height: 2.5em;
            transform-origin: 50% 30%;
        }

        .hamster__limb--br {
            animation: hamsterBRLimb var(--dur) linear infinite;
            background: linear-gradient(hsl(30,90%,80%) 90%,hsl(0,90%,75%) 90%);
            transform: rotate(-25deg) translateZ(-1px);
        }

        .hamster__limb--bl {
            animation: hamsterBLLimb var(--dur) linear infinite;
            background: linear-gradient(hsl(30,90%,90%) 90%,hsl(0,90%,85%) 90%);
            transform: rotate(-25deg);
        }

        .hamster__tail {
            animation: hamsterTail var(--dur) linear infinite;
            background: hsl(0,90%,85%);
            border-radius: 0.25em 50% 50% 0.25em;
            box-shadow: 0 -0.2em 0 hsl(0,90%,75%) inset;
            top: 1.5em;
            right: -0.5em;
            width: 1em;
            height: 0.5em;
            transform: rotate(30deg) translateZ(-1px);
            transform-origin: 0.25em 0.25em;
        }

        .spoke {
            animation: spoke var(--dur) linear infinite;
            background: radial-gradient(100% 100% at center,hsl(0,0%,60%) 4.8%,hsla(0,0%,60%,0) 5%),
                        linear-gradient(hsla(0,0%,55%,0) 46.9%,hsl(0,0%,65%) 47% 52.9%,hsla(0,0%,65%,0) 53%) 50% 50% / 99% 99% no-repeat;
        }

        /* Animations */
        @keyframes hamster {
            from, to {
                transform: rotate(4deg) translate(-0.8em,1.85em);
            }
            50% {
                transform: rotate(0) translate(-0.8em,1.85em);
            }
        }

        @keyframes hamsterHead {
            from, 25%, 50%, 75%, to {
                transform: rotate(0);
            }
            12.5%, 37.5%, 62.5%, 87.5% {
                transform: rotate(8deg);
            }
        }

        @keyframes hamsterEye {
            from, 90%, to {
                transform: scaleY(1);
            }
            95% {
                transform: scaleY(0);
            }
        }

        @keyframes hamsterEar {
            from, 25%, 50%, 75%, to {
                transform: rotate(0);
            }
            12.5%, 37.5%, 62.5%, 87.5% {
                transform: rotate(12deg);
            }
        }

        @keyframes hamsterBody {
            from, 25%, 50%, 75%, to {
                transform: rotate(0);
            }
            12.5%, 37.5%, 62.5%, 87.5% {
                transform: rotate(-2deg);
            }
        }

        @keyframes hamsterFRLimb {
            from, 25%, 50%, 75%, to {
                transform: rotate(50deg) translateZ(-1px);
            }
            12.5%, 37.5%, 62.5%, 87.5% {
                transform: rotate(-30deg) translateZ(-1px);
            }
        }

        @keyframes hamsterFLLimb {
            from, 25%, 50%, 75%, to {
                transform: rotate(-30deg);
            }
            12.5%, 37.5%, 62.5%, 87.5% {
                transform: rotate(50deg);
            }
        }

        @keyframes hamsterBRLimb {
            from, 25%, 50%, 75%, to {
                transform: rotate(-60deg) translateZ(-1px);
            }
            12.5%, 37.5%, 62.5%, 87.5% {
                transform: rotate(20deg) translateZ(-1px);
            }
        }

        @keyframes hamsterBLLimb {
            from, 25%, 50%, 75%, to {
                transform: rotate(20deg);
            }
            12.5%, 37.5%, 62.5%, 87.5% {
                transform: rotate(-60deg);
            }
        }

        @keyframes hamsterTail {
            from, 25%, 50%, 75%, to {
                transform: rotate(30deg) translateZ(-1px);
            }
            12.5%, 37.5%, 62.5%, 87.5% {
                transform: rotate(10deg) translateZ(-1px);
            }
        }

        @keyframes spoke {
            from {
                transform: rotate(0);
            }
            to {
                transform: rotate(-1turn);
            }
        }
        """
    )

    # JavaScript to hide preloader after 7 seconds and show main content
    preloader_js = Script(
        """
        setTimeout(function() {
            document.getElementById('preloader').style.display = 'none';
            document.getElementById('main-content').style.display = 'block';
        }, 7000);
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

    # CSS Styling
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
        """
    )


    # Main content wrapped in a Div that is initially hidden
    main_content = Div(
        id="main-content",
        style="display: none;",  # Initially hidden
        children=[
            P(Em("Write something nice!")),
            form,
            Div(
                children=[
                    "Made With 💖 by ",
                    A("Sujal", href="https://github.com/sujalkalra", target='_blank'),
                ]
            ),
            Hr(),
            render_message_list(),
        ]
    )

    return Div(
        preloader_css,
        preloader_html,
        preloader_js,
        css_style,
        image_with_link,
        floating_button,  # Add floating button
        main_content
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
