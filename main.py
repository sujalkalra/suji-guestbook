import reflex as rx
import datetime

# State to handle form input and storing messages
class GuestbookState(rx.State):
    name: str
    message: str
    messages: list[dict] = []

    def post_message(self):
        if self.name and self.message:
            self.messages.append({
                "name": self.name,
                "message": self.message,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            self.name = ""
            self.message = ""

# Define the main app style
style = rx.Style("""
    :root {
        --primary-color: #47a3f3;
        --secondary-color: #6c757d;
        --accent-color: #00c897;
        --bg-light: #ffffff;
        --bg-dark: #1a1a1a;
        --text-light: #f1f1f1;
        --text-dark: #1a1a1a;
        --border-color: #ccc;
        --card-bg-light: #f9f9f9;
        --card-bg-dark: #2c2c2c;
        --footer-bg-light: #f1f1f1;
        --footer-bg-dark: #111;
        --shadow: 0 2px 5px rgba(0,0,0,0.1);
        --hover-shadow: 0 4px 12px rgba(0,0,0,0.2);
        --transition: all 0.3s ease-in-out;
    }

    body.light {
        background-color: var(--bg-light);
        color: var(--text-dark);
    }

    body.dark {
        background-color: var(--bg-dark);
        color: var(--text-light);
    }

    .header {
        padding: 2rem 5%;
        text-align: center;
    }

    .form-section {
        padding: 2rem 5%;
    }

    .form-group {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin-bottom: 1rem;
    }

    .form-input, .form-textarea {
        width: 100%;
        padding: 0.75rem 1rem;
        border: 1px solid var(--border-color);
        border-radius: 6px;
        background-color: var(--bg-light);
        color: var(--text-dark);
        font-size: 1rem;
        transition: var(--transition);
    }

    .form-input:focus, .form-textarea:focus {
        border-color: var(--accent-color);
        outline: none;
        box-shadow: 0 0 0 3px rgba(71, 163, 243, 0.3);
    }

    .submit-button {
        background-color: var(--primary-color);
        color: #fff;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 6px;
        cursor: pointer;
        font-size: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        transition: var(--transition);
    }

    .submit-button:hover {
        background-color: var(--accent-color);
        box-shadow: var(--hover-shadow);
    }

    .messages-section {
        margin-bottom: 2rem;
    }

    .message-card {
        background-color: var(--card-bg-light);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow);
        transition: var(--transition);
    }

    .message-card:hover {
        box-shadow: var(--hover-shadow);
    }

    .message-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
    }

    .message-author {
        font-weight: 600;
        color: var(--primary-color);
    }

    .message-time {
        font-size: 0.875rem;
        color: var(--secondary-color);
    }

    .message-content {
        font-size: 1rem;
        color: var(--text-dark);
        line-height: 1.5;
    }

    .empty-message {
        text-align: center;
        font-style: italic;
        color: var(--secondary-color);
        padding: 1rem;
        background-color: var(--card-bg-light);
        border-radius: 6px;
    }

    .site-footer {
        background-color: var(--footer-bg-light);
        padding: 1rem 5%;
        text-align: center;
        box-shadow: var(--shadow);
    }

    .footer-content {
        max-width: 800px;
        margin: 0 auto;
        font-size: 0.9rem;
    }

    .heart {
        color: red;
        margin: 0 0.2rem;
        font-weight: bold;
    }

    .footer-link {
        color: var(--primary-color);
        text-decoration: none;
        margin: 0 0.3rem;
        transition: var(--transition);
    }

    .footer-link:hover {
        color: var(--accent-color);
        text-decoration: underline;
    }

    @media (max-width: 600px) {
        .message-header {
            flex-direction: column;
            align-items: flex-start;
        }
    }
""")

# Component to display the form
def guestbook_form():
    return rx.box(
        rx.form(
            rx.box(
                rx.input(
                    placeholder="Your Name",
                    value=GuestbookState.name,
                    on_change=GuestbookState.set_name,
                    class_name="form-input"
                ),
                rx.text_area(
                    placeholder="Write your message...",
                    value=GuestbookState.message,
                    on_change=GuestbookState.set_message,
                    class_name="form-textarea"
                ),
                rx.button("Submit", on_click=GuestbookState.post_message, class_name="submit-button"),
                class_name="form-group"
            ),
            class_name="form-section"
        )
    )

# Component to display messages
def message_list():
    return rx.box(
        rx.foreach(
            GuestbookState.messages,
            lambda msg: rx.box(
                rx.box(
                    rx.text(msg["name"], class_name="message-author"),
                    rx.text(msg["timestamp"], class_name="message-time"),
                    class_name="message-header"
                ),
                rx.text(msg["message"], class_name="message-content"),
                class_name="message-card"
            )
        ) if GuestbookState.messages else rx.text("No messages yet.", class_name="empty-message"),
        class_name="messages-section"
    )

# Main app layout
def index():
    return rx.box(
        rx.box(
            rx.heading("Guestbook", size="8", class_name="header"),
            guestbook_form(),
            message_list(),
        ),
        rx.footer(
            rx.text("Made with ", rx.span("❤", class_name="heart"), " by Sujal"),
            class_name="site-footer"
        )
    )

app = rx.App(style=style)
app.add_page(index)
app.compile()
