import os
from datetime import datetime
import pytz
from supabase import create_client
from dotenv import load_dotenv
from fasthtml.common import *

# Load environment variables
load_dotenv()

# Constants
MAX_NAME_CHAR = 30
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
        Link(rel='stylesheet', href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap"),
        Link(rel='stylesheet', href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"),
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
            Div(
                Div(
                    Span(
                        I(class_="fas fa-user-circle"),
                        class_="avatar"
                    ),
                    class_="avatar-container"
                ),
                Div(
                    H3(entry['name'], class_="message-author"),
                    Span(entry['timestamp'], class_="message-time"),
                    class_="message-meta"
                ),
                class_="message-header-flex"
            ),
            class_="message-header"
        ),
        Div(
            P(entry['message'], class_="message-content"),
            class_="message-body"
        ),
        class_="message-card"
    )

def render_message_list():
    messages = get_messages()
    message_elements = [render_message(entry) for entry in messages]
    
    if not message_elements:
        message_elements = [
            Div(
                I(class_="far fa-comment-dots empty-icon"),
                H3("No messages yet", class_="empty-title"),
                P("Be the first to leave a message in the guestbook!", class_="empty-text"),
                class_="empty-message"
            )
        ]
    
    return Div(*message_elements, id="message-list", class_="message-list-container")

def render_theme_toggle():
    toggle_script = Script("""
    document.addEventListener('DOMContentLoaded', function() {
        // Check for saved theme preference or use preferred color scheme
        const currentTheme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
        
        // Apply the theme
        document.documentElement.setAttribute('data-theme', currentTheme);
        document.getElementById('theme-toggle').checked = currentTheme === 'dark';
        
        // Update theme icon
        updateThemeIcon(currentTheme === 'dark');
        
        // Handle toggle changes
        document.getElementById('theme-toggle').addEventListener('change', function(e) {
            const theme = e.target.checked ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
            updateThemeIcon(theme === 'dark');
        });
        
        function updateThemeIcon(isDark) {
            const iconElement = document.querySelector('.theme-icon');
            if (isDark) {
                iconElement.classList.remove('fa-sun');
                iconElement.classList.add('fa-moon');
            } else {
                iconElement.classList.remove('fa-moon');
                iconElement.classList.add('fa-sun');
            }
        }
    });
    """)
    
    return Div(
        Label(
            Input(type="checkbox", id="theme-toggle", class_="theme-toggle-input"),
            Span(I(class_="fas fa-sun theme-icon"), class_="theme-toggle-slider"),
            class_="theme-toggle"
        ),
        toggle_script,
        class_="theme-toggle-container"
    )

def render_loading_indicator():
    return Div(
        Div(class_="loading-spinner"),
        class_="loading-container"
    )

