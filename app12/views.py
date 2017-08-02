# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth.hashers import make_password, check_password
from models import UserModel, SessionToken, PostModel, LikeModel, CommentModel
from datetime import datetime
from datetime import timedelta
from django.utils import timezone
from Instaclone.settings import BASE_DIR
from forms import SignUpForm, LoginForm, PostForm, LikeForm, CommentForm
from imgurpython import ImgurClient
from clarifai.rest import ClarifaiApp

app = ClarifaiApp(api_key='ba18384f19dc4e6b95bd1c76f356d308')


# Create  views
def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        print request.body
        if form.is_valid():
            username = form.cleaned_data['username']
            name = form.cleaned_data['full_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            print 'Here'
            # saving data to Data Base
            empty = len(username) == 0 and len(password) == 0
            if len(username) >= 4 and len(password) >= 3:
                user = UserModel(full_name=name, password=make_password(password), email=email, username=username)
                user.save()
                return render(request, 'success.html')
            else:
                text = {}
                text = "Username or password is not long enough"
                return render(request, 'index.html', {'text': text})
                # return redirect('login/')

        else:
            form = SignUpForm()
    elif request.method == "GET":
        form = SignUpForm()
        today = datetime.now()
    return render(request, 'index.html', {'today': today, 'form': form})


#  view for login
def login_view(request):
    response_data = {}
    # check if request is POST
    if request.method == "POST":
        # define form
        form = LoginForm(request.POST)
        # check if form is valid
        if form.is_valid():
            # retrieve username
            username = form.cleaned_data.get('username')
            # retrieve password
            password = form.cleaned_data.get('password')
            user = UserModel.objects.filter(username=username).first()
            # check if user exixts
            if user:
                #  if correct password
                if check_password(password, user.password):
                    print 'Here'
                    token = SessionToken(user=user)
                    # creating session token
                    token.create_token()
                    # saving session token
                    token.save()
                    # redirect to feeds page
                    response = redirect('feed/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
                else:
                    response_data['message'] = "Invalid Password! Please try again!!!"
    elif request.method == "GET":
        form = LoginForm()
    response_data['form'] = form

    return render(request, 'login.html', response_data)


#  view for feed
def feed_view(request):
    # check if user is valid
    user = check_validation(request)
    # if user exists
    if user:
        # retrieve all the posts
        posts = PostModel.objects.all().order_by('created_on')
        # load feed page
        return render(request, 'feed.html', {'posts': posts})
    else:
        # redirect to login page
        return redirect('login/')


# create view for post
def post_view(request):
    # check if user is valid
    user = check_validation(request)
    # check user exists
    if user:
        # check if request is POST
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            # check if form is valid
            if form.is_valid():
                # accept image
                image = form.cleaned_data.get('image')
                # accept caption
                caption = form.cleaned_data.get('caption')
                post = PostModel(user=user, image=image, caption=caption)
                # save the post
                post.save()
                # define path
                path = str(BASE_DIR + '/' + post.image.url)
                # define client
                client = ImgurClient('06485b886506250', 'a6f84995f175d6505426428f738a1a6a25b6753b')
                # define image url
                post.image_url = client.upload_from_path(path, anon=True)['link']
                # save the image url
                post.save()
                # display image url
                print "Image URL:" + post.image_url
                message = {"Post added successfully"}

                return redirect('/feed/')
            else:
                form = PostForm()
            # load post page
            return render(request, 'post.html', {'form': form})
    else:
        # redirect to login page
        return redirect('login/')


#  view for like
def like_view(request):
    # check if user is valid
    user = check_validation(request)
    # check user exists & request is POST
    if user and request.method == "POST":
        form = LikeForm(request.POST)
        # check if form is valid
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
            if not existing_like:
                LikeModel.objects.create(post_id=post_id, user=user)
            else:
                existing_like.delete()
            return redirect('/feed/')
    else:
        return redirect('login/')


#  view for comment
def comment_view(request):
    # check if user is valid
    user = check_validation(request)
    # check user exists & request is POST
    if user and request.method == "POST":
        form = CommentForm(request.POST)
        # check if form is valid
        if form.is_valid():
            # retrieve post id
            post_id = form.cleaned_data.get('post').id
            # accept the comment-text from the form
            comment_text = form.cleaned_data.get('comment_text')
            comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
            # save the comment
            comment.save()
            # redirect to the feeds page
            return redirect('/feed/')
        else:
            # redirect to the feeds page
            return redirect('/feed/')
    else:
        # redirect to the login page
        return redirect('login/')


# view for showing points
def point_view(request):
    # define list for urls
    urls = []
    # define list for images
    image_list = []
    response_data = {}
    # retreive all the posts from the PostModel
    posts = PostModel.objects.all()
    # iterate over all the posts
    for post in posts:
        # retrieving image url
        url = post.image_url
        # displaying image url
        print "URL's: %s" % (url)
        # appending url to urls list
        urls.append(url)
        # retrieving images
        image = post.image
        # appending images to the list of images
        image_list.append(image)
    # displaying urls
    print "URLS: %s" % (urls)
    # iterate over urls
    for u in urls:
        # print urls
        print "\n\nURL: " + u
    # define a list
    lis = []
    # iterate over the list
    for x in range(0, len(urls)):
        model = app.models.get('general-v1.3')
        response = model.predict_by_url(url=url)
        for x in range(0, len(response['outputs'][0]['data']['concepts'])):
            if response['outputs'][0]['data']['concepts'][x]['value'] >= 0.99:
                lis.append(response['outputs'][0]['data']['concepts'][x]['name'])
                # print "\n\n\n%s" % (response_data)
                # lis.append(response_data)
    # displaying the list
    print "LIST: %s" % (lis)
    # removing duplicate elements from the list
    l = list(set(lis))
    # displaying the list
    print "LIST: %s" % (l)

    # loading points page
    return render_to_response('interest.html', {'l': l})

    '''
    tags = []
    for u in urls:
        model = app.models.get('general-v1.3')
        print "Images: " + (u)
        response = model.predict_by_url(url=u)
        tags = tags.append(response['outputs'][0]['input']['data']['image']['url'])
        print "\n\n\nResponse in loop: %s" % (tags)
    print "\n\n\nResponse: %s" % (tags)

    model = app.models.get('general-v1.3')
    img = ClImage(url=url)
    response = model.predict([img])
    print response['outputs'][0]['input']['data']['image']['url']
    for x in range(0, len(response['outputs'][0]['data']['concepts'])):
        if response['outputs'][0]['data']['concepts'][x]['value'] >= 0.97:
            tags = response['outputs'][0]['data']['concepts'][x]['name']
            print "\n\n\n%s" % (tags)
    #response = model.predict_by_url(url=image_url)
    print response

    for x in range(0, len(response['outputs'][0]['data']['concepts'])):
        if response['outputs'][0]['data']['concepts'][x]['value'] >= 0.80:
            tags = response['outputs'][0]['data']['concepts'][x]['name']
            print "\n\n\n%s" % (tags)
            list.append(tags)
    print list
    print "\n\n\n%s" % (tags)

    interest = ' '.join(list)
    print interest

    for x in range(0, len(response['outputs'][0]['data']['concepts'])):
        if response['outputs'][0]['data']['concepts'][x]['value'] >= 0.80:
            tags = response['outputs'][0]['data']['concepts'][x]['name']
                  
    '''


#  view for logout
def logout_view(request):
    # load logout page
    return render(request, 'logout.html')


#  view for checking validation
def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            return session.user
    else:
        return None
'''
# win points
def win_points(user,image_url,caption):
    brands_in_caption=0
    brand_selected=""
    points=0;
    brands = BrandModel.objects.all()
    
    for brand in brands:
        if caption.__contains__(brand.name):
            brand_selected=brand.name
            brands_in_caption+=1
    image_caption = verify_image(image_url)
    if brands_in_caption==1:
        points+=50
        if image_caption.__contains__(brand_selected):
            points+=50
    else:
        if image_caption != "":
            if BrandModel.objects.filter(name=image_caption):
                points += 50
    if points >= 50:
        brand = BrandModel.objects.filter(name=brand_selected).first()
        PointsModel.objects.create(user=user,brand=brand)
        return "Post Added with 1 points"
    else:
        return "Post Added"




'''