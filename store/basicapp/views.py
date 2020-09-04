from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from basicapp.forms import UserForm, UserProfileInfoForm,EntryForm,DealerForm
from django.contrib import messages
from basicapp.models import UserProfileInfo,UserDealers,UserStock
# Extra Imports for the Login and Logout Capabilities
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# Create your views here.
def index(request):
    return render(request, 'basicapp/index.html')


@login_required
def special(request):
    # Remember to also set login url in settings.py!
    # LOGIN_URL = '/basic_app/user_login/'
    return HttpResponse("You are logged in. Nice!\n Now you can access your database.")


@login_required
def user_logout(request):
    # Log out the user.
    logout(request)
    # Return to homepage.
    return HttpResponseRedirect(reverse('index'))


def register(request):

    registered = False

    if request.method == 'POST':

        # Get info from "both" forms
        # It appears as one form to the user on the .html page
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)

        # Check to see both forms are valid
        if user_form.is_valid() and profile_form.is_valid():

            # Save User Form to Database
            user = user_form.save()

            # Hash the password
            user.set_password(user.password)

            # Update with Hashed password
            user.save()

            # Now we deal with the extra info!

            # Can't commit yet because we still need to manipulate
            profile = profile_form.save(commit=False)

            # Set One to One relationship between
            # UserForm and UserProfileInfoForm
            profile.user = user

            # Check if they provided a profile picture
            if 'profile_pic' in request.FILES:
                print('found it')
                # If yes, then grab it from the POST form reply
                profile.profile_pic = request.FILES['profile_pic']

            # Now save model
            profile.save()

            # Registration Successful!
            registered = True

        else:
            # One of the forms was invalid if this else gets called.
            print(user_form.errors, profile_form.errors)

    else:
        # Was not an HTTP post so we just render the forms as blank.
        user_form = UserForm()
        profile_form = UserProfileInfoForm()

    # This is the render and context dictionary to feed
    # back to the registration.html file page.
    return render(request, 'basicapp/register.html',
                  {'user_form': user_form,
                           'profile_form': profile_form,
                           'registered': registered})


def user_login(request):
    if request.method == 'POST':
        # First get the username and password supplied
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Django's built-in authentication function:
        user = authenticate(username=username, password=password)

        # If we have a user
        if user:
            #Check it the account is active
            if user.is_active:
                # Log the user in.
                login(request, user)
                # Send the user back to some page.
                # In this case their homepage.
                return HttpResponseRedirect(reverse('index'))
            else:
                # If account is not active:
                return HttpResponse("Your account is not active.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(
                username, password))
            return HttpResponse("Invalid login details supplied.")

    else:
        #Nothing has been provided for username or password.
        return render(request, 'basicapp/login.html', {})


def viewdb(request):
    if request.user.is_authenticated:
        itemlist=UserStock.objects.filter(owner__username=request.user.username).order_by('dealer')
        contdict={'records': itemlist}
        return render(request, 'basicapp/view.html',contdict)
    else:
        return render(request,'basicapp/login.html')


def dbms(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            entry_form = EntryForm()
            if entry_form.is_valid():
                # entry=entry_form.save(commit=False)
                # entry.owner=request.user
                entry_form.save()
            else:
                print(entry_form.errors)
        else:
            entry_form = EntryForm(request.user)
        if request.method=='POST':
            user = User.objects.filter(id=request.user.id)
            dealer_form=DealerForm(user,request.POST)
            if dealer_form.is_valid():
                # dealer = dealer_form.save(commit=False)
                # dealer.owner = request.user
                dealer_form.save()
            else:
                print(dealer_form.errors,"error")
        else:
            dealer_form = DealerForm()
        return render(request, 'basicapp/dbms.html',{'entry_form': entry_form,'dealer_form': dealer_form})
    else:
        return render(request, 'basicapp/login.html')


def createorder(request):
    if request.user.is_authenticated:
        return render(request, 'basicapp/order.html')
    else:
        return render(request, 'basicapp/login.html')