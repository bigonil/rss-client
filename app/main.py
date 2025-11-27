from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates
import xml.etree.ElementTree as ET
import requests
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from python_http_client.exceptions import HTTPError

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

RSS_URL = "https://azurestatuscdn.azureedge.net/en-us/status/feed/"
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
TO_EMAIL = os.getenv("TO_EMAIL", "destination@example.com")
FROM_EMAIL = os.getenv("FROM_EMAIL", "your_verified_sender@example.com")


def parse_custom_rss(xml_content):
    """
    Parse Azure Status RSS XML content and return a list of entries.

    Args:
        xml_content: Raw XML feed content as bytes or string.

    Returns:
        List of dictionaries containing title, link, published, and summary.
    """
    root = ET.fromstring(xml_content)
    items = []
    for item in root.findall(".//channel/item"):
        title = item.findtext("title", default="(No Title)")
        link = item.findtext("link", default="#")
        pub_date = item.findtext("pubDate", default="")
        description = item.findtext("description", default="")
        items.append(
            {
                "title": title,
                "link": link,
                "published": pub_date,
                "summary": description,
            }
        )
    return items


def send_notification_email(entries):
    """
    Send a notification email via SendGrid with the provided feed entries.

    Args:
        entries: List of entry dictionaries to include in the email body.
    """
    if not entries or not SENDGRID_API_KEY or not FROM_EMAIL or not TO_EMAIL:
        return

    subject = "🔔 Azure Status - New Updates Detected"
    body = "\n\n".join(
        [f"• {e['title']}\n{e['link']}\n{e['published']}" for e in entries]
    )

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=TO_EMAIL,
        subject=subject,
        plain_text_content=body,
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        print("✅ Notification email sent.")
    except HTTPError as e:
        print("❌ SendGrid HTTP error:", e)
    except Exception as e:
        print("❌ Error sending email:", e)


@app.get("/", response_class=HTMLResponse)
async def read_feed(request: Request):
    """
    Fetch the Azure status RSS feed, parse entries, optionally send email
    notifications, and render the index template.

    Args:
        request (Request):
            The incoming FastAPI request object used for template rendering.

    Returns:
        TemplateResponse:
            The rendered index.html page with parsed RSS entries.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (RSS Client - FastAPI)"
        }
        response = requests.get(RSS_URL, headers=headers, timeout=10)
        response.raise_for_status()

        entries = parse_custom_rss(response.content)
        print(f"✅ Found {len(entries)} entries")
        for entry in entries[:3]:
            print("➡️", entry["title"])

        if entries:
            send_notification_email(entries)

    except Exception as e:
        print("❌ Error fetching/parsing feed:", e)
        entries = []

    return templates.TemplateResponse("index.html", {"request": request, "entries": entries})