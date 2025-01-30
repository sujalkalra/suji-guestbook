import os
from datetime import datetime
import pytz
from pymongo import MongoClient
from dotenv import load_dotenv
from fasthtml.common import *

# Load environment variables
load_dotenv()

MAX_NAME_CHAR = 15
MAX_MESSAGE_CHAR = 500
TIMESTAMP_FMT = "%Y-%m-%d %I:%M:%S %p %Z"

# Initialize MongoDB client
mongo_client = MongoClient(os.getenv("MONGO_URI"))
db = mongo_client['sujalkiguestbook']
collection = db['Forks']

# Create app with a favicon link
app, rt = fast_app(
    hdrs=(Link(rel='icon', type='image/favicon.ico', href="/assets/me.ico"),),
)


def get_ist_time():
    ist_tz = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist_tz)


def add_message(name, message):
    if not name or not message:
        raise ValueError("Name and message cannot be empty")

    name = name.strip()[:MAX_NAME_CHAR]
    message = message.strip()[:MAX_MESSAGE_CHAR]

    timestamp = get_ist_time().strftime(TIMESTAMP_FMT)
    try:
        collection.insert_one(
            {"name": name, "message": message, "timestamp": timestamp}
        )
    except Exception as e:
        print(f"Database error: {e}")
        raise


def get_messages():
    try:
        messages = list(collection.find().sort("timestamp", -1))
        return messages
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return []


def render_message(entry):
    return (
        Article(
            Header(f"Name: {entry.get('name', 'Anonymous')}"),
            P(
                entry.get('message', 'No message'),
                _class="message-content",
                **{"_hx-on:load": """
                    if(this.scrollHeight > this.clientHeight) {
                        this.classList.add('scrollable');
                    }
                """}
            ),
            Footer(Small(Em(f"Posted: {entry.get('timestamp', 'Unknown time')}"))),
            _class="message-card"
        )
    )


def render_message_list():
    messages = get_messages()
    return Div(
        Div(
            *[render_message(entry) for entry in messages],
            _class="message-grid"
        ),
        id="message-list",
    )


