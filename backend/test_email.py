import django, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'domusgestor.settings'
django.setup()
from django.core.mail import send_mail
send_mail('Test DomusGestor', 'Funciona!', None, ['domusgestor2026@gmail.com'])
print('Enviat OK')
