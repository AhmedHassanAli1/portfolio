from django.http import HttpResponse
from .RegistrationForm import RegistrationForm
from django.shortcuts import render, redirect

# Create your views here.
def registration_view(request):

    # If the form has been submitted
    if request.method == "POST": 
        form = RegistrationForm(request.POST) # Create an instance of the RegistrationForm with the submitted data 
        if form.is_valid():
            user = form.save() # Save the new user in the database
            #return HttpResponse("User registered!")
            return redirect("/login") # Redirect to the home page
    else:
        form = RegistrationForm()
        print("FORM ERRORS:", form.errors)

    return render(request, "register/register.html", {"form": form})   #Render the register.html template with the form as context