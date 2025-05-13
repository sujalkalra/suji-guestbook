import os
from datetime import datetime
import pytz
from supabase import create_client
from dotenv import load_dotenv
from fasthtml.common import *

# --- Setup ---
load_dotenv()
MAX_NAME_CHAR = 30
MAX_MESSAGE_CHAR = 500
TIMESTAMP_FMT = "%Y-%m-%d %I:%M:%S %p %Z"
IST_TZ = pytz.timezone("Asia/Kolkata")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Utility ---
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

def render_avatar(name):
    initials = "".join([x[0] for x in name.split()][:2]).upper()
    return Div(
        Span(initials, _class="avatar-initials"),
        _class="avatar-circle"
    )

def render_message(entry):
    return Div(
        Div(
            render_avatar(entry['name']),
            Div(
                Span(entry['name'], _class="message-author"),
                Span(entry['timestamp'], _class="message-time"),
                _class="message-meta"
            ),
            _class="message-header-flex"
        ),
        P(entry['message'], _class="message-content"),
        _class="message-card"
    )

def render_message_list():
    messages = get_messages()
    if not messages:
        return Div(
            Div(
                I(_class="far fa-comment-dots empty-icon"),
                H3("No messages yet", _class="empty-title"),
                P("Be the first to leave a message in the guestbook!", _class="empty-text"),
                _class="empty-message"
            ),
            id="message-list"
        )
    return Div(*(render_message(entry) for entry in messages), id="message-list", _class="message-list-container")

def render_theme_toggle():
    toggle_script = Script("""
    document.addEventListener('DOMContentLoaded', function() {
        const themeToggle = document.getElementById('theme-toggle');
        const root = document.documentElement;
        const setTheme = (theme) => {
            root.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
        };
        let theme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
        setTheme(theme);
        themeToggle.checked = theme === 'dark';
        themeToggle.addEventListener('change', function() {
            setTheme(this.checked ? 'dark' : 'light');
        });
    });
    """)
    return Div(
        Label(
            Input(type="checkbox", id="theme-toggle", _class="theme-toggle-input"),
            Span(I(_class="fas fa-moon theme-icon"), I(_class="fas fa-sun theme-icon"), _class="theme-toggle-slider"),
            _class="theme-toggle"
        ),
        toggle_script,
        _class="theme-toggle-container"
    )

