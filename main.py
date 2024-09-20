import os
from datetime import datetime
import pytz
from supabase import create_client
from dotenv import load_dotenv

from fasthtml.common import *


#Load env var
load_dotenv()


MAX_NAME_CHAR = 15
MAX_MESSAGE_CHAR = 50
TIMESTAMP_FMT = "%Y-%m-%d %I:%M:%S %p CET"


#initialize supabase client:
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

app, rt = fast_app(
    hdrs=(Link(rel='icon', type='image/png', href="/assets/about.png"),),
)

app,rt = fast_app()


def get_cet_time():
    cet_tz = pytz.timezone("CET")
    return datetime.now(cet_tz)

def add_message(name,message):
    timestamp = get_cet_time().strftime(TIMESTAMP_FMT)
    supabase.table("myGuestbook").insert(
        {"name" : name, "message" : message, "timestamp" : timestamp}
    ).execute()


def get_messages():
    #sort By id in descending order to get latest first
    response = (
        supabase.table("myGuestbook").select("*").order("id",desc=True).execute()
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
        id = "message-list",
    )



def render_content():
    form = Form(
        Fieldset(
            Input(
                type = "text",
                name = "name",
                placeholder = "Name",
                required = True,
                maxlenght = MAX_NAME_CHAR,
            ),
            Input(
                type="text",
                name="message",
                placeholder="Message",
                required=True,
                maxlenght=MAX_MESSAGE_CHAR,
            ),
            Button("Submit" , type = "submit"),
            role = "group",
        ),
        method = "post",
        hx_post="/submit-message",
        hx_target="#message-list",
        hx_swap="outerHTML",
        hx_on__after_request = "this.reset()",
    )


    return Div(
        P(Em("Write something nice!")),
        form,

        Div(
            "Made With 💖 by",
            A("Sujal",href="https://github.com/sujalkalra",target='_blank'),
        ),
        Hr(),
        render_message_list(),
    
    )

@rt('/')
def get():
    return Titled("Suji's Guestbook 📖", render_content())

@rt("/submit-message",methods = ["post"])
def post(name: str,message:str):
    add_message(name,message)
    return render_message_list()

serve()