from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

# Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage


from .forms import AccountForm
from .models import Account


def register(request):
    if request.method == "POST":
        form = AccountForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            phone_number = form.cleaned_data["phone_number"]
            password = form.cleaned_data["password"]
            username = email.split("@")[0]
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
            )
            user.phone_number = phone_number
            user.save()

            # User activation
            currente_site = get_current_site(request)
            mail_subject = "Please activete your account."
            message = render_to_string(
                "accounts/account_verification_email.html",
                {
                    "user": user,
                    "domain": currente_site,
                    "uid": urlsafe_base64_encode(force_bytes(user.id)),
                    "token": default_token_generator.make_token(user),
                },
            )

            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            # messages.success(
            #     request,
            #     "Thank you, registration successfull. Please you have verification to you email address. ",
            # )
            return redirect("/account/login?command=verification&email=" + email)
    else:
        form = AccountForm()
    context = {"form": form}
    return render(request, "accounts/register.html", context)


def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = auth.authenticate(email=email, password=password)
        print(user)
        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid login credentials")
            return redirect("login")

    return render(request, "accounts/login.html")


@login_required(login_url="login")
def loggout(request):
    auth.logout(request)
    messages.success(request, "You are logged out.")
    return redirect("login")


def activate(request, uidb64=None, token=None):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulation! You account is activated.")
        return redirect("login")
    else:
        messages.error(request, "Invalide activation link.")
        return redirect("register")


@login_required(login_url="login")
def dashboard(request):
    return render(request, "accounts/dashboard.html")


def forgout_password(request):
    if request.method == "POST":
        email = request.POST["email"]
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset password email
            currente_site = get_current_site(request)
            mail_subject = "Reset your password."
            message = render_to_string(
                "accounts/reset_password_email.html",
                {
                    "user": user,
                    "domain": currente_site,
                    "uid": urlsafe_base64_encode(force_bytes(user.id)),
                    "token": default_token_generator.make_token(user),
                },
            )

            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(
                request,
                "Password reset email has been sent to your email address.",
            )
            return redirect("login")
        else:
            messages.warning(request, "Account does not exist.")
            return redirect("forgout_password")
    else:
        return render(request, "accounts/forgout_password.html")


def resetpassword_validate(request, uidb64=None, token=None):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.success(request, "Please reset your password.")
        return redirect("reset_password")
    else:
        messages.error(request, "This link has been expired.")
        return redirect("login")


def reset_password(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        if password == confirm_password:
            uid = request.session.get("uid")
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successful")
            # falta remover session uid
            return redirect("login")
        else:
            messages.error(request, "Password do not match!")
            return redirect("reset_password")
    else:
        return render(request, "accounts/reset_password.html")
