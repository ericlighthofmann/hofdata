from datetime import datetime
from validate_email import validate_email

from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage

def contact_me(request):

    name = request.POST['name']
    from_email = request.POST['email']
    is_valid = validate_email(from_email)
    if is_valid:
        message = request.POST['message']
        message = message + '\n' + '---------------------------' + '\n' + 'Sent by: ' + str(from_email)
        email = EmailMessage(
            'HOFDATA: Email from ' + str(name) + ' ' +str(datetime.now().date()), #subject
            message, #body
            from_email, #from
            ['ericlighthofmann@gmail.com'], #to
            reply_to=[from_email], #reply to
        )
        email.send()
        messages.success(request, 'Thank you for reaching out. I will respond as soon as I am able.')
        return redirect('/#three')

    else:
        messages.error(request, 'That does not look like a valid email address. Try again please!')
        return redirect('/#three')
