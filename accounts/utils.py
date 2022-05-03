from django.core.mail import EmailMessage
import threading
from accounts.models import User


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Util:
    @staticmethod
    def send_email(data):
        # email = EmailMessage(
        #     subject=data['email_subject'], body=data['email_body'], from_email=[data['from_email']], to=[data['to_email']])
        EmailThread(email).start()


def update_login_details(request):
    user = User.objects.get(email=request.data['email'])
    user.sign_in_counts = user.sign_in_counts + 1
    user.current_sign_in_ip = request.headers['HOST']
    user.last_sign_in_ip = request.headers['HOST']
    user.save()
    return True
