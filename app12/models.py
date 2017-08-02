# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
import uuid

# Create your models here.

# Create a model for user
class UserModel(models.Model):
    # email field
    email = models.EmailField();
    #fullname field
    full_name = models.CharField(max_length=120)
    #username field
    username = models.CharField(max_length=120)
    #password field
    password = models.CharField(max_length=40)
    #created-on field
    created_on = models.DateTimeField(auto_now_add=True)
    #updated-on field
    updated_on = models.DateTimeField(auto_now=True)




# Create a model for SessionToken
class SessionToken(models.Model):
    #user field
    user = models.ForeignKey(UserModel)
    #session-token field
    session_token = models.CharField(max_length=255)
    #last-request-on field
    last_request_on = models.DateTimeField(auto_now=True)
    #created-on field
    created_on = models.DateTimeField(auto_now_add=True)
    #is-valid field
    is_valid = models.BooleanField(default=True)

    # function to generate a session token
    def create_token(self):
        #generating session token
        self.session_token = uuid.uuid4()




# Create a model for post
class PostModel(models.Model):
    #user field
    user = models.ForeignKey(UserModel)
    #image field
    image = models.FileField(upload_to='user_images')
    #image-url field
    image_url = models.CharField(max_length=255)
    #caption field
    caption = models.CharField(max_length=240)
    #created-on field
    created_on = models.DateTimeField(auto_now_add=True)
    #updated-on field
    updated_on = models.DateTimeField(auto_now=True)

    @property
    def like_count(self):
        return len(LikeModel.objects.filter(post=self))

    @property
    def comments(self):
        return CommentModel.objects.filter(post=self).order_by('created_on')



# Create a model for liking a post
class LikeModel(models.Model):
    #user field
    user = models.ForeignKey(UserModel)
    #post field
    post = models.ForeignKey(PostModel)
    #created-on field
    created_on = models.DateTimeField(auto_now_add=True)
    #updated-on field
    updated_on = models.DateTimeField(auto_now=True)




# Create a model for adding a comment
class CommentModel(models.Model):
    #user field
    user = models.ForeignKey(UserModel)
    #post field
    post = models.ForeignKey(PostModel)
    #comment-text field
    comment_text = models.CharField(max_length=555)
    #created-on field
    created_on = models.DateTimeField(auto_now_add=True)
    #updated-on field
    updated_on = models.DateField(auto_now=True)
