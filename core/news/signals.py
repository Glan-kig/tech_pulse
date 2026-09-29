from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django_q.tasks import async_task
from .tasks import send_welcome_email_task

@receiver(user_signed_up)
def send_welcome_email(request, user, **kwargs):
    # Avec allauth, l'utilisateur est passé dans la variable 'user'
    print(f"[SIGNAL TRIGGERED] Inscription validée via Allauth pour : {user.username}")
    
    async_task(send_welcome_email_task, user.id)
                   