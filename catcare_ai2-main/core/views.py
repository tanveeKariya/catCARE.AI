from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth import login, authenticate, logout
import pandas as pd
import pickle
from datetime import datetime
from .models import History,Recommendation
from django.core.mail import send_mail
from django.contrib import messages
import re
import random
from django.contrib.auth.decorators import login_required

def welcome(request):
    return render(request, 'welcome.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('/login/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form':form})

def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request,request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request,username = username ,password = password)

            if user is not None:
                login(request,user)
                return redirect('/success/')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form':form})

@login_required(login_url="/login/")
def success(request):
    return render(request, 'home.html')

@login_required(login_url="/login/")
def about(request):
    return render(request, 'about.html')

@login_required(login_url="/login/")
def contact(request):
    return render(request, 'contact.html')

@login_required(login_url="/login/")
def product(request):
    return render(request, 'product.html')

def predict(request):
    if request.method == 'POST':
        machine = request.POST.get('machine')
        time = request.POST.get('time')
        component = request.POST.get('component')
        parameter = request.POST.get('parameter')
        value = request.POST.get('value')
        purchase_date = datetime.strptime(time, '%Y-%m-%d')

            # Get the current date
        current_date = datetime.now()

        # Calculate the difference in days
        days = (current_date - purchase_date).days


        with open('xgb_model.pkl', 'rb') as file:
            data = pickle.load(file)
            model = data['model']
            scaler = data['scaler']
            le_component = data['le_component']
            le_parameter = data['le_parameter']
            le_probability = data['le_probability']

        def predict_failure(machine, component, parameter, value, days):
            input_data = pd.DataFrame({
                'Machine': [machine],
                'Component': [component],
                'Parameter': [parameter],
                'Value': [value],
                'Days': [days]
            })
            
            machine_mapping = {
                'Excavator_1': 1,
                'Articulated_Truck_1': 2,
                'Backhoe_Loader_1': 3,
                'Dozer_1': 4,
                'Asphalt_Paver_1': 5
            }
            
            input_data['Machine'] = input_data['Machine'].map(machine_mapping)
            
            input_data['Component'] = le_component.transform(input_data['Component'])
            input_data['Parameter'] = le_parameter.transform(input_data['Parameter'])
            
            input_data[['Value', 'Days']] = scaler.transform(input_data[['Value', 'Days']])
            
            prediction = model.predict(input_data)
            
            probability_of_failure = le_probability.inverse_transform(prediction)
            
            return probability_of_failure[0]

        machine_input = machine
        component_input = component
        parameter_input = parameter
        value_input = value
        days_input = days

        string = ''

        if component == 'Fuel':
            if parameter == 'Temparature' or parameter == 'Level':
                string = component+' '+parameter
            else:
                string = parameter
        elif component == 'Engine':
            if parameter == 'Temparature' or parameter == 'Speed' or parameter == 'Oil Pressure':
                string = component+' '+parameter
            else:
                string = parameter
        else:
            string = parameter

        prediction = predict_failure(machine_input, component_input, parameter_input, value_input, days_input)

        username = request.user.username

        history = History(
            username = username,
            machine = machine,
            component = component,
            parameter = parameter,
            value = value,
            date = current_date,
            failure = prediction
        )
        history.save()

        recommendations = Recommendation.objects.filter(component = string)
        return render(request, 'recommendations.html',{'recommendations': recommendations,'prediction':prediction})
    
    return render(request, 'product.html')

def sendmail(request):
    if request.method == 'POST':
        subject = request.POST['subject']
        message = f'Name : {request.POST["name"]} \nEmail : {request.POST["email"]} \nMessage : \n\n{request.POST["message"]}'

        send_mail(
            subject,
            message,
            "portfoliogiru@gmail.com",
            ["girendra.singh2003@gmail.com"],
            fail_silently=False,
        )
        messages.success(request, "Mail Sent Successfully")
        return render(request, 'contact.html')

    else:
        messages.success(request, "Mail Not Sent")
        return render(request, 'contact.html')