def render_content():
    # Header section
    header = Header(
        Div(
            Div(
                I(class_="fas fa-book-open header-icon"),
                H1("Sujal's Guestbook", class_="site-title"),
                class_="title-container"
            ),
            render_theme_toggle(),
            class_="header-content"
        ),
        class_="site-header"
    )
    
    # Form section with character counter
    char_counter_script = Script("""
    document.addEventListener('DOMContentLoaded', function() {
        const messageTextarea = document.getElementById('message-textarea');
        const charCounter = document.getElementById('char-counter');
        const submitButton = document.querySelector('.submit-button');
        
        messageTextarea.addEventListener('input', function() {
            const remaining = 500 - this.value.length;
            charCounter.textContent = remaining + ' characters remaining';
            
            if (remaining < 0) {
                charCounter.classList.add('char-limit-exceeded');
                submitButton.disabled = true;
            } else {
                charCounter.classList.remove('char-limit-exceeded');
                submitButton.disabled = false;
            }
        });
        
        // Form submission animation
        const form = document.querySelector('.guestbook-form');
        const loadingOverlay = document.getElementById('loading-overlay');
        
        form.addEventListener('submit', function() {
            loadingOverlay.classList.add('visible');
            setTimeout(() => {
                loadingOverlay.classList.remove('visible');
            }, 1000);
        });
    });
    """)
    
    form = Form(
        Div(
            H2("Leave a Message", class_="form-title"),
            Div(
                Div(
                    Label("Your Name", for_="name-input", class_="form-label"),
                    Div(
                        I(class_="fas fa-user input-icon"),
                        Input(
                            type="text",
                            id="name-input",
                            name="name",
                            placeholder="Enter your name",
                            required=True,
                            maxlength=MAX_NAME_CHAR,
                            class_="form-input"
                        ),
                        class_="input-container"
                    ),
                    class_="form-group"
                ),
                Div(
                    Label("Your Message", for_="message-textarea", class_="form-label"),
                    Div(
                        I(class_="fas fa-comment input-icon"),
                        Textarea(
                            id="message-textarea",
                            placeholder="Share your thoughts...",
                            name="message",
                            required=True,
                            rows="4",
                            maxlength="500",
                            class_="form-textarea"
                        ),
                        class_="textarea-container"
                    ),
                    Div(
                        Span("500 characters remaining", id="char-counter", class_="char-counter"),
                        class_="textarea-footer"
                    ),
                    class_="form-group"
                ),
                class_="form-fields"
            ),
            Div(
                Button(
                    I(class_="fas fa-paper-plane"),
                    " Submit Message",
                    type="submit",
                    class_="submit-button"
                ),
                class_="form-actions"
            ),
            class_="form-container"
        ),
        char_counter_script,
        method="post",
        hx_post="/submit-message",
        hx_target="#message-list",
        hx_swap="outerHTML",
        hx_indicator="#loading-overlay",
        hx_on__after_request="this.reset(); document.getElementById('char-counter').textContent = '500 characters remaining';",
        class_="guestbook-form"
    )
    
    # Loading overlay
    loading_overlay = Div(
        Div(
            Div(class_="spinner"),
            P("Sending your message...", class_="loading-text"),
            class_="loading-content"
        ),
        id="loading-overlay",
        class_="loading-overlay"
    )
    
    # Messages section
    messages_section = Section(
        Div(
            H2("Recent Messages", class_="section-title"),
            I(class_="fas fa-sync-alt refresh-icon", title="Refresh messages", 
              hx_get="/refresh-messages", hx_target="#message-list", hx_swap="outerHTML"),
            class_="section-header"
        ),
        render_message_list(),
        class_="messages-section"
    )
    
    # Stats section
    stats_section = Section(
        Div(
            Div(
                I(class_="fas fa-users stat-icon"),
                Div(
                    H3("25+", class_="stat-number"),
                    P("Visitors", class_="stat-label"),
                    class_="stat-text"
                ),
                class_="stat-item"
            ),
            Div(
                I(class_="fas fa-comments stat-icon"),
                Div(
                    H3("100+", class_="stat-number"),
                    P("Messages", class_="stat-label"),
                    class_="stat-text"
                ),
                class_="stat-item"
            ),
            Div(
                I(class_="fas fa-heart stat-icon"),
                Div(
                    H3("Thank You", class_="stat-number"),
                    P("For Visiting", class_="stat-label"),
                    class_="stat-text"
                ),
                class_="stat-item"
            ),
            class_="stats-container"
        ),
        class_="stats-section"
    )
    
    # Footer
    footer = Footer(
        Div(
            Div(
                P("Made with ", Span("❤️", class_="heart"), " by ", 
                  A("Sujal", href="https://github.com/sujalkalra", target="_blank", class_="footer-link")),
                class_="footer-text"
            ),
            Div(
                A(I(class_="fab fa-github"), " GitHub", 
                  href="https://github.com/sujalkalra", target="_blank", class_="social-link"),
                A(I(class_="fas fa-code-branch"), " New Version", 
                  href="https://sujiguestbook2.vercel.app", target="_blank", class_="social-link"),
                class_="social-links"
            ),
            Div(
                P("© 2025 Sujal's Guestbook. All rights reserved.", class_="copyright-text"),
                class_="copyright"
            ),
            class_="footer-content"
        ),
        class_="site-footer"
    )
    
    css_style = Style("""
    :root {
        --primary-color: #4361ee;
        --primary-light: #4895ef;
        --primary-dark: #3a0ca3;
        --secondary-color: #4cc9f0;
        --accent-color: #7209b7;
        --success-color: #2ec4b6;
        --warning-color: #ff9f1c;
        --error-color: #e63946;
        
        --bg-color: #f8f9fa;
        --card-bg: #ffffff;
        --input-bg: #ffffff;
        --header-bg: #ffffff;
        --footer-bg: #f1f3f5;
        
        --text-color: #212529;
        --text-muted: #6c757d;
        --text-light: #f8f9fa;
        --border-color: #dee2e6;
        
        --shadow-sm: 0 2px 5px rgba(0, 0, 0, 0.05);
        --shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);
        
        --radius-sm: 4px;
        --radius: 8px;
        --radius-lg: 16px;
        
        --transition: all 0.3s ease;
        --transition-slow: all 0.5s ease;
        
        --font-sans: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    [data-theme="dark"] {
        --primary-color: #4cc9f0;
        --primary-light: #90e0ef;
        --primary-dark: #3a86ff;
        --secondary-color: #7209b7;
        --accent-color: #f72585;
        
        --bg-color: #121212;
        --card-bg: #1e1e1e;
        --input-bg: #2d2d2d;
        --header-bg: #1a1a1a;
        --footer-bg: #1a1a1a;
        
        --text-color: #e0e0e0;
        --text-muted: #adb5bd;
        --border-color: #333;
        
        --shadow-sm: 0 2px 5px rgba(0, 0, 0, 0.15);
        --shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.35);
    }
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: var(--font-sans);
        background-color: var(--bg-color);
        color: var(--text-color);
        line-height: 1.6;
        transition: var(--transition);
        display: flex;
        flex-direction: column;
        min-height: 100vh;
    }
    
    /* Container */
    .container {
        width: 100%;
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-weight: 600;
        line-height: 1.3;
        margin-bottom: 0.5rem;
    }
    
    a {
        color: var(--primary-color);
        text-decoration: none;
        transition: var(--transition);
    }
    
    a:hover {
        color: var(--primary-light);
    }
    
    /* Header Styles */
    .site-header {
        background-color: var(--header-bg);
        box-shadow: var(--shadow);
        padding: 1rem 0;
        margin-bottom: 2rem;
        position: sticky;
        top: 0;
        z-index: 100;
        border-bottom: 1px solid var(--border-color);
    }
    
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 1.5rem;
    }
    
    .title-container {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .header-icon {
        font-size: 1.5rem;
        color: var(--primary-color);
    }
    
    .site-title {
        color: var(--primary-color);
        font-size: 1.75rem;
        font-weight: 700;
        letter-spacing: -0.5px;
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
        background-color: var(--text-muted);
        transition: var(--transition);
        border-radius: 34px;
        display: flex;
        align-items: center;
        justify-content: center;
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
        z-index: 1;
    }
    
    .theme-toggle-input:checked + .theme-toggle-slider {
        background-color: var(--primary-color);
    }
    
    .theme-toggle-input:checked + .theme-toggle-slider:before {
        transform: translateX(30px);
    }
    
    .theme-icon {
        color: var(--text-light);
        font-size: 14px;
        position: absolute;
        z-index: 0;
    }
    
    /* Main Content */
    main {
        flex-grow: 1;
        padding: 0 1.5rem;
        max-width: 1000px;
        margin: 0 auto;
        width: 100%;
    }
    
    /* Form Styles */
    .guestbook-form {
        background-color: var(--card-bg);
        border-radius: var(--radius);
        padding: 2rem;
        margin-bottom: 3rem;
        box-shadow: var(--shadow);
        transition: var(--transition);
        border: 1px solid var(--border-color);
    }
    
    .guestbook-form:hover {
        box-shadow: var(--shadow-lg);
    }
    
    .form-title {
        color: var(--primary-color);
        margin-bottom: 1.5rem;
        position: relative;
        display: inline-block;
    }
    
    .form-title:after {
        content: '';
        position: absolute;
        bottom: -8px;
        left: 0;
        width: 80px;
        height: 3px;
        background-color: var(--primary-color);
        border-radius: 3px;
    }
    
    .form-container {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }
    
    .form-fields {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }
    
    .form-group {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .form-label {
        font-weight: 500;
        color: var(--text-color);
    }
    
    .input-container {
        position: relative;
    }
    
    .input-icon {
        position: absolute;
        left: 15px;
        top: 50%;
        transform: translateY(-50%);
        color: var(--text-muted);
    }
    
    .form-input, .form-textarea {
        width: 100%;
        padding: 0.8rem 1rem 0.8rem 2.5rem;
        border: 1px solid var(--border-color);
        border-radius: var(--radius-sm);
        background-color: var(--input-bg);
        color: var(--text-color);
        font-family: var(--font-sans);
        transition: var(--transition);
        font-size: 1rem;
    }
    
    .form-textarea {
        resize: vertical;
        min-height: 120px;
    }
    
    .form-input:focus, .form-textarea:focus {
        outline: none;
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.15);
    }
    
    .textarea-footer {
        display: flex;
        justify-content: flex-end;
        margin-top: 0.5rem;
    }
    
    .char-counter {
        font-size: 0.8rem;
        color: var(--text-muted);
    }
    
    .char-limit-exceeded {
        color: var(--error-color);
    }
    
    .form-actions {
        display: flex;
        justify-content: flex-end;
    }
    
    .submit-button {
        background-color: var(--primary-color);
        color: white;
        border: none;
        border-radius: var(--radius-sm);
        padding: 0.8rem 1.5rem;
        font-weight: 500;
        font-size: 1rem;
        cursor: pointer;
        transition: var(--transition);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .submit-button:hover:not(:disabled) {
        background-color: var(--primary-dark);
        transform: translateY(-2px);
    }
    
    .submit-button:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }
    
    /* Loading overlay */
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(3px);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
        opacity: 0;
        visibility: hidden;
        transition: var(--transition);
    }
    
    .loading-overlay.visible {
        opacity: 1;
        visibility: visible;
    }
    
    .loading-content {
        background-color: var(--card-bg);
        border-radius: var(--radius);
        padding: 2rem;
        text-align: center;
        box-shadow: var(--shadow-lg);
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
    }
    
    .spinner {
        width: 50px;
        height: 50px;
        border: 5px solid rgba(0, 0, 0, 0.1);
        border-radius: 50%;
        border-top-color: var(--primary-color);
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .loading-text {
        color: var(--text-color);
        font-weight: 500;
    }
    
    /* Messages Section */
    .messages-section {
        margin-bottom: 3rem;
    }
    
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    
    .section-title {
        font-size: 1.5rem;
        color: var(--primary-color);
        position: relative;
        display: inline-block;
    }
    
    .section-title:after {
        content: '';
        position: absolute;
        bottom: -8px;
        left: 0;
        width: 60px;
        height: 3px;
        background-color: var(--primary-color);
        border-radius: 3px;
    }
    
    .refresh-icon {
        color: var(--primary-color);
        cursor: pointer;
        font-size: 1.2rem;
        transition: var(--transition);
    }
    
    .refresh-icon:hover {
        color: var(--primary-dark);
        transform: rotate(180deg);
    }
    
    .message-list-container {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }
    
    .message-card {
        background-color: var(--card-bg);
        border-radius: var(--radius);
        padding: 1.5rem;
        box-shadow: var(--shadow);
        transition: var(--transition);
        border: 1px solid var(--border-color);
        overflow: hidden;
    }
    
    .message-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-3px);
    }
    
    .message-header {
        margin-bottom: 1rem;
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 1rem;
    }
    
    .message-header-flex {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .avatar-container {
        width: 40px;
        height: 40px;
        background-color: var(--primary-light);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    
    .avatar {
        color: white;
        font-size: 1.2rem;
    }
    
    .message-meta {
        flex-grow: 1;
    }
    
    .message-author {
        font-weight: 600;
        color: var(--primary-color);
        margin-bottom: 0.25rem;
        font-size: 1.1rem;
    }
    
    .message-time {
        font-size: 0.85rem;
        color: var(--text-muted);
        display: block;
    }
    
    .message-body {
        padding-top: 0.5rem;
    }
    
    .message-content {
        line-height: 1.6;
        white-space: pre-wrap;
        color: var(--text-color);
    }
    
    .empty-message {
        text-align: center;
        padding: 3rem 2rem;
        background-color: var(--card-bg);
        border-radius: var(--radius);
        border: 1px dashed var(--border-color);
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
    }
    
    .empty-icon {
        font-size: 3rem;
        color: var(--text-muted);
        margin-bottom: 1rem;
    }
    
    .empty-title {
        color: var(--text-color);
        font-size: 1.5rem;
    }
    
    .empty-text {
        color: var(--text-muted);
        max-width: 400px;
    }
    
    /* Stats Section */
    .stats-section {
        margin-bottom: 3rem;
    }
    
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
    }
    
    .stat-item {
        background-color: var(--card-bg);
        border-radius: var(--radius);
        padding: 1.5rem;
        box-shadow: var(--shadow);
        transition: var(--transition);
        border: 1px solid var(--border-color);
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .stat-item:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-3px);
    }
    
    .stat-icon {
        font-size: 2rem;
        color: var(--primary-color);
        background-color: rgba(67, 97, 238, 0.1);
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    
    .stat-text {
        flex-grow: 1;
    }
    
    .stat-number {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 0.25rem;
    }
    
    .stat-label {
        color: var(--text-muted);
        font-size: 0.9rem;
    }
    
    /* Footer Styles */
    .site-footer {
        background-color: var(--footer-bg);
        padding: 2rem 0;
        margin-top: 2rem;
        border-top: 1px solid var(--border-color);
    }
    
    .footer-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 1.5rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1.5rem;
        text-align: center;
    }
    
    .footer-text {
        font-size: 1rem;
    }
    
    .footer-link {
        font-weight: 500;
        color: var(--primary-color);
    }
    
    .heart {
        color: var(--error-color);
        display: inline-block;
        animation: heartbeat 1.5s infinite;
        margin: 0 3px;
    }
    
    .social-links {
        display: flex;
        gap: 1rem;
    }
    
    .social-link {
        color: var(--text-color);
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-sm);
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
        transition: var(--transition);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .social-link:hover {
        background-color: var(--primary-color);
        color: white;
        transform: translateY(-2px);
    }
    
    .copyright {
        color: var(--text-muted);
        font-size: 0.85rem;
    }
    
    @keyframes heartbeat {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.2); }
    }
    
    /* Welcome Section */
    .welcome-text {
        text-align: center;
        margin-bottom: 2rem;
        font-size: 1.1rem;
        color: var(--text-muted);
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Responsive Styles */
    @media (max-width: 768px) {
        .site-title {
            font-size: 1.4rem;
        }
        
        .guestbook-form {
            padding: 1.5rem;
        }
        
        .message-card {
            padding: 1.2rem;
        }
        
        .stats-container {
            grid-template-columns: 1fr;
        }
        
        .social-links {
            flex-direction: column;
            gap: 0.75rem;
        }
    }
    
    @media (max-width: 576px) {
        .header-content {
            flex-direction: column;
            gap: 1rem;
        }
        
        .theme-toggle-container {
            margin-top: 0.75rem;
        }
        
        .form-actions {
            justify-content: center;
        }
        
        .submit-button {
            width: 100%;
        }
        
        .message-header-flex {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.75rem;
        }
        
        .avatar-container {
            margin-bottom: 0.5rem;
        }
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideInUp {
        from {
            transform: translateY(20px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    .guestbook-form, .message-card, .stat-item {
        animation: fadeIn 0.6s ease-out forwards, slideInUp 0.6s ease-out forwards;
    }
    
    .message-card:nth-child(2) { animation-delay: 0.1s; }
    .message-card:nth-child(3) { animation-delay: 0.2s; }
    .message-card:nth-child(4) { animation-delay: 0.3s; }
    .message-card:nth-child(5) { animation-delay: 0.4s; }
    
    .stat-item:nth-child(2) { animation-delay: 0.1s; }
    .stat-item:nth-child(3) { animation-delay: 0.2s; }
    """)

# Routes
@app.get("/")
def index():
    return Div(
        Div(
            P("Welcome to my guestbook! Feel free to leave a message and connect with others. Your thoughts and feedback are greatly appreciated!", class_="welcome-text"),
            class_="container"
        ),
        main := Main(
            Div(
                form,
                messages_section,
                stats_section,
                class_="container"
            ),
            class_="main-content"
        ),
        loading_overlay,
        footer,
        css_style,
        class_="page-wrapper"
    )
    
@app.post("/submit-message")
def submit_message(name: str = Form(...), message: str = Form(...)):
    # Validation
    if len(name) > MAX_NAME_CHAR:
        name = name[:MAX_NAME_CHAR]
    
    if len(message) > MAX_MESSAGE_CHAR:
        message = message[:MAX_MESSAGE_CHAR]
        
    # Add message to database
    add_message(name, message)
        
    # Return updated message list
    return render_message_list()
    
@app.get("/refresh-messages")
def refresh_messages():
    return render_message_list()

serve()
