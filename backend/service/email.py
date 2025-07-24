"""
Utility function for sending emails.
"""

import os
import re
import mimetypes
import logging

from email.mime.image import MIMEImage

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import loader, TemplateDoesNotExist


logger = logging.getLogger(__name__)


def read_image(filename):
    f = settings.STATIC_ROOT / "images" / filename
    if os.path.exists(f):
        return open(f, "rb").read()


class EmailInlineImages(EmailMultiAlternatives):
    """Adds inline images"""

    def __init__(self, *args, **kwargs):
        self.inlined_images = set()
        super().__init__(*args, **kwargs)

    def inline_image(self, filename):
        if filename in self.inlined_images:
            return
        image = read_image(filename)
        if not image:
            return
        self.inlined_images.add(filename)
        payload = MIMEImage(image)
        payload.add_header("Content-ID", "<%s>" % filename)
        self.attach(payload)
        self.mixed_subtype = "related"


def send_templated_email(
    from_email,
    to,
    subject,
    template_name,
    context_dict,
    bcc=None,
    attachments=None,
    **kwargs
):
    if "subject" not in context_dict:
        context_dict["subject"] = subject
    if isinstance(to, str):
        to = [to]
    if bcc is None:
        bcc = []
    elif isinstance(bcc, str):
        bcc = [bcc]

    # Get and render the text and (optional) html part for the email
    context_dict = {"settings": settings, **context_dict}
    template = loader.get_template(template_name + ".txt")
    text_part = template.render(context_dict)
    try:
        template = loader.get_template(template_name + ".html")
        html_part = template.render(context_dict)
    except TemplateDoesNotExist:
        html_part = None

    message = EmailInlineImages(
        subject=subject,
        body=text_part,
        from_email=from_email,
        to=to,
        bcc=bcc,
        **kwargs
    )

    if html_part:
        message.attach_alternative(html_part, "text/html")
        for image in re.findall("['\"\\(]cid:([^'\"\\)]+)['\"\\)]", html_part):
            message.inline_image(image)

    for attachment in attachments or []:
        message.attach(
            attachment.name,
            attachment.file.getvalue(),
            mimetypes.guess_type(attachment.name)[0],
        )

    message.send()