@login_required(login_url="/login/")
def history(request):

    historys = History.objects.filter(username = request.user.username)
    return render(request,'history.html',{'historys':historys})

patterns = {
    "plat_use": r"(?i)(how.*use.*(platform|tool)|how.*make.*(prediction|predictions)|steps.*use.*(platform|tool)|guide.*(use|on|with)|instructions.*(use|for).*platform)",
    "machine_status": r"(?i)(where.*(see|find).*recommendations|what.*(machine|system).*status|how.*get.*suggestions|what.*happens.*after.*prediction|can.*(i|we).*see.*status)",
    "contact": r"(?i)(contact.*(support|team)|how.*contact.*(support|team|caterpillar)|get.*in.*touch.*(with)?.*caterpillar|connect.*to.*(caterpillar|team)|talk.*to.*(caterpillar|team)|how.*reach.*(caterpillar|team)|contact.*more|reach.*(caterpillar|team)|connect.*with.*(caterpillar|team))",
    "login_issue": r"(?i)(trouble.*log.*in|cant.*log.*in|cannot.*log.*in|login.*problem|issue.*login|i.*cant.*login|i.*can't.*login|i.*cannot.*login|i.*can't.*login)",
    "greeting": r"(?i)\b(hi|hello|hey|greetings|good morning|good afternoon|good evening)\b",
}

responses = {
    "plat_use": [
        "To use the platform, first log in to your account. Then, select the machine, component, and parameter you want to review, and click 'predict' to know the probability of failure.",
        "Log into your profile, choose the machine, component, and parameter, and click 'predict' to see the probability of failure.",
        "Use the platform by logging in, selecting the machine, component, and parameter, and hitting 'predict' to get the probability of failure.",
        "Log in, choose your machine and parameter, and then press 'predict' to know the potential risk of failure.",
        "After logging in, pick the machine, component, and parameter, and then click 'predict' to check the failure probability."
    ],
    "machine_status": [
        "After making a prediction, you'll be automatically redirected to the recommendations section where you can see detailed suggestions.",
        "Once you make a prediction, the system will show you the status and recommendations for the machine.",
        "After your prediction, you can check the machine's status and get recommendations in the recommendations section.",
        "The platform will take you to the recommendations section after your prediction, where you can see the machine's status.",
        "You can see the machine's status and get recommendations after the prediction process in the designated section."
    ],
    "contact": [
        "You can connect with the Caterpillar company via the link in the contact section or by sending an email.",
        "Feel free to reach out to the Caterpillar team using the contact link provided, or you can send them an email.",
        "To get in touch with Caterpillar, use the contact section's link or drop them an email.",
        "For contacting Caterpillar, follow the link in the contact section or email them directly.",
        "To reach Caterpillar support, use the contact details provided in the contact section or send an email."
    ],
    "login_issue": [
        "Try resetting your password first. If that doesn't work, let us know so we can connect you with the support team.",
        "If you're having trouble logging in, please reset your password. If the issue persists, we can connect you to the support team.",
        "Please attempt a password reset. If you still can't log in, we'll help you get in touch with the support team."
    ],
    "greeting": [
        "Hello there! I am CatChat. How can I help you?",
        "Hi! I'm CatChat. What can I assist you with today?",
        "Hey! How can I be of service?",
        "Greetings! How may I help you today?",
        "Hello! I'm CatChat, your assistant. What can I do for you?"
    ]
}

def get_response(user_input):
    for key, pattern in patterns.items():
        if re.search(pattern, user_input):
            return random.choice(responses[key])
    return "We'll connect you to our customer support shortly, kindly wait..."

def chat_view(request):
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []
    
    if request.method == "POST":
        user_input = request.POST.get('message')
        bot_response = get_response(user_input)

        request.session['chat_history'].append({'user': user_input, 'bot': bot_response})
        request.session.modified = True

        return render(request, 'chat.html', {
            'chat_history': request.session['chat_history']
        })
    
    return render(request, 'chat.html', {
        'chat_history': request.session.get('chat_history', [])
    })


def user_logout(request):
    request.session.pop('chat_history', None)
    logout(request)
    return redirect('/')