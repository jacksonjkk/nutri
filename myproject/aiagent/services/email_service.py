from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

class EmailService:
    @staticmethod
    def send_ai_notification(user, title, summary, insight=None, recommendations=None, motivation=None, severity='Low'):
        """
        Sends a beautiful HTML email to the user with AI-generated insights.
        """
        subject = f"NutriAgent 🥑: {title}"
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [user.email]
        
        # In a real production app, this would be your app's frontend URL
        dashboard_url = "http://localhost:5173" if settings.DEBUG else "https://nutri-ai-agent.onrender.com"

        html_content = render_to_string('emails/notification.html', {
            'title': title,
            'username': user.username or 'NutriUser',
            'summary': summary,
            'insight': insight,
            'recommendations': recommendations if isinstance(recommendations, list) else [recommendations] if recommendations else [],
            'motivation': motivation,
            'severity': severity,
            'dashboard_url': dashboard_url,
            'subject': subject
        })
        text_content = strip_tags(html_content)

        # Create email object
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        
        try:
            msg.send(fail_silently=False)
            return True
        except Exception as e:
            print(f"Failed to send email to {user.email}: {e}")
            return False
