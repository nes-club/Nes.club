from django.template import loader

from notifications.email.sender import send_transactional_email
from users.models.user import User


def send_invited_email(from_user: User, to_user: User):
    invite_template = loader.get_template("emails/invited.html")
    send_transactional_email(
        recipient=to_user.email,
        subject=f"🚀 Вас пригласили в сообщество",
        html=invite_template.render({"from_user": from_user, "to_user": to_user}),
        tags=["invited"]
    )
