from cmath import log
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from common.forms import UserForm
from django.contrib.auth.decorators import login_required

# Create your views here.
def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)   # 사용자인증
            login(request, user) # 로그인
            return redirect('index')
    
    else:
        form = UserForm()
    return render(request, 'common/signup.html', {'form':form})


@login_required(login_url='common:login')
def profile(request):
    username = request.user.username
    name = f'{request.user.first_name} {request.user.last_name}'
    email = request.user.email
    groups = request.user.groups
    
    context = {
        'username': username,
        'name': name,
        'email': email,
        'groups': groups,
    }
    return render(request, 'common/profile.html', context)