from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .forms import TodoForm
from .models import Todo


def signupuser(request):
    if request.method == 'GET':
        return render(request, 'signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, 'signupuser.html',
                              {'form': UserCreationForm(), 'error': 'please choose another user name'})
        else:
            return render(request, 'signupuser.html',
                          {'form': UserCreationForm(), 'error': 'User name and password did not match'})


@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


def home(request):
    return render(request, 'home.html')


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'loginuser.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'loginuser.html',
                          {'form': AuthenticationForm(), 'error': 'username and password does not match'})
        else:
            login(request, user)
            return redirect('currenttodos')

@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'createtodo.html', {'form': TodoForm()})
    else:
        form = TodoForm(request.POST)

        new_todo = form.save(commit=False)
        new_todo.user = request.user
        new_todo.save()
        return redirect('currenttodos')

@login_required
def currenttodos(request):
    todos = Todo.objects.filter(user=request.user, completed__isnull=True)
    return render(request, 'currenttodos.html', {'todos': todos})

@login_required
def viewtodo(request, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id, user=request.user)
    if request.method == 'GET':

        return render(request, 'viewtodo.html', {'todo': todo, 'form': TodoForm(instance=todo)})
    else:
        new_todo = TodoForm(request.POST, instance=todo)
        new_todo.save()
        return redirect('currenttodos')

@login_required
def completetodo(request, todo_id):
    if request.method == 'POST':
        todo = get_object_or_404(Todo, pk=todo_id)
        todo.completed = timezone.now()
        todo.save()
        return redirect('currenttodos')

@login_required
def deletetodo(request, todo_id):
    if request.method == 'POST':
        todo = get_object_or_404(Todo, pk=todo_id)
        todo.delete()
        return redirect('currenttodos')