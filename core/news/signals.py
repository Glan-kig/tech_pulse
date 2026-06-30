from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
import threading

@receiver(user_signed_up)
def send_welcome_email(sender, instance, created, **kwargs):
    print(f"[SIGNAL TRIGGERED] Signal lancé pour l'user : {instance.username}, Created = {created}")
    if created and instance.email:
        subject = "Bienvenue sur TechPulse !"

        message = ""
        
        # Message au format HTML poli (optionnel mais recommandé pour le style)
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
                                    Bonjour <span style="color: #38bdf8;">{instance.username}</span>,</p>
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
                                                        <a href="https://techpulse.onrender.com" target="_blank" style="display: inline-block; font-size: 13px; font-weight: 700; color: #0b0e14; text-decoration: none; padding: 14px 28px; text-transform: uppercase; letter-spacing: 0.5px; border-radius: 6px; background-color: #0ea5e9;">
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
        
        # Extraction de l'adresse email de l'utilisateur
        recipient_list = [instance.email]

        def _execute_email_send():
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=recipient_list,
                    html_message=html_message,
                    fail_silently=False  # False ici pour capturer l'erreur dans notre bloc except
                )
                print(f"[Thread] E-mail de bienvenue envoyé avec succès à {instance.email} !")
            except Exception as e:
                print(f"[Thread] Erreur lors de l'envoi du mail de bienvenue : {e}")
        
        threading.Thread(
                target=_execute_email_send
            ).start()
                   