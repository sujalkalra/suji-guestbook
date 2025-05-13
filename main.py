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
            Span(
                I(_class="fas fa-moon theme-icon moon"),
                I(_class="fas fa-sun theme-icon sun"),
                _class="theme-toggle-slider"
            ),
            _class="theme-toggle"
        ),
        toggle_script,
        _class="theme-toggle-container"
    )

# --- Main Content ---
app, rt = fast_app(
    hdrs=(
        Link(rel='icon', type='image/x-icon', href="/assets/me.ico"),
        Link(rel='preconnect', href="https://fonts.googleapis.com"),
        Link(rel='preconnect', href="https://fonts.gstatic.com", crossorigin=""),
        Link(rel='stylesheet', href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap"),
        Link(rel='stylesheet', href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css"),
    )
)

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
            Button(
                I(_class="fas fa-paper-plane"), " Send",
                type="submit", _class="submit-button"
            ),
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
        _class="guestbook-form glass-card"
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
        _class="site-header glass-card"
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
            Div(I(_class="fas fa-users stat-icon"), Div(H3("25+", _class="stat-number"), P("Visitors", _class="stat-label"), _class="stat-text"), _class="stat-item glass-card"),
            Div(I(_class="fas fa-comments stat-icon"), Div(H3("100+", _class="stat-number"), P("Messages", _class="stat-label"), _class="stat-text"), _class="stat-item glass-card"),
            Div(I(_class="fas fa-heart stat-icon"), Div(H3("Thank You", _class="stat-number"), P("For Visiting", _class="stat-label"), _class="stat-text"), _class="stat-item glass-card"),
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
        _class="site-footer glass-card"
    )

    css_style = Style("""
    :root {
        --primary: #4a6fa5;
        --primary-light: #6ea8fe;
        --primary-dark: #274472;
        --accent: #47a3f3;
        --bg: #e9f0fa;
        --card: #fff;
        --glass: rgba(255,255,255,0.65);
        --glass-dark: rgba(35,41,58,0.65);
        --text: #23293a;
        --muted: #6c757d;
        --border: #e0e0e0;
        --shadow: 0 8px 32px rgba(74,111,165,0.13);
        --radius: 18px;
        --transition: all 0.2s cubic-bezier(.4,0,.2,1);
    }
    [data-theme="dark"] {
        --primary: #90caf9;
        --primary-light: #b6e0fe;
        --primary-dark: #274472;
        --accent: #64b5f6;
        --bg: #181c24;
        --card: #23293a;
        --glass: rgba(35,41,58,0.65);
        --glass-dark: rgba(35,41,58,0.85);
        --text: #e0e0e0;
        --muted: #adb5bd;
        --border: #333;
        --shadow: 0 8px 32px rgba(74,111,165,0.18);
    }
    body {
        background: linear-gradient(135deg, var(--bg) 60%, var(--primary-light) 100%);
        color: var(--text);
        font-family: 'Inter', 'Poppins', sans-serif;
        min-height: 100vh;
        margin: 0;
        display: flex;
        flex-direction: column;
        align-items: stretch;
    }
    .glass-card {
        background: var(--glass);
        box-shadow: var(--shadow);
        border-radius: var(--radius);
        border: 1px solid var(--border);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
    }
    .site-header {
        margin-bottom: 2rem;
        position: sticky;
        top: 0;
        z-index: 100;
        border-bottom: 1px solid var(--border);
        padding: 1.5rem 0 1rem 0;
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
        filter: drop-shadow(0 2px 8px var(--primary-light));
    }
    .site-title {
        color: var(--primary);
        font-size: 2.1rem;
        font-weight: 700;
        letter-spacing: -1px;
        text-shadow: 0 2px 8px rgba(74,111,165,0.07);
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
    .theme-icon { font-size: 1.1rem; color: #fff; opacity: 0.7; transition: color 0.3s;}
    .theme-toggle-slider .moon { opacity: 1; }
    .theme-toggle-slider .sun { opacity: 0.7; }
    .theme-toggle-input:checked + .theme-toggle-slider .moon { opacity: 0.7; }
    .theme-toggle-input:checked + .theme-toggle-slider .sun { opacity: 1; }
    .guestbook-form {
        margin: 0 auto 2.5rem auto;
        max-width: 500px;
        padding: 2.2rem 2.5rem 1.7rem 2.5rem;
        transition: var(--transition);
    }
    .form-fields { display: flex; flex-direction: column; gap: 1.2rem; }
    .form-input, .form-textarea {
        width: 100%; padding: 1rem 1.2rem;
        border: 1.5px solid var(--border);
        border-radius: var(--radius);
        background: var(--glass-dark);
        color: var(--text);
        font-size: 1.08rem;
        font-family: inherit;
        transition: var(--transition);
        margin-bottom: 0.2rem;
        box-shadow: 0 2px 8px rgba(74,111,165,0.04);
    }
    .form-input:focus, .form-textarea:focus {
        outline: none;
        border-color: var(--primary);
        box-shadow: 0 0 0 2px var(--primary-light);
    }
    .textarea-footer {
        display: flex; justify-content: flex-end; font-size: 0.97rem;
        color: var(--muted);
    }
    .char-limit-exceeded { color: #e63946; }
    .submit-button {
        background: linear-gradient(90deg, var(--primary), var(--accent));
        color: #fff;
        border: none;
        border-radius: var(--radius);
        padding: 0.9rem 1.7rem;
        font-weight: 600;
        font-size: 1.13rem;
        cursor: pointer;
        box-shadow: var(--shadow);
        transition: var(--transition);
        margin-top: 0.5rem;
        display: flex; align-items: center; gap: 0.7rem;
        letter-spacing: 0.5px;
        position: relative;
        overflow: hidden;
    }
    .submit-button:hover:not(:disabled) {
        background: linear-gradient(90deg, var(--primary-dark), var(--primary));
        transform: translateY(-2px) scale(1.03);
        box-shadow: 0 8px 24px rgba(74,111,165,0.13);
    }
    .submit-button:disabled { opacity: 0.6; cursor: not-allowed; }
    .messages-section { margin: 2.5rem auto 2rem auto; max-width: 700px; }
    .section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.2rem; }
    .section-title { font-size: 1.3rem; color: var(--primary); font-weight: 600; }
    .refresh-icon { color: var(--primary); cursor: pointer; font-size: 1.1rem; transition: var(--transition);}
    .refresh-icon:hover { color: var(--accent); transform: rotate(180deg);}
    .message-list-container { display: flex; flex-direction: column; gap: 1.2rem; }
    .message-card {
        background: var(--glass);
        border-radius: var(--radius);
        box-shadow: var(--shadow);
        padding: 1.2rem 1.5rem;
        border: 1px solid var(--border);
        display: flex; flex-direction: column;
        animation: fadeIn 0.5s;
        transition: var(--transition);
    }
    .message-header-flex { display: flex; align-items: center; gap: 1rem; margin-bottom: 0.3rem;}
    .avatar-circle {
        width: 44px; height: 44px; border-radius: 50%;
        background: linear-gradient(135deg, var(--primary-light), var(--primary));
        display: flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 1.2rem; color: #fff; box-shadow: 0 2px 8px rgba(74,111,165,0.09);
    }
    .message-meta { flex-grow: 1; }
    .message-author { font-weight: 600; color: var(--primary); font-size: 1.08rem;}
    .message-time { font-size: 0.93rem; color: var(--muted);}
    .message-content { line-height: 1.7; color: var(--text); margin-top: 0.2rem;}
    .empty-message {
        text-align: center; padding: 2.5rem 1.5rem;
        background: var(--glass); border-radius: var(--radius);
        border: 1px dashed var(--border); color: var(--muted);
        display: flex; flex-direction: column; align-items: center; gap: 1rem;
    }
    .empty-icon { font-size: 2.5rem; color: var(--muted);}
    .empty-title { color: var(--primary); font-size: 1.2rem;}
    .empty-text { color: var(--muted);}
    .stats-section { margin: 2.5rem auto 2rem auto; max-width: 700px;}
    .stats-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1.2rem;}
    .stat-item {
        background: var(--card);
        border-radius: var(--radius);
        padding: 1.2rem;
        box-shadow: var(--shadow);
        border: 1px solid var(--border);
        display: flex;
        align-items: center;
        gap: 1rem;
        transition: var(--transition);
    }
    .stat-item:hover {
        box-shadow: 0 8px 24px rgba(74,111,165,0.13);
        transform: translateY(-2px);
    }
    .stat-icon {
        font-size: 1.7rem;
        color: var(--primary);
        background: var(--primary-light);
        border-radius: 50%;
        width: 38px;
        height: 38px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .stat-number {
        font-size: 1.2rem;
        font-weight: 700;
        color: var(--primary);
    }
    .stat-label {
        color: var(--muted);
        font-size: 0.95rem;
    }
    .site-footer {
        background: var(--card);
        padding: 2rem 0 1rem 0;
        border-top: 1px solid var(--border);
        margin-top: 2rem;
    }
    .footer-content {
        max-width: 900px;
        margin: 0 auto;
        text-align: center;
    }
    .footer-link, .social-link {
        color: var(--primary);
        font-weight: 500;
        margin: 0 0.3rem;
        transition: var(--transition);
        text-decoration: none;
    }
    .footer-link:hover, .social-link:hover {
        color: var(--accent);
        text-decoration: underline;
    }
    .heart {
        color: #e63946;
        animation: heartbeat 1.5s infinite;
        display: inline-block;
        margin: 0 2px;
    }
    .social-links {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin: 1rem 0;
    }
    .copyright {
        color: var(--muted);
        font-size: 0.95rem;
        margin-top: 0.5rem;
    }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    @keyframes heartbeat { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.18); } }
    @media (max-width: 600px) {
        .header-content, .footer-content, .guestbook-form, .messages-section, .stats-section {
            max-width: 100vw;
            padding: 0.7rem;
        }
        .site-header, .site-footer {
            padding-left: 0.2rem;
            padding-right: 0.2rem;
        }
        .form-fields {
            gap: 0.7rem;
        }
        .message-card, .stat-item {
            padding: 0.8rem 0.7rem;
        }
    }
    """)

    # ... rest of your return statement and routes remain unchanged ...
