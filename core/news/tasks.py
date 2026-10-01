from django.core.mail import send_mail
from django.conf import settings
from .models import Contact

def send_contact_email_task(contact_id):
    """Tâche exécutée en arrière-plan par le worker Django-Q"""
    try:
        contact = Contact.objects.get(id=contact_id)
        subject = f"[TechPulse Contact] {contact.subject}"
        message_body = f"Message de : {contact.name} ({contact.email})\n\n{contact.message}"

        send_mail(
            subject=subject,
            message=message_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        print(f"[ASYNC TASK SUCCESS] E-mail envoyé pour le contact ID: {contact_id}")
    except Contact.DoesNotExist:
        print(f"[ASYNC TASK ERROR] Contact ID {contact_id} introuvable.")
    except Exception as e:
        print(f"[ASYNC TASK SMTP ERROR] : {e}")


def send_welcome_email_task(user_id):
    """Tâche d'envoi du mail de bienvenue"""
    from django.contrib.auth.models import User
    try:
        user = User.objects.get(id=user_id)
        if user.email:
            subject = "Bienvenue sur TechPulse !"
            message = f"Bonjour {user.username}, bienvenue sur TechPulse !"

            host_list = getattr(settings, 'THIS_HOST', [])
            host_url = host_list[0] if host_list and host_list[0] else 'https://techpulse-w97t.onrender.com'
                    
            html_message = f"""
                    <div style="background-color: #0b0e14; padding: 35px 20px; min-height: 100%; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
                        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 550px; background-color: #11151c; border: 1px solid #222936; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.25);">
                            <tr>
                                <td style="padding: 35px 35px 20px 35px; border-bottom: 1px solid #1f2633;">
                                    <span style="font-family: 'Courier New', Courier, monospace; color: #0ea5e9; font-weight: bold; font-size: 14px; letter-spacing: 1px; display: block; margin-bottom: 5px;">
                                        &gt; CONNEXION INITIALISÉE_
                                    </span>
                                    <h1 style="color: #ffffff; font-size: 24px; font-weight: 700; margin: 0; letter-spacing: -0.5px;">TechPulse Terminal</h1>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 30px 35px 25px 35px;">
                                    <p style="color: #ffffff; font-size: 16px; font-weight: 600; margin-top: 0; margin-bottom: 16px;">
                                        Bonjour <span style="color: #38bdf8;">{user.username}</span>,</p>
                                    <p style="color: #94a3b8; font-size: 14px; line-height: 1.6; margin-bottom: 16px;">
                                        Toute l'équipe est ravie de vous compter parmi les membres du réseau <strong style="color: #e2e8f0;">TechPulse</strong>. Votre session a été synchronisée et sécurisée avec succès.
                                    </p>
                                    <p style="color: #94a3b8; font-size: 14px; line-height: 1.6; margin-bottom: 30px;">
                                        Vous disposez maintenant d'un accès complet pour analyser le flux technologique, sauvegarder vos articles favoris et échanger avec la communauté de développeurs.
                                    </p>
                                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                        <tr>
                                            <td align="center">
                                                <table border="0" cellpadding="0" cellspacing="0" style="border-collapse: separate;">
                                                    <tr>
                                                        <td align="center" bgcolor="#0ea5e9" style="border-radius: 6px;">
                                                            <a href="{host_url}" target="_blank" style="display: inline-block; font-size: 13px; font-weight: 700; color: #0b0e14; text-decoration: none; padding: 14px 28px; text-transform: uppercase; letter-spacing: 0.5px; border-radius: 6px; background-color: #0ea5e9;">
                                                                Accéder au Flux Principal
                                                            </a>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 20px 35px 25px 35px; border-top: 1px solid #1f2633; background-color: #0e1219; text-align: center;">
                                    <p style="font-size: 11px; font-family: 'Courier New', Courier, monospace; color: #475569; margin: 0; text-transform: uppercase; letter-spacing: 0.5px;">
                                        TechPulse Terminal v1.0 — Génération Automatique
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </div>
                    """
                    
            recipient_list = [user.email]

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                html_message=html_message,
                fail_silently=False
            )

            print(f"[ASYNC TASK SUCCESS] Mail de bienvenue envoyé à {user.email}")
    except Exception as e:
        print(f"[ASYNC TASK WELCOME ERROR] : {e}")