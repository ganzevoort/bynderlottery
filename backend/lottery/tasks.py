"""
Tasks for the accounts app.

- send_lottery_winner_emails
- close_lottery
"""

import logging
import itertools
import operator

from django.conf import settings
from django.utils import timezone
from celery.schedules import crontab

from service.background import celery_app
from service.email import send_templated_email

from .models import Draw


logger = logging.getLogger(__name__)


@celery_app.task(ignore_result=True)
def send_lottery_winner_emails(draw_id):
    """Send lottery winner emails."""
    draw = Draw.objects.get(id=draw_id)
    winning_ballots = draw.ballots.filter(prize__isnull=False)
    for account, ballots in itertools.groupby(
        winning_ballots.order_by("account", "prize__amount"),
        key=operator.attrgetter("account"),
    ):
        try:
            prizes = [b.prize for b in ballots]
            send_templated_email(
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=account.user.email,
                subject=f"You have won in the {draw.drawtype.name} lottery",
                template_name="lottery/email/winner",
                context_dict={
                    "user": account.user,
                    "account": account,
                    "draw": draw,
                    "prizes": prizes,
                    "total_amount": sum(p.amount for p in prizes),
                },
            )
            logger.info(f"Lottery winner email sent to {account.user.email}")
        except Exception:
            # Don't fail the whole task if one email fails.
            logger.exception(
                f"Failed to send lottery winner email to {account.user.email}"
            )
    logger.info(f"Lottery winner emails sent for draw {draw_id}")


@celery_app.task(ignore_result=True)
def close_lottery_draw(draw_id):
    """Close a lottery and send winner emails."""
    draw = Draw.objects.get(id=draw_id)
    if draw.closed:
        logger.info(f"Lottery draw {draw_id} already closed")
        return
    draw.closed = timezone.now()
    draw.save()
    # There's a limited number of prizes and a large number of ballots, keep
    # ballots as a queryset to avoid fetching more than needed.
    prizes = [p for p in draw.drawtype.prizes.all() for _ in range(p.number)]
    ballots = draw.ballots.all().order_by("?")
    for prize, ballot in zip(prizes, ballots):
        ballot.prize = prize
        ballot.save()
    logger.info(f"Lottery draw {draw_id} closed")
    send_lottery_winner_emails.delay(draw_id)


@celery_app.task(ignore_result=True)
def close_todays_draw():
    """Close today's lottery draw if one exists."""
    today = timezone.now().date()
    try:
        draw = Draw.objects.get(date=today)
        close_lottery_draw(draw.id)
        logger.info(f"Successfully closed today's draw {draw.id}")
    except Draw.DoesNotExist:
        logger.info("No draw found for today")
    except Exception:
        logger.exception("Failed to close today's draw")


# Schedule the task to run daily at 20:00
celery_app.conf.beat_schedule.update(
    {
        "close-todays-draw": {
            "task": "lottery.tasks.close_todays_draw",
            "schedule": crontab(hour=20, minute=0),
        },
    }
)
