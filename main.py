# Import necessary modules
import os
from datetime import datetime
import pytz  # Library to work with time zones
from supabase import create_client  # Supabase client for database interaction
from dotenv import load_dotenv  # For loading environment variables from a .env file
from fasthtml.common import *  # Importing HTML utility functions

# Load environment variables from .env file
load_dotenv()

# Define character limits for name and message inputs
MAX_NAME_CHAR = 15
MAX_MESSAGE_CHAR = 50

# Define timestamp format for displaying in CET timezone
TIMESTAMP_FMT = "%Y-%m-%d %I:%M:%S %p CET"

# Initialize Supabase client using environment variables
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# Initialize Fast app and set up header with favicon
app, rt = fast_app(
    hdrs=(Link(rel='icon', type='image/png', href="assets/about.png"),),
)

# Reinitialize Fast app (possibly redundant, remove if not needed)
app, rt = fast_app()

# Function to get the current CET time
def get_cet_time():
    cet_tz = pytz.timezone("CET")  # Set timezone to CET
    return datetime.now(cet_tz)  # Return the current time in CET

# Function to add a message to the Supabase guestbook table
def add_message(name, message):
    timestamp = get_cet_time().strftime(TIMESTAMP_FMT)  # Get current time in the defined format
    # Insert the name, message, and timestamp into the 'myGuestbook' table
    supabase.table("myGuestbook").insert(
        {"name": name, "message": message, "timestamp": timestamp}
    ).execute()

# Function to retrieve all messages from the database
def get_messages():
    # Retrieve all records from 'myGuestbook', sorted by 'id' in descending order (latest first)
    response = (
        supabase.table("myGuestbook").select("*").order("id", desc=True).execute()
    )
    return response.data  # Return the retrieved data

# Function to render a single message entry as an HTML article
def render_message(entry):
    return (
        Article(
            Header(f"Name: {entry['name']}"),  # Display the name as a header
            P(entry['message']),  # Display the message in a paragraph
            Footer(Small(Em(f"Posted: {entry['timestamp']}")))  # Display the timestamp in the footer
        )
    )

# Function to render the list of all messages
def render_message_list():
    messages = get_messages()  # Get all messages from the database
    return Div(
        *[render_message(entry) for entry in messages],  # Render each message in the list
        id="message-list",  # Set the HTML element ID for later targeting
    )

# Function to render the main content, including the form and message list
def render_content():
    # Create a form for submitting a new message
    form = Form(
        Fieldset(
            Input(
                type="text",
                name="name",
                placeholder="Name",  # Placeholder for the name field
                required=True,  # Make the field required
                maxlength=MAX_NAME_CHAR,  # Set maximum character limit for the name
            ),
            Input(
                type="text",
                name="message",
                placeholder="Message",  # Placeholder for the message field
                required=True,  # Make the field required
                maxlength=MAX_MESSAGE_CHAR,  # Set maximum character limit for the message
            ),
            Button("Submit", type="submit"),  # Submit button for the form
            role="group",  # Group the inputs together for accessibility
        ),
        method="post",  # Form submission method
        hx_post="/submit-message",  # URL to send the form data to
        hx_target="#message-list",  # HTML target to update after submission
        hx_swap="outerHTML",  # Swap content after form submission
        hx_on__after_request="this.reset()",  # Reset form fields after submission
    )

    # Return the entire content including the form and message list
    return Div(
        P(Em("Write something nice!")),  # Instructional text
        form,  # Form for message submission
        Div(
            "Made With 💖 by ",  # Footer section with author credit
            A("Sujal", href="https://github.com/sujalkalra", target='_blank'),  # Link to author's GitHub
        ),
        Hr(),  # Horizontal line
        render_message_list(),  # List of messages
    )

# Route handler for the homepage
@rt('/')
def get():
    # Render the page with a title and the main content
    return Titled("Suji's Guestbook 📖", render_content())

# Route handler for message submission
@rt("/submit-message", methods=["post"])
def post(name: str, message: str):
    add_message(name, message)  # Add the message to the database
    return render_message_list()  # Return the updated message list

# Start the application server
serve()
