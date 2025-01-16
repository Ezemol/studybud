from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from.forms import RoomForm



def loginViewPage(request):
    page = 'login' # Pasa la info de que está logueado
    if request.user.is_authenticated:
        return redirect('base:home')

    if request.method == 'POST':
        # Obtenemos la info del user
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try: 
            user = User.objects.get(username=username) # Se fija si existe el user
        except: # user not found
            messages.error(request, "User doesn't exist.")

        user = authenticate(request, username=username, password=password) # Autenticación del user

        if user is not None: # If User existe
            login(request, user)
            return redirect('base:home')
        else:
            messages.error(request, "Username or password doesn't exist.") 

    context = {'page':page}
    return render(request, 'base/login_register.html', context)



def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('base:home')
        else:
            messages.error(request, 'An error ocurred during registration.')

    context = {'form':form}
    return render(request, 'base/login_register.html', context)



# Logout view
def logoutUser(request):
    logout(request)
    return redirect('base:home')



# Main view
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else '' # Obtiene q del browser 
    
    # Lista de las rooms que coincidan con q
    rooms = Room.objects.filter(
        # Filtra los topicos, nombres, descriptions que incluyan q
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )

    # Lista de topics y contador de salas
    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {
        'rooms':rooms, 
        'topics':topics, 
        'room_count':room_count, 
        'room_messages':room_messages,
    }
    return render(request, 'base/home.html', context)



# Devuelve una room en particular con id
def room(request, pk):

    # Busca la room con id y renderiza room page
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('base:room', pk=room.id)

    context = {'room': room, 'room_messages':room_messages, 'participants':participants}
    return render(request, 'base/room.html', context)



# Profile view
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_message = user.message_set.all()
    topics = Topic.objects.all()

    context = {
        'user':user,
        'rooms':rooms,
        'topics':topics,
        'room_messages':room_message,
        }
    return render(request, 'base/profile.html', context)



# Redirige al user al login si no está logueado e intenta crear room.
@login_required(login_url='base:login')
def createRoom(request):
    form = RoomForm() # Form predeterminado de django

    if request.method == 'POST':
        form = RoomForm(request.POST) # Analiza los datos del form enviado y los guarda en form

        # Si el form es válido lo guarda
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('base:home')

    # Else renderiza el form vacío
    context = {'form':form}
    return render(request, 'base/room_form.html', context)



# View para actualizar una sala
@login_required(login_url='base:login')
def updateRoom(request, pk):
    # Busca una sala por su id
    room = Room.objects.get(id=pk)

    # Precompleta los datos de la sala con el room ya creado
    form = RoomForm(instance=room)

    # Maneja si algun user quiere editar un post de otro usuario
    if request.user != room.host:
        return HttpResponse('You are not alowed here!!')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room) # Guarda en variable 'form' el form editado
        if form.is_valid: # Si es válido lo guarda en la base de datos
            form.save()
            return redirect('base:home')

    # Manda el context actualizado, ya sea con o sin cambios.
    context = {'form': form}
    return render(request, 'base/room_form.html', context)



# View para borrar sala
@login_required(login_url='base:login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk) # Busca sala por id

    # Maneja si algun user quiere eliminar un post de otro usuario
    if request.user != room.host:
        return HttpResponse('You are not alowed here!!')
    
    # If user quiere borrar sala 
    if request.method == 'POST':
        room.delete()
        return redirect('base:home')
           
    return render(request, 'base/delete.html', {
        'obj':room
    })



# View para borrar mensajes
@login_required(login_url='base:login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk) # Busca sala por id

    # Maneja si algun user quiere eliminar un post de otro usuario
    if request.user != message.user:
        return HttpResponse('You are not alowed here!!')
    
    # If user quiere borrar sala 
    if request.method == 'POST':
        message.delete()
        return redirect('base:home')
           
    return render(request, 'base/delete.html', {'obj':message})