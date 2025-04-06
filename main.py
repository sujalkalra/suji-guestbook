import os
from datetime import datetime
import pytz
from supabase import create_client
from dotenv import load_dotenv
from fasthtml.common import *

# Load environment variables
load_dotenv()

# Constants
MAX_NAME_CHAR = 30  # Increased for more flexibility
MAX_MESSAGE_CHAR = float('inf')
TIMESTAMP_FMT = "%Y-%m-%d %I:%M:%S %p %Z"

# Supabase Credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# FastAPI App
app, rt = fast_app(
    hdrs=(
        Link(rel='icon', type='image/x-icon', href="/assets/me.ico"),
        Link(rel='preconnect', href="https://fonts.googleapis.com"),
        Link(rel='preconnect', href="https://fonts.gstatic.com", crossorigin=""),
        Link(rel='stylesheet', href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap"),
        Link(rel='stylesheet', href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css"),
    )
)

# Global timezone object (optimization)
IST_TZ = pytz.timezone("Asia/Kolkata")

def get_ist_time():
    return datetime.now(IST_TZ)

def add_message(name, message):
    timestamp = get_ist_time().strftime(TIMESTAMP_FMT)
    supabase.table("myGuestbook").insert(
        {"name": name, "message": message, "timestamp": timestamp}
    ).execute()

def get_messages(limit=10):
    response = (
        supabase.table("myGuestbook")
        .select("*")
        .order("id", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data

def render_message(entry):
    return Div(
        Div(
            Span(entry['name'], _class="message-author"),
            Span(entry['timestamp'], _class="message-time"),
            _class="message-header"
        ),
        P(entry['message'], _class="message-content"),
        _class="message-card"
    )

def render_message_list():
    messages = get_messages()
    message_elements = [render_message(entry) for entry in messages]
    if not message_elements:
        message_elements = [Div("No messages yet. Be the first to leave a message!", _class="empty-message")]
    
    return Div(*message_elements, id="message-list")

def render_theme_toggle():
    toggle_script = Script("""
    document.addEventListener('DOMContentLoaded', function() {
        // Check for saved theme preference or use preferred color scheme
        const currentTheme = localStorage.getItem('theme') || 
            (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
        
        // Apply the theme
        document.documentElement.setAttribute('data-theme', currentTheme);
        document.getElementById('theme-toggle').checked = currentTheme === 'dark';
        
        // Handle toggle changes
        document.getElementById('theme-toggle').addEventListener('change', function(e) {
            const theme = e.target.checked ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
        });
    });
    """)
    
    return Div(
        Label(
            Input(type="checkbox", id="theme-toggle", _class="theme-toggle-input"),
            Span(_class="theme-toggle-slider"),
            _class="theme-toggle"
        ),
        toggle_script,
        _class="theme-toggle-container"
    )

def render_content():
    # Header section
    header = Header(
        Div(
            H1("Sujal's Guestbook", _class="site-title"),
            render_theme_toggle(),
            _class="header-content"
        ),
        _class="site-header"
    )
    
    # Form section
    form = Form(
        Div(
            Input(
                type="text", name="name", placeholder="Your Name",
                required=True, maxlength=MAX_NAME_CHAR,
                _class="form-input"
            ),
            Div(
                Textarea(
                    placeholder="Leave a message...", name="message",
                    required=True, rows="3", _class="form-textarea"
                ),
                _class="textarea-container"
            ),
            Button(
                I(_class="fas fa-paper-plane"), " Send Message", 
                type="submit", _class="submit-button"
            ),
            _class="form-group"
        ),
        method="post",
        hx_post="/submit-message",
        hx_target="#message-list",
        hx_swap="outerHTML",
        hx_on__after_request="this.reset()",
        _class="guestbook-form"
    )
    
    # Messages section
    messages_section = Section(
        H2("Recent Messages", _class="section-title"),
        render_message_list(),
        _class="messages-section"
    )
    
    # Footer
    footer = Footer(
        Div(
            P("Made with ", Span("❤️", _class="heart"), " by ", 
              A("Sujal", href="https://github.com/sujalkalra", target="_blank")),
            P(
                A(I(_class="fab fa-github"), " GitHub", 
                  href="https://github.com/sujalkalra", target="_blank", _class="footer-link"),
                " | ",
                A("Try New Version", href="https://sujiguestbook2.vercel.app", 
                  target="_blank", _class="footer-link")
            ),
            _class="footer-content"
        ),
        _class="site-footer"
    )

    css_style = Style("""
    :root {
        --bg-color: #f9f9f9;
        --text-color: #333;
        --primary-color: #4a6fa5;
        --secondary-color: #6c757d;
        --accent-color: #47a3f3;
        --border-color: #e0e0e0;
        --card-bg: #ffffff;
        --input-bg: #ffffff;
        --header-bg: #ffffff;
        --footer-bg: #f0f2f5;
        --shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        --hover-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
        --transition: all 0.3s ease;
    }
    
    [data-theme="dark"] {
        --bg-color: #121212;
        --text-color: #e0e0e0;
        --primary-color: #90caf9;
        --secondary-color: #adb5bd;
        --accent-color: #64b5f6;
        --border-color: #333;
        --card-bg: #1e1e1e;
        --input-bg: #2d2d2d;
        --header-bg: #1a1a1a;
        --footer-bg: #1a1a1a;
        --shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        --hover-shadow: 0 10px 15px rgba(0, 0, 0, 0.4);
    }
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Poppins', sans-serif;
        background-color: var(--bg-color);
        color: var(--text-color);
        line-height: 1.6;
        transition: background-color 0.3s ease, color 0.3s ease;
        display: flex;
        flex-direction: column;
        min-height: 100vh;
    }
    
    /* Header Styles */
    .site-header {
        background-color: var(--header-bg);
        box-shadow: var(--shadow);
        padding: 1rem 5%;
        margin-bottom: 2rem;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .site-title {
        color: var(--primary-color);
        font-size: 1.8rem;
        font-weight: 600;
    }
    
    /* Theme Toggle Styles */
    .theme-toggle-container {
        display: flex;
        align-items: center;
    }
    
    .theme-toggle {
        position: relative;
        display: inline-block;
        width: 60px;
        height: 30px;
        margin-left: 10px;
    }
    
    .theme-toggle-input {
        opacity: 0;
        width: 0;
        height: 0;
    }
    
    .theme-toggle-slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: var(--secondary-color);
        transition: var(--transition);
        border-radius: 34px;
    }
    
    .theme-toggle-slider:before {
        position: absolute;
        content: "";
        height: 22px;
        width: 22px;
        left: 4px;
        bottom: 4px;
        background-color: white;
        transition: var(--transition);
        border-radius: 50%;
    }
    
    .theme-toggle-input:checked + .theme-toggle-slider {
        background-color: var(--accent-color);
    }
    
    .theme-toggle-input:checked + .theme-toggle-slider:before {
        transform: translateX(30px);
    }
    
    /* Main Content Styles */
    main {
        max-width: 800px;
        margin: 0 auto;
        padding: 0 1rem;
        flex-grow: 1;
        width: 100%;
    }
    
    .section-title {
        font-size: 1.5rem;
        color: var(--primary-color);
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--accent-color);
    }
    
    /* Form Styles */
    .guestbook-form {
        background-color: var(--card-bg);
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: var(--shadow);
        transition: var(--transition);
    }
    
    .guestbook-form:hover {
        box-shadow: var(--hover-shadow);
    }
    
    .form-group {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .form-input, .form-textarea {
        width: 100%;
        padding: 0.8rem 1rem;
        border: 1px solid var(--border-color);
        border-radius: 6px;
        background-color: var(--input-bg);
        color: var(--text-color);
        font-family: 'Poppins', sans-serif;
        transition: var(--transition);
    }
    
    .form-input:focus, .form-textarea:focus {
        outline: none;
        border-color: var(--accent-color);
        box-shadow: 0 0 0 3px rgba(71, 163, 243, 0.2);
    }
    
    .textarea-container {
        position: relative;
    }
    
    .submit-button {
        background-color: var(--primary-color);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.8rem 1.5rem;
        font-weight: 500;
        cursor: pointer;
        transition: var(--transition);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        align-self: flex-start;
    }
    
    .submit-button:hover {
        background-color: var(--accent-color);
        transform: translateY(-2px);
    }
    
    /* Messages Styles */
    .messages-section {
        margin-bottom: 2rem;
    }
    
    .message-card {
        background-color: var(--card-bg);
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow);
        border-left: 4px solid var(--accent-color);
        transition: var(--transition);
    }
    
    .message-card:hover {
        box-shadow: var(--hover-shadow);
    }
    
    .message-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    
    .message-author {
        font-weight: 600;
        color: var(--primary-color);
    }
    
    .message-time {
        font-size: 0.8rem;
        color: var(--secondary-color);
    }
    
    .message-content {
        line-height: 1.6;
        white-space: pre-wrap;
    }
    
    .empty-message {
        text-align: center;
        padding: 2rem;
        color: var(--secondary-color);
        background-color: var(--card-bg);
        border-radius: 8px;
    }
    
    /* Footer Styles */
    .site-footer {
        background-color: var(--footer-bg);
        padding: 1.5rem 5%;
        margin-top: 2rem;
        text-align: center;
    }
    
    .footer-content {
        max-width: 800px;
        margin: 0 auto;
    }
    
    .footer-link {
        color: var(--primary-color);
        text-decoration: none;
        transition: var(--transition);
    }
    
    .footer-link:hover {
        color: var(--accent-color);
        text-decoration: underline;
    }
    
    .heart {
        color: #ff6b6b;
        display: inline-block;
        animation: heartbeat 1.5s infinite;
    }
    
    @keyframes heartbeat {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    
    /* Responsive Styles */
    @media (max-width: 768px) {
        .site-title {
            font-size: 1.5rem;
        }
        
        .guestbook-form, .message-card {
            padding: 1rem;
        }
        
        .submit-button {
            width: 100%;
        }
    }
    """)

    main_content = Main(
        Div(
            header,
            Main(
                Div(
                    P("Welcome to my guestbook! Leave a message and share your thoughts.", _class="welcome-text"),
                    form,
                    messages_section,
                ),
            ),
            footer,
            css_style,
            _class="container"
        )
    )

    return main_content

@rt('/')
def get():
    return Titled("Sujal's Guestbook", render_content())

@rt("/submit-message", methods=["post"])
def post(name: str, message: str):
    add_message(name, message)
    return render_message_list()

@rt('/main-content')
def main_content():
    return HTMLResponse(content=open("main_content.html").read())

# Run the optimized app
serve()
