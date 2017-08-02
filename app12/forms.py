from django import forms
from models import UserModel, PostModel, LikeModel, CommentModel

#creating a signup form
class SignUpForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['email', 'username', 'full_name', 'password']


#creating a login form
class LoginForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['username', 'password']


#creating a post form
class PostForm(forms.ModelForm):
    class Meta:
        model = PostModel
        fields = ['image', 'caption']

#creating a like form
class LikeForm(forms.ModelForm):
    class Meta:
        model = LikeModel
        fields = ['post']

#creating a comment form
class CommentForm(forms.ModelForm):
    class Meta:
        model = CommentModel
        fields = ['comment_text', 'post']
