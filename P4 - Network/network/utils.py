from .models import Post, User, Like, Follow
from django.core.paginator import Paginator


def check_like(post_id, user_id):
    ''' check if specific user has liked specific post '''
    if Like.objects.filter(user=user_id, post=post_id).exists():
        return True
    return False


def count_like(post_id):
    ''' count number of likes of specific post '''
    return Like.objects.filter(post=post_id).count()


def like(post_id, user_id):
    ''' 
    record like of specific post by specific 
    user if records doesn't alredy exist 
    '''
    check = Like.objects.filter(post=post_id, user=user_id).exists()
    if not check:
        try:
            user = User.objects.get(pk=user_id)
            post = Post.objects.get(pk=post_id)
        
            new_like = Like(post=post, user=user)
            new_like.save()
        except:
            return False
    return True        


def unlike(post_id, user_id):
    ''' delete like record by specific user if record exists '''
    query = Like.objects.filter(post=post_id, user=user_id)

    if query: 
        try:
            query.delete()
            return True
        except:
            pass

    return False
            

def count_followings(follower_id):
    return Follow.objects.filter(follower=follower_id).count()


def list_followings(follower_id):
    queryset = Follow.objects.filter(follower=follower_id)
    followings = []
    for row in queryset:
        followings.append(row.following)
    return followings


def count_followers(following_id):
    return Follow.objects.filter(following=following_id).count()


def follow(follower_id, following_id):
    """ record follow if record doesn't already exist """
    check = Follow.objects.filter(follower=follower_id, following=following_id).exists()
    # if already exists, skip re-recording and return true
    if check:
        return True

    # if self-follow is requested, return false
    if following_id == follower_id:
        return False

    # add record
    try:
        follower = User.objects.get(pk=follower_id)
        following = User.objects.get(pk=following_id)

        new_follow = Follow(follower=follower, following=following)
        new_follow.save()

        return True
    except:
        return False


def unfollow(follower_id, following_id):
    ''' delete follow record by specific follower and following users if record exists '''
    query = Follow.objects.filter(follower=follower_id, following=following_id)

    if query: 
        try:
            query.delete()
            return True
        except:
            pass

    return False


def check_follow(follower_id, following_id):
    ''' check if specific user has followed specific user '''
    if Follow.objects.filter(follower=follower_id, following=following_id).exists():
        return True
    return False


def serialize_all(serialize_for, user_id, username=None):
    '''
         query query set and create dictionary from its data,
        then add liked status and liked count

        if username is present, load queryset for a specific username profile
    '''

    # query for profile page
    if serialize_for == 'profile':
        profile_user = User.objects.get(username=username)
        queryset = list(Post.objects.filter(author=profile_user).order_by('-timestamp'))

    # query for index page
    elif serialize_for == 'index':
        queryset = list(Post.objects.all().order_by('-timestamp'))

    # query for following page
    elif serialize_for == 'following':
        followings = list_followings(user_id)
        queryset = list(Post.objects.filter(author__in=followings).order_by('-timestamp'))

    # initialize query data and add likecount number and liked status
    # turning each query of queryset imto dict of data
    for i in range(len(queryset)):
        post = queryset[i]
        data = post.serialize()
    
        data['likecount'] = count_like(post.pk)
        data['liked'] = check_like(post.pk, user_id)
        
        # replace query with newly created dict
        queryset[i] = data
            
    return queryset


def validateuser(user_id, post_id):
    ''' validate user when editing post if request.user is post author '''
    post = Post.objects.filter(pk=post_id)
    if post.exists():
        post = post.first()
        if post.author.pk == user_id:
            return True
    return False


def init_and_paginate(page, request, username=None):
    ''' initialize all data and paginate them  for requested page
    
        page - which page is requested to initialize data for (following, index or profile)
        request - request object for accessing GET param and user pk
    
    '''
    page_num = request.GET.get('page', 1)

    if page == 'profile':
        posts = serialize_all(page, request.user.pk, username)
    else:
        posts = serialize_all(page, request.user.pk)

    # paginate
    posts_paginated = Paginator(posts, 10)
    page_obj = posts_paginated.get_page(page_num)

    return page_obj