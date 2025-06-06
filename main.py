import os
from datetime import datetime
import pytz
import html # Added import
from supabase import create_client
from dotenv import load_dotenv
from fasthtml.common import *

# --- Setup ---
load_dotenv()
MAX_NAME_CHAR = 30
MAX_MESSAGE_CHAR = 500
MESSAGES_PER_PAGE = 10 # Added for pagination
TIMESTAMP_FMT = "%Y-%m-%d %I:%M:%S %p %Z"
IST_TZ = pytz.timezone("Asia/Kolkata")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Utility ---
def get_ist_time():
    return datetime.now(IST_TZ)

def add_message(name, message):
    # Validate input
    if not name or not name.strip():
        print("Error: Name cannot be empty or just whitespace.")
        return False
    if not message or not message.strip():
        print("Error: Message cannot be empty or just whitespace.")
        return False
    if len(name.strip()) > MAX_NAME_CHAR:
        print(f"Error: Name exceeds maximum length of {MAX_NAME_CHAR}.")
        return False
    if len(message.strip()) > MAX_MESSAGE_CHAR:
        print(f"Error: Message exceeds maximum length of {MAX_MESSAGE_CHAR}.")
        return False

    # Sanitize input
    sanitized_name = html.escape(name.strip())
    sanitized_message = html.escape(message.strip())

    timestamp = get_ist_time().strftime(TIMESTAMP_FMT)
    try:
        supabase.table("myGuestbook").insert(
            {"name": sanitized_name, "message": sanitized_message, "timestamp": timestamp}
        ).execute()
        return True
    except Exception as e:
        print(f"Error adding message to Supabase: {e}")
        return False

def get_messages(page: int = 1, per_page: int = MESSAGES_PER_PAGE):
    try:
        offset = (page - 1) * per_page
        response = (
            supabase.table("myGuestbook")
            .select("*", count="exact") # Request total count
            .order("id", desc=True)
            .range(offset, offset + per_page - 1) # Use range for pagination
            .execute()
        )
        # The count is available in response.count if `count="exact"` is used.
        # For has_more, we check if fetched items + offset < total count,
        # or simpler: if fetched items == per_page (common proxy for has_more).
        total_fetched = len(response.data)
        # has_more = (offset + total_fetched) < response.count if response.count is not None else False
        # Simpler has_more for now:
        has_more = total_fetched == per_page

        return {'data': response.data, 'current_page': page, 'per_page': per_page, 'total_fetched': total_fetched, 'has_more': has_more}
    except Exception as e:
        print(f"Error getting messages: {e}")
        return {'data': [], 'current_page': page, 'per_page': per_page, 'total_fetched': 0, 'has_more': False}

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
                Span("·", _class="meta-separator"),  # <-- Add this separator
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
    # This function is being replaced by render_message_list_content
    # and the new /messages route.
    # messages = get_messages() # Old call
    # if not messages: # Old check
    #     return Div(
    #         Div(
    #             I(_class="far fa-comment-dots empty-icon"),
    #             H3("No messages yet", _class="empty-title"),
    #             P("Be the first to leave a message in the guestbook!", _class="empty-text"),
    #             _class="empty-message"
    #         ),
    #         id="message-list" # This ID will now be on the wrapper in index()
    #     )
def render_message_list_content(page: int):
    messages_info = get_messages(page=page, per_page=MESSAGES_PER_PAGE)
    
    if page == 1 and messages_info['total_fetched'] == 0:
        return [Div( # Return as a list with one item
            Div(
                I(_class="far fa-comment-dots empty-icon"),
                H3("No messages yet", _class="empty-title"),
                P("Be the first to leave a message in the guestbook!", _class="empty-text"),
                _class="empty-message"
            ),
            # id="message-list-items" # ID will be on the wrapper
        )]

    rendered_messages = [render_message(entry) for entry in messages_info['data']]

    if messages_info['has_more']:
        rendered_messages.append(
            Button("Load More Messages", 
                   _class="load-more-button", 
                   hx_get=f"/messages?page={page + 1}", 
                   hx_target="this", # The button itself
                   hx_swap="outerHTML", # Replace button with new content (new msgs + next button)
                   # Consider adding hx_indicator here if a global one isn't used
                  )
        )
    return rendered_messages

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
            Input(type="checkbox", id="theme-toggle", _class="theme-switch", aria_label="Toggle website theme between light and dark modes"),
            Span(
                I(_class="fas fa-moon icon moon"),
                I(_class="fas fa-sun icon sun"),
                _class="slider"
            ),
            _class="theme-switch"
        ),
        toggle_script,
        _class="theme-toggle-container"
    )

# --- Main Content ---
app, rt = fast_app(
    hdrs=(
        Link(rel='icon', type='image/x-icon', href="/assets/me.ico"),
        Link(rel='stylesheet', href='/assets/style.css'),
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
            # Consider adding <Label for="name-input">Your Name</Label> explicitly for better a11y
            Input(
                type="text", name="name", placeholder="Your Name", required=True,
                maxlength=MAX_NAME_CHAR, _class="form-input", id="name-input", aria_label="Your Name"
            ),
            # Consider adding <Label for="message-input">Your Message</Label> explicitly
            Textarea(
                placeholder="Leave a message...", name="message", required=True,
                rows=3, maxlength=MAX_MESSAGE_CHAR, _class="form-textarea", id="message-input", aria_label="Your Message"
            ),
            Div(
                Span(f"{MAX_MESSAGE_CHAR} characters remaining", id="char-counter", _class="char-counter"),
                _class="textarea-footer"
            ),
            Button(
                I(_class="fas fa-paper-plane"), " Send",
                type="submit", _class="submit-button", aria_label="Send your message"
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
              hx_get="/messages?page=1", hx_target="#message-list-items", hx_swap="innerHTML", # Or outerHTML if #message-list-items is the direct list
              role="button", aria_label="Refresh messages", tabindex="0"),
            _class="section-header"
        ),
        Div(*render_message_list_content(page=1), id="message-list-items"), # Unpack content here
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

    # Return the full page content
    return [
        header,
        form,
        messages_section,
        stats_section,
        footer
    ]

@app.post("/submit-message")
async def submit_message(name: str, message: str):
    add_message(name, message) # Return value is ignored as per current plan
    # The old render_message_list() is gone.
    # This should probably return the new structure as well, if used by any hx-post.
    # For now, let's assume the form's hx_target="#message-list-items" and hx_swap will handle it
    # by this endpoint returning the same kind of partial as /messages.
    # This might need adjustment if the form post expects a different structure.
    # However, the original form was hx_target="#message-list", hx_swap="outerHTML".
    # The new ID for items is "#message-list-items".
    # The form's hx_target should be "#message-list-items" and hx_swap="innerHTML" (or outerHTML).
    # Let's update the form target and swap in the index() function later if needed.
    # For now, this function will return the first page of messages.
    return render_message_list_content(page=1)


# This replaces the old @app.get("/refresh-messages")
@app.get("/messages")
async def get_messages_paginated(page: int = 1): # FastAPI/Starlette handles query param conversion
    return render_message_list_content(page=page)

css_style = Style("""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Nunito:wght@400;700&display=swap');
:root {
    --primary: #5f6fff;
    --primary-light: #a1b6ff;
    --primary-dark: #2a2e6e;
    --accent: #ff7eb3;
    --bg: #f5f7fa;
    --card: #fff;
    --glass: rgba(255,255,255,0.72);
    --glass-dark: rgba(35,41,58,0.72);
    --text: #23293a;
    --muted: #7a7f9a;
    --border: #e0e0e0;
    --shadow: 0 8px 32px rgba(95,111,255,0.13);
    --radius: 20px;
    --transition: all 0.22s cubic-bezier(.4,0,.2,1);
}
[data-theme="dark"] {
    --primary: #a1b6ff;
    --primary-light: #5f6fff;
    --primary-dark: #23293a;
    --accent: #ffb86b;
    --bg: #181c24;
    --card: #23293a;
    --glass: rgba(35,41,58,0.82);
    --glass-dark: rgba(35,41,58,0.92);
    --text: #f6f6fa;
    --muted: #b0b4c1;
    --border: #333;
    --shadow: 0 8px 32px rgba(95,111,255,0.18);
}
body {
    background: linear-gradient(135deg, var(--bg) 60%, var(--primary-light) 100%);
    color: var(--text);
    font-family: 'Inter', 'Nunito', 'Poppins', sans-serif;
    min-height: 100vh;
    margin: 0;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    letter-spacing: 0.01em;
}
.glass-card {
    background: var(--glass);
    box-shadow: var(--shadow);
    border-radius: var(--radius);
    border: 1px solid var(--border);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
}
.site-header {
    margin-bottom: 2rem;
    position: sticky;
    top: 0;
    z-index: 100;
    border-bottom: 1px solid var(--border);
    padding: 1.7rem 0 1.2rem 0;
    background: var(--glass);
    box-shadow: 0 2px 16px rgba(95,111,255,0.07);
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
    gap: 1rem;
}
.header-icon {
    font-size: 2.1rem;
    color: var(--primary);
    filter: drop-shadow(0 2px 8px var(--primary-light));
}
.site-title {
    color: var(--primary);
    font-size: 2.3rem;
    font-weight: 800;
    letter-spacing: -1.5px;
    font-family: 'Nunito', 'Inter', sans-serif;
    text-shadow: 0 2px 8px rgba(95,111,255,0.09);
}
.theme-toggle-container { display: flex; align-items: center; }
.theme-toggle {
    position: relative;
    width: 52px;
    height: 28px;
    display: inline-block;
}
.theme-toggle-input {
    opacity: 0;
    width: 0;
    height: 0;
}
.theme-toggle-slider {
    background: var(--muted);
    border-radius: 34px;
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    cursor: pointer;
    transition: background 0.3s;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 8px;
}
.toggle-icon {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    font-size: 1.15rem;
    color: #fff;
    opacity: 0.7;
    transition: opacity 0.3s;
    z-index: 2;
    pointer-events: none;
}
.toggle-moon {
    left: 10px;
    opacity: 1;
    transition: opacity 0.3s;
}
.toggle-sun {
    right: 10px;
    opacity: 0.5;
    transition: opacity 0.3s;
}
.theme-toggle-input:checked + .theme-toggle-slider .toggle-moon {
    opacity: 0.5;
}
.theme-toggle-input:checked + .theme-toggle-slider .toggle-sun {
    opacity: 1;
}
.toggle-knob {
    position: absolute;
    top: 4px;
    left: 4px;
    width: 20px;
    height: 20px;
    background: linear-gradient(135deg, var(--primary-light), var(--primary));
    border-radius: 50%;
    transition: transform 0.3s cubic-bezier(.4,0,.2,1), background 0.3s;
    box-shadow: 0 2px 8px rgba(95,111,255,0.13);
    z-index: 3;
}
.theme-toggle-input:checked + .theme-toggle-slider .toggle-knob {
    transform: translateX(24px);
    background: linear-gradient(135deg, var(--primary-dark), var(--accent));
}
.meta-separator {
    margin: 0 0.5em;
    color: var(--muted);
    font-weight: 400;
    font-size: 1.1em;
    user-select: none;
}
.guestbook-form {
    margin: 0 auto 2.5rem auto;
    max-width: 500px;
    padding: 2.2rem 2.5rem 1.7rem 2.5rem;
    transition: var(--transition);
    font-family: 'Nunito', 'Inter', sans-serif;
    font-size: 1.08rem;
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
    box-shadow: 0 2px 8px rgba(95,111,255,0.04);
}
.form-input:focus, .form-textarea:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 2px var(--primary-light);
}
.textarea-footer {
    display: flex; justify-content: flex-end; font-size: 0.97rem;
    color: var(--muted);
}
.char-limit-exceeded { color: #ff4d6d; }
.submit-button {
    background: linear-gradient(90deg, var(--primary), var(--accent));
    color: #fff;
    border: none;
    border-radius: var(--radius);
    padding: 0.9rem 1.7rem;
    font-weight: 700;
    font-size: 1.15rem;
    cursor: pointer;
    box-shadow: var(--shadow);
    transition: var(--transition);
    margin-top: 0.5rem;
    display: flex; align-items: center; gap: 0.7rem;
    letter-spacing: 0.5px;
    position: relative;
    overflow: hidden;
    font-family: 'Nunito', 'Inter', sans-serif;
}
.submit-button:hover:not(:disabled) {
    background: linear-gradient(90deg, var(--primary-dark), var(--primary));
    transform: translateY(-2px) scale(1.04);
    box-shadow: 0 8px 24px rgba(95,111,255,0.13);
}
.submit-button:disabled { opacity: 0.6; cursor: not-allowed; }
.messages-section { margin: 2.5rem auto 2rem auto; max-width: 700px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.2rem; }
.section-title { font-size: 1.35rem; color: var(--primary); font-weight: 700; font-family: 'Nunito', 'Inter', sans-serif;}
.refresh-icon { color: var(--primary); cursor: pointer; font-size: 1.1rem; transition: var(--transition);}
.refresh-icon:hover { color: var(--accent); transform: rotate(180deg);}
.message-list-container { display: flex; flex-direction: column; gap: 1.2rem; }

.message-header-flex { 
    display: flex; 
    align-items: center; 
    gap: 1rem; 
    margin-bottom: 0.3rem;
}

.avatar-circle {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: linear-gradient(135deg, #a1b6ff 0%, #5f6fff 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 1.3rem;
    color: #fff;
    box-shadow: 0 2px 12px rgba(95,111,255,0.12);
    margin-right: 0.7rem;
    transition: box-shadow 0.2s;
}
.avatar-circle:hover {
    box-shadow: 0 4px 24px rgba(95,111,255,0.18);
}
.avatar-initials {
    font-family: 'Nunito', 'Inter', sans-serif;
    font-size: 1.2em;
    font-weight: 900;
    letter-spacing: 0.02em;
}

.message-card {
    background: var(--glass);
    border-radius: 22px;
    box-shadow: 0 4px 24px rgba(95,111,255,0.10);
    padding: 1.4rem 1.7rem;
    border: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    transition: box-shadow 0.2s, border 0.2s;
    margin-bottom: 0.7rem;
}
.message-card:hover {
    box-shadow: 0 8px 32px rgba(95,111,255,0.16);
    border: 1.5px solid var(--primary-light);
}

.message-meta {
    flex-grow: 1;
    display: flex;
    align-items: center;
    gap: 0.5em;
}

.message-author {
    font-weight: 800;
    color: var(--primary);
    font-size: 1.13rem;
    font-family: 'Nunito', 'Inter', sans-serif;
    margin-right: 0.2em;
}

.meta-separator {
    margin: 0 0.5em;
    color: var(--muted);
    font-weight: 700;
    font-size: 1.2em;
    user-select: none;
}

.message-time {
    font-size: 0.98rem;
    color: var(--muted);
    font-weight: 500;
    font-family: 'Inter', 'Nunito', sans-serif;
}

.message-content {
    line-height: 1.8;
    color: var(--text);
    margin-top: 0.4rem;
    font-size: 1.08rem;
    font-family: 'Inter', 'Nunito', sans-serif;
}
.site-footer {
    margin-top: 2rem;
    padding: 2rem 0 1.5rem 0;
    background: var(--glass);
    border-top: 1px solid var(--border);
    box-shadow: 0 -2px 16px rgba(99,102,241,0.07);
    width: 100%;
}

.footer-content {
    max-width: 900px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.2rem;
    padding: 0 2rem;
}

.heart {
    color: var(--accent);
    font-size: 1.2em;
    vertical-align: middle;
}

.footer-link {
    color: var(--primary);
    text-decoration: none;
    font-weight: 700;
    margin-left: 0.2em;
}

.footer-link:hover {
    color: var(--accent);
    text-decoration: underline;
}

.social-links {
    display: flex;
    gap: 1.5rem;
    margin-top: 0.5rem;
}

.social-link {
    color: var(--primary);
    text-decoration: none;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.4em;
    transition: color 0.2s;
}

.social-link:hover {
    color: var(--accent);
}

.copyright {
    font-size: 1rem;
    color: var(--muted);
    margin-top: 0.5rem;
}

/* Modern theme toggle switch */
.theme-toggle-container {
    display: flex;
    align-items: center;
}

.theme-switch {
    position: relative;
    display: inline-block;
    width: 54px;
    height: 28px;
}

.theme-switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.slider {
    position: absolute;
    cursor: pointer;
    top: 0; left: 0; right: 0; bottom: 0;
    background: var(--muted);
    border-radius: 34px;
    transition: background 0.3s;
    box-shadow: 0 2px 8px rgba(99,102,241,0.10);
}

.slider:before {
    position: absolute;
    content: "";
    height: 22px;
    width: 22px;
    left: 4px;
    bottom: 3px;
    background: linear-gradient(135deg, var(--primary-light), var(--primary));
    border-radius: 50%;
    transition: transform 0.3s cubic-bezier(.4,0,.2,1), background 0.3s;
    box-shadow: 0 2px 8px rgba(99,102,241,0.13);
}

.theme-switch input:checked + .slider {
    background: var(--primary-dark);
}

.theme-switch input:checked + .slider:before {
    transform: translateX(26px);
    background: linear-gradient(135deg, var(--primary-dark), var(--accent));
}

.slider .icon {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    font-size: 1.15rem;
    color: #fff;
    opacity: 0.8;
    z-index: 2;
    pointer-events: none;
}

.slider .icon.sun {
    right: 10px;
    opacity: 0.7;
}

.slider .icon.moon {
    left: 10px;
    opacity: 1;
}

.theme-switch input:checked + .slider .icon.sun {
    opacity: 1;
}

.theme-switch input:checked + .slider .icon.moon {
    opacity: 0.5;
}

/* Make the form wider */
.guestbook-form {
    margin: 0 auto 2.5rem auto;
    max-width: 700px; /* was 500px */
    padding: 2.2rem 2.5rem 1.7rem 2.5rem;
    transition: var(--transition);
    font-family: 'Nunito', 'Inter', sans-serif;
    font-size: 1.08rem;
    background: var(--glass);
    box-shadow: var(--shadow);
    border-radius: var(--radius);
    border: 1px solid var(--border);
}