# --- Main Content ---
@app.get("/")
def index():
    form = Form(
        Div(
            Input(
                type="text", name="name", placeholder="Your Name", required=True,
                maxlength=MAX_NAME_CHAR, _class="form-input"
            ),
            Textarea(
                placeholder="Leave a message...", name="message", required=True,
                rows=3, maxlength=MAX_MESSAGE_CHAR, _class="form-textarea"
            ),
            Div(
                Span(f"{MAX_MESSAGE_CHAR} characters remaining", id="char-counter", _class="char-counter"),
                _class="textarea-footer"
            ),
            Button(I(_class="fas fa-paper-plane"), " Send", type="submit", _class="submit-button"),
            _class="form-fields"
        ),
        Script(f"""
        document.addEventListener('DOMContentLoaded', function() {{
            const textarea = document.querySelector('.form-textarea');
            const counter = document.getElementById('char-counter');
            const btn = document.querySelector('.submit-button');
            textarea.addEventListener('input', function() {{
                const remain = {MAX_MESSAGE_CHAR} - this.value.length;
                counter.textContent = remain + ' characters remaining';
                btn.disabled = remain < 0 || this.value.trim().length == 0;
                counter.classList.toggle('char-limit-exceeded', remain < 0);
            }});
        }});
        """),
        method="post",
        hx_post="/submit-message",
        hx_target="#message-list",
        hx_swap="outerHTML",
        hx_on__after_request="this.reset();document.getElementById('char-counter').textContent='{MAX_MESSAGE_CHAR} characters remaining';",
        _class="guestbook-form"
    )

    header = Header(
        Div(
            Div(
                I(_class="fas fa-book-open header-icon"),
                H1("Sujal's Guestbook", _class="site-title"),
                _class="title-container"
            ),
            render_theme_toggle(),
            _class="header-content"
        ),
        _class="site-header"
    )

    messages_section = Section(
        Div(
            H2("Recent Messages", _class="section-title"),
            I(_class="fas fa-sync-alt refresh-icon", title="Refresh messages",
              hx_get="/refresh-messages", hx_target="#message-list", hx_swap="outerHTML"),
            _class="section-header"
        ),
        render_message_list(),
        _class="messages-section"
    )

    stats_section = Section(
        Div(
            Div(I(_class="fas fa-users stat-icon"), Div(H3("25+", _class="stat-number"), P("Visitors", _class="stat-label"), _class="stat-text"), _class="stat-item"),
            Div(I(_class="fas fa-comments stat-icon"), Div(H3("100+", _class="stat-number"), P("Messages", _class="stat-label"), _class="stat-text"), _class="stat-item"),
            Div(I(_class="fas fa-heart stat-icon"), Div(H3("Thank You", _class="stat-number"), P("For Visiting", _class="stat-label"), _class="stat-text"), _class="stat-item"),
            _class="stats-container"
        ),
        _class="stats-section"
    )

    footer = Footer(
        Div(
            P("Made with ", Span("❤️", _class="heart"), " by ", A("Sujal", href="https://github.com/sujalkalra", target="_blank", _class="footer-link")),
            Div(
                A(I(_class="fab fa-github"), " GitHub", href="https://github.com/sujalkalra", target="_blank", _class="social-link"),
                A(I(_class="fas fa-code-branch"), " New Version", href="https://sujiguestbook2.vercel.app", target="_blank", _class="social-link"),
                _class="social-links"
            ),
            P("© 2025 Sujal's Guestbook. All rights reserved.", _class="copyright"),
            _class="footer-content"
        ),
        _class="site-footer"
    )

    css_style = Style("""
    :root {
        --primary: #4a6fa5;
        --primary-light: #6ea8fe;
        --primary-dark: #274472;
        --accent: #47a3f3;
        --bg: #f7faff;
        --card: #fff;
        --text: #222;
        --muted: #6c757d;
        --border: #e0e0e0;
        --shadow: 0 4px 16px rgba(74,111,165,0.08);
        --radius: 12px;
        --transition: all 0.2s cubic-bezier(.4,0,.2,1);
    }
    [data-theme="dark"] {
        --primary: #90caf9;
        --primary-light: #b6e0fe;
        --primary-dark: #274472;
        --accent: #64b5f6;
        --bg: #181c24;
        --card: #23293a;
        --text: #e0e0e0;
        --muted: #adb5bd;
        --border: #333;
        --shadow: 0 4px 16px rgba(74,111,165,0.18);
    }
    body {
        background: var(--bg);
        color: var(--text);
        font-family: 'Poppins', sans-serif;
        min-height: 100vh;
        margin: 0;
        display: flex;
        flex-direction: column;
    }
    .site-header {
        background: var(--card);
        box-shadow: var(--shadow);
        padding: 1.5rem 0 1rem 0;
        margin-bottom: 2rem;
        position: sticky;
        top: 0;
        z-index: 100;
        border-bottom: 1px solid var(--border);
    }
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 900px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    .title-container {
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }
    .header-icon {
        font-size: 1.7rem;
        color: var(--primary);
    }
    .site-title {
        color: var(--primary);
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -1px;
    }
    .theme-toggle-container { display: flex; align-items: center; }
    .theme-toggle { position: relative; width: 54px; height: 28px; display: inline-block; }
    .theme-toggle-input { opacity: 0; width: 0; height: 0; }
    .theme-toggle-slider {
        background: var(--muted);
        border-radius: 34px;
        position: absolute; top: 0; left: 0; right: 0; bottom: 0;
        cursor: pointer; transition: var(--transition);
        display: flex; align-items: center; justify-content: space-between; padding: 0 8px;
    }
    .theme-toggle-input:checked + .theme-toggle-slider { background: var(--primary); }
    .theme-icon { font-size: 1.1rem; color: #fff; opacity: 0.7; }
    .guestbook-form, .messages-section, .stats-section { max-width: 98vw; padding: 1rem; }
        .site-header, .site-footer { padding-left: 0.5rem; padding-right: 0.5rem; }
    }
    """)

    return Div(
        header,
        Div(
            P("Welcome to my guestbook! Leave a message and connect with others. Your thoughts and feedback are greatly appreciated!", _class="welcome-text"),
            form,
            messages_section,
            stats_section,
            _class="container"
        ),
        footer,
        css_style
    )

@app.post("/submit-message")
def submit_message(name: str = Form(...), message: str = Form(...)):
    if len(name) > MAX_NAME_CHAR:
        name = name[:MAX_NAME_CHAR]
    if len(message) > MAX_MESSAGE_CHAR:
        message = message[:MAX_MESSAGE_CHAR]
    add_message(name, message)
    return render_message_list()

@app.get("/refresh-messages")
def refresh_messages():
    return render_message_list()

serve()
