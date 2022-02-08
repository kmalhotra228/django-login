from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.urls import reverse
from login import settings
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_text
from .tokens import generate_token
from django.contrib.sites.shortcuts import get_current_site
# Create your views here.
def home(request):
    return render(request,'member/home.html')
def signupUser(request):
    if request.method == 'POST':
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username = username):
            messages.error(request,"Username only exist pls try some other username")
            return redirect(reverse("member:home"))


        if User.objects.filter(email = email):
            messages.error(request,"Email already exist")
            return redirect(reverse("member:home"))


        if len(username) > 10:
            messages.error(request,"username must be unnder 10 charcters")
            return redirect(reverse("member:home"))


        if pass1 != pass2:
            messages.error(request,"passwords didn't matches")
            return redirect(reverse("member:home"))


        if not username.isalnum():
            messages.error(request,"username must be alpha numeric")
            return redirect(reverse("member:home"))



        myuser = User.objects.create_user(username,email,pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()


        messages.success(request,"Your account has been succesfully created, Please confirm your email address inorder to confirm your email address")

        #Welcome Email
        subject = "Welcome to the mycompany"
        message = "Hello " + myuser.first_name +"!!\n"+ "Welcome here!! \n Thankyou for visting us \n We have also sent you the confirmation email, Please confirm your email address \n\n Thankyou"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject,message,from_email,to_list, fail_silently = False)

        # email address confirmation email
        current_site = get_current_site(request)
        email_subject = "Confirmation of email"
        message2 = render_to_string('email_confirmation.html',{
            'name':myuser.first_name,
            'domain':current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)

        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],

        )
        email.fail_silently = True
        email.send()


        return redirect(reverse('member:login'))

    



       

    return render(request,'member/signup_user.html')


def loginUser(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['pass1']

        user = authenticate(username=username,password= password)

        if user is not None:
            login(request,user)
            fname = user.first_name
            return render(request,'member/home.html',{'fname':fname})
        else:
            messages.error(request,"Bad Creadintials")
            return redirect(reverse("member:home"))

    return render(request,'member/login_user.html')

def logoutUser(request):
    logout(request)
    messages.success(request,'LogOut sucessfully')
    return redirect(reverse("member:home"))

def activate(request,uidb64,token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)

    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        myuser.save()
        login(request,myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect(reverse('member:login'))

    else:
        return render(request,'member/activation_failed.html')