def render_content():
    css_style = Style(
        """
        :root {
            --primary-color: #6366f1;
            --primary-light: #818cf8;
            --primary-dark: #4f46e5;
            --secondary-color: #10b981;
            --accent-color: #f472b6;
            --background: #f8fafc;
            --card-bg: #ffffff;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --gradient: linear-gradient(135deg, var(--primary-color), var(--accent-color));
        }

        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            color: var(--text-primary);
            background: var(--background);
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(99, 102, 241, 0.1) 0%, transparent 20%),
                radial-gradient(circle at 90% 80%, rgba(244, 114, 182, 0.1) 0%, transparent 20%);
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }

        .guestbook-header {
            text-align: center;
            margin-bottom: 40px;
            padding: 20px;
            background: var(--gradient);
            border-radius: 16px;
            color: white;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            box-shadow: var(--shadow);
        }

        .guestbook-header h1 {
            margin: 0;
            font-size: 2.5em;
        }

        .guestbook-image {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            box-shadow: var(--shadow);
            transition: all 0.3s ease;
            border: 3px solid white;
            display: block;
            margin: 20px auto;
        }

        .guestbook-image:hover {
            transform: scale(1.1) rotate(5deg);
        }

        /* Form Layout and Styling */
        form {
            background: var(--card-bg);
            padding: 30px;
            border-radius: 16px;
            box-shadow: var(--shadow);
            margin: 20px auto;
            border: 1px solid var(--border-color);
            max-width: 600px;
        }

        fieldset {
            border: none;
            padding: 0;
            margin: 0;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .input-group {
            display: flex;
            gap: 15px;
            align-items: center;
        }

        input[name="name"] {
            flex: 1;
            min-width: 150px;
            max-width: 200px;
        }

        input[name="message"] {
            flex: 2;
        }

        input[type="text"] {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid var(--border-color);
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s ease;
            background: var(--background);
            height: 45px;
        }

        input[type="text"]:focus {
            border-color: var(--primary-color);
            outline: none;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
        }

        button[type="submit"] {
            width: 100%;
            height: 45px;
            background: var(--gradient);
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            -webkit-border-radius: 10px;
            -moz-border-radius: 10px;
        }

        button[type="submit"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.3);
        }

        button[type="submit"]:active {
            transform: translateY(1px);
        }

        /* Message Grid Layout */
        .message-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }

        .message-card {
            border: 1px solid var(--border-color);
            padding: 25px;
            border-radius: 16px;
            background: var(--card-bg);
            box-shadow: var(--shadow);
            transition: all 0.3s ease;
            position: relative;
            height: 300px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .message-card::before {
            content: '';
            position: absolute;
            top: -1px;
            left: -1px;
            width: calc(100% + 2px);
            height: 4px;
            background: var(--gradient);
            border-radius: 16px 16px 0 0;
        }

        .message-card header {
            color: var(--primary-color);
            font-weight: 600;
            margin-bottom: 12px;
            font-size: 1.2em;
            flex-shrink: 0;
        }

        .message-card .message-content {
            margin: 12px 0;
            color: var(--text-primary);
            line-height: 1.7;
            overflow-y: auto;
            flex-grow: 1;
            padding-right: 10px;
        }

        .message-card .message-content::-webkit-scrollbar {
            width: 6px;
        }

        .message-card .message-content::-webkit-scrollbar-track {
            background: var(--border-color);
            border-radius: 3px;
        }

        .message-card .message-content::-webkit-scrollbar-thumb {
            background-color: var(--primary-light);
            border-radius: 3px;
        }

        .message-card footer {
            color: var(--text-secondary);
            font-size: 0.9em;
            margin-top: 15px;
            padding-top: 12px;
            border-top: 2px solid var(--border-color);
            flex-shrink: 0;
        }

        .message-content.scrollable::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 20px;
            background: linear-gradient(transparent, var(--card-bg));
            pointer-events: none;
        }

        /* Dark Mode */
        @media (prefers-color-scheme: dark) {
            :root {
                --background: #0f172a;
                --card-bg: #1e293b;
                --text-primary: #e2e8f0;
                --text-secondary: #94a3b8;
                --border-color: #334155;
            }

            input[type="text"] {
                background: #1e293b;
                color: var(--text-primary);
            }
        }

        /* Mobile Adjustments */
        @media (max-width: 768px) {
            .input-group {
                flex-direction: column;
            }

            input[name="name"] {
                max-width: 100%;
            }

            form {
                padding: 20px;
                margin: 20px 10px;
            }

            .guestbook-header h1 {
                font-size: 2em;
            }
        }
        """
    )

    form = Form(
        Fieldset(
            Div(
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
                    placeholder="Write something nice!",
                    required=True,
                    maxlength=MAX_MESSAGE_CHAR,
                ),
                _class="input-group"
            ),
            Button("✨ Send Message", type="submit"),
            role="group",
        ),
        method="post",
        hx_post="/submit-message",
        hx_target="#message-list",
        hx_swap="outerHTML",
        hx_on__after_request="this.reset()",
    )

    image_with_link = A(
        Img(
            src="/assets/me.png",
            alt="Guestbook Image",
            _class="guestbook-image"
        ),
        href="https://github.com/sujalkalra",
        target="_blank"
    )

    return Div(
        css_style,
        Div(
            H1("Suji's Guestbook 📖"),
            _class="guestbook-header"
        ),
        image_with_link,
        form,
        Div(
            "Made With 💖 by ",
            A("Sujal", href="https://github.com/sujalkalra", target='_blank'),
            _class="text-center"
        ),
        Hr(),
        render_message_list(),
    )


@rt('/')
def get():
    return render_content()


@rt("/submit-message", methods=["post"])
def post(name: str, message: str):
    try:
        add_message(name, message)
        return render_message_list()
    except ValueError as ve:
        return Div(
            P(f"Error: {ve}"),
            id="message-list"
        )
    except Exception as e:
        return Div(
            P(f"Error: Could not submit message. Please try again. Details: {e}"),
            id="message-list"
        )


# Check MongoDB connection
try:
    mongo_client.server_info()  # Check if the connection is valid
except Exception as e:
    raise EnvironmentError(f"Database connection error: {e}")

if not os.getenv("MONGO_URI"):
    raise EnvironmentError("Missing required environment variable: MONGO_URI")

serve()
