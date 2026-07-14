"""
Section 10 deliverable: generate the HTML report, and send Discord
alerts for anything not yet alerted on (regressions, RCA reports, and
a daily digest).

Run:
    python -m sentinel.reporting.run_report
"""

from datetime import date

from .html_report import generate_html_report
from ..alerting.discord_bot import send_regression_alert, send_rca_alert, send_daily_digest
from ..repository import SentinelRepository


def main():
    path = generate_html_report()
    print(f"HTML report written to {path}")

    repo = SentinelRepository()

    regressions = repo.get_open_regressions(limit=50)
    sent = sum(send_regression_alert(r) for r in regressions)
    print(f"Sent {sent} new regression alert(s) (rest were duplicates or skipped).")

    rca_reports = repo.get_rca_reports(limit=50)
    sent_rca = sum(send_rca_alert(r) for r in rca_reports)
    print(f"Sent {sent_rca} new RCA alert(s).")

    stats = repo.get_summary_stats()
    digest_sent = send_daily_digest(stats, reference_id=str(date.today()))
    print(f"Daily digest sent: {digest_sent}")


if __name__ == "__main__":
    main()
