#!/usr/bin/env python3
"""Weekly email digest — sends the subscriber list to the owner.

Usage:
    python scripts/send_weekly_email_digest.py

Required env vars:
    DIGEST_RECIPIENT_EMAIL  — owner email to receive the digest
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS — SMTP credentials

Optional:
    ARC_DB_PATH — path to arc_local_auth.sqlite3 (default: arc_service/data/arc_local_auth.sqlite3)
"""

from __future__ import annotations

import os
import smtplib
import sqlite3
from datetime import UTC, datetime
from email.mime.text import MIMEText
from pathlib import Path

DB_PATH = Path(os.environ.get("ARC_DB_PATH", "arc_service/data/arc_local_auth.sqlite3"))


def load_subscribers() -> list[dict]:
    if not DB_PATH.exists():
        return []
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT email, source, sc_username, display_name, subscribed_at FROM email_subscribers WHERE status = 'active' ORDER BY subscribed_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


GIVEAWAY_THRESHOLD = 1000
HUB_URL = "https://garebear99.github.io/TizWildinEntertainmentHUB/"
SC_URL = "https://soundcloud.com/tizwildin"


def build_admin_digest(subscribers: list[dict]) -> str:
    """Admin report sent to the owner with the full subscriber list."""
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "TizWildin Entertainment HUB — Admin Subscriber Report",
        f"Generated: {now}",
        f"Total active subscribers: {len(subscribers)}",
        "",
        "─" * 60,
    ]
    if not subscribers:
        lines.append("No subscribers yet.")
    else:
        lines.append(f"{'Email':<40} {'Source':<12} {'SC Username':<20} {'Subscribed'}")
        lines.append("─" * 60)
        for s in subscribers:
            lines.append(
                f"{s['email']:<40} {s['source']:<12} {(s.get('sc_username') or ''):<20} {s['subscribed_at'][:10]}"
            )
    lines.append("")
    lines.append("─" * 60)
    return "\n".join(lines)


def build_subscriber_newsletter(total_subscribers: int) -> str:
    """Community newsletter sent to every subscriber every Monday."""
    remaining = max(0, GIVEAWAY_THRESHOLD - total_subscribers)
    progress_pct = min(100, int((total_subscribers / GIVEAWAY_THRESHOLD) * 100))

    lines = [
        "🎛️ TizWildin Entertainment HUB — Weekly Update",
        "",
        f"Hey! Thanks for being part of the TizWildin community.",
        "",
        "─" * 50,
        "",
        "📢 HELP US GROW — SHARE THE HUB",
        "",
        "We're building something real: free professional audio plugins,",
        "sample packs, MIDI tools, games, and a full creator ecosystem.",
        "",
        "Share the HUB with a friend or on social media:",
        f"  🌐 {HUB_URL}",
        f"  🔊 {SC_URL}",
        "",
        "The more people who join, the more we can give back.",
        "",
        "─" * 50,
        "",
        f"🎁 1,000 USER GIVEAWAY MILESTONE",
        "",
        f"  Current community size: {total_subscribers}",
        f"  Target: {GIVEAWAY_THRESHOLD}",
        f"  Progress: {progress_pct}% ({remaining} to go)" if remaining > 0 else f"  🎉 WE HIT {GIVEAWAY_THRESHOLD}! Giveaways are LIVE!",
        "",
        "When we reach 1,000 users, giveaways begin — free plugin",
        "upgrades, exclusive sample packs, and more.",
        "Every follower counts. Share the link!",
        "",
        "─" * 50,
        "",
        "📻 COMING SOON: 24/7 RADIO STREAM",
        "",
        "A 24/7 live radio stream is coming to YouTube, connected",
        "to the TizWildin ecosystem. It will include:",
        "  • Continuous music playback from TizWildin releases",
        "  • Song submission routing for the promotional roster",
        "  • Badge-gated daily submissions for supporters",
        "",
        "Stay tuned for the launch announcement.",
        "",
        "─" * 50,
        "",
        "Free plugins. Free packs. Real DSP. Open source.",
        "Great sound shouldn't cost anything.",
        "",
        "— Gary Doman (GareBear99 / TizWildin)",
        "",
        f"Unsubscribe: reply to this email with 'unsubscribe'",
    ]
    return "\n".join(lines)


def _smtp_config() -> tuple[str, int, str, str]:
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER", "")
    password = os.environ.get("SMTP_PASS", "")
    return host, port, user, password


def send_email(subject: str, body: str, recipient: str) -> None:
    host, port, user, password = _smtp_config()
    if not user or not password:
        return
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = recipient
    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(user, [recipient], msg.as_string())


def send_bulk(subject: str, body: str, recipients: list[str]) -> int:
    """Send the same email to all recipients. Returns count sent."""
    host, port, user, password = _smtp_config()
    if not user or not password:
        print("ERROR: Missing SMTP_USER or SMTP_PASS.")
        return 0
    sent = 0
    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        for addr in recipients:
            try:
                msg = MIMEText(body)
                msg["Subject"] = subject
                msg["From"] = user
                msg["To"] = addr
                server.sendmail(user, [addr], msg.as_string())
                sent += 1
            except Exception as exc:
                print(f"  Failed to send to {addr}: {exc}")
    return sent


def main() -> None:
    subscribers = load_subscribers()
    now_date = datetime.now(UTC).strftime("%Y-%m-%d")
    owner_email = os.environ.get("DIGEST_RECIPIENT_EMAIL", "")

    # 1. Send community newsletter to ALL subscribers
    newsletter = build_subscriber_newsletter(len(subscribers))
    emails = [s["email"] for s in subscribers if s.get("email")]
    print(f"Subscribers: {len(emails)}")
    print(newsletter)
    print()

    if emails and os.environ.get("SMTP_USER"):
        subject = f"🎛️ TizWildin Weekly — {now_date}"
        sent = send_bulk(subject, newsletter, emails)
        print(f"Newsletter sent to {sent}/{len(emails)} subscribers.")
    else:
        print("No subscribers or SMTP not configured — newsletter printed to stdout only.")

    # 2. Send admin digest to owner
    if owner_email and os.environ.get("SMTP_USER"):
        admin_body = build_admin_digest(subscribers)
        admin_subject = f"TizWildin Admin Digest — {now_date} ({len(subscribers)} subscribers)"
        send_email(admin_subject, admin_body, owner_email)
        print(f"Admin digest sent to {owner_email}")


if __name__ == "__main__":
    main()
