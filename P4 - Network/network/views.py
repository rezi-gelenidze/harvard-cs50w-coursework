from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
import json

from .models import User, Post
from . import utils

def index(request):
    if request.method == "POST" and request.user.is_authenticated:
        # (POST) recieve new post content and save it
        content = request.POST.get('content', '')
        new_post = Post(content=content, author=request.user)
        new_post.save()

        return HttpResponseRedirect(reverse('index'))

    # (GET) paginate data and render specified page
    page_obj = utils.init_and_paginate('index', request)

    return render(request, "network/index.html", {
        'page_obj':page_obj
        })


def profile(request, username):
    if request.method == "GET":
        # query and check existance of user by username
        query = User.objects.filter(username=username)
        
        if not query.exists():
            return render(request, 'network/profile.html', {
                'message':'Profile not found.'
            })

        prof_userpk = query.first().pk

        # serialize all post data and paginate them
        page_obj = utils.init_and_paginate('profile', request, username)

        # init profile data
        profile_data = {
            'pk':prof_userpk,
            'username':username,
            'followers':utils.count_followers(prof_userpk),
            'following':utils.count_followings(prof_userpk),
            'is_following':utils.check_follow(request.user.pk, prof_userpk)
        }

        return render(request, 'network/profile.html', {
            'page_obj':page_obj,
            'profile':profile_data
        })


@login_required(login_url='/login')
def following(request):
    ''' render following page '''
    if request.method == 'GET':
        # (GET) paginate data and render specified page
        page_obj = utils.init_and_paginate('following', request)

        return render(request, "network/following.html", {
            'page_obj':page_obj
            })


def edit(request):
    ''' handling post edit POST request '''
    if request.user.is_authenticated:
        if request.method == 'POST':
            data = json.loads(request.body)
            new_content = data['new_content']
            post_id = data['post_id']
            
            if utils.validateuser(request.user.pk, post_id):
                if new_content and post_id:
                    post = Post.objects.get(pk=post_id)
                    post.content = new_content
                    post.save()

                    return JsonResponse({}, status=201)
                else:
                    return JsonResponse({}, status=400)
            else:
                return JsonResponse({}, status=403)
    else:
        return JsonResponse({}, status=302)


def like(request):
    ''' handlong like/unlike PUT request '''
    if request.method == 'PUT' and request.user.is_authenticated:
        data = json.loads(request.body)
        
        post_id = data['post_id']
        user_id = request.user.pk

        liked = utils.check_like(post_id, user_id)
        if liked:
            utils.unlike(post_id, user_id)
        else:
            utils.like(post_id, user_id)

        return JsonResponse({})
    return JsonResponse({}, status=302)


def follow(request):
    ''' handling follow/unfollow PUT request '''
    if request.method == "PUT":
        data = json.loads(request.body)
        
        profile_id = data['profile_id']
        user_id = request.user.pk
        print(data)
        following = utils.check_follow(user_id, profile_id)
        if following:
            utils.unfollow(user_id, profile_id)
        else:
            utils.follow(user_id, profile_id)

        return JsonResponse({})
    return JsonResponse({}, status=302)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
