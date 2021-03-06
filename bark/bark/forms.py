from django import forms
from django.contrib.auth.models import User
from bark.models import UserProfile, Post, UserReset, Comment, getInstitution, Tag

# get data for user when they sign up
class UserForm(forms.ModelForm):
    username = forms.CharField(label="username")
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    # required to check if the user has an ac.uk domain
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        domain = getInstitution(self.cleaned_data.get('email'))

        try:
            foundExistingTag = Tag.objects.get(name__iexact = username)

            raise forms.ValidationError("There is already a tag with the same name.")
        except Tag.DoesNotExist:
            pass

        #Checking email that it's a proper ac.uk email
        if "ac.uk" not in domain:
            print "Invalid Education domain."
            self.add_error('email', "Invalid institution email given. You'll need one with .ac.uk to signup with bark.")

# get data for the User Profile
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('profile_picture',)

class PostForm(forms.ModelForm):
    class Meta:
        # provide an association between PostForm and Post.
        model = Post
        exclude = ('slug', 'views', 'author', 'creation_date', 'rating', 'tags')

        def form_valid(self, form):
            form.instance.author = self.request.user
            return super(Meta, self).form_valid(form)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('author', 'post')


# login Form (as name suggests)
class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=50, required=True)
    password = forms.CharField(label='Password', max_length=50, widget=forms.PasswordInput(), required=True)

    def clean(self):

        #Checking the existance of the username and password
        cleaned_data = super(LoginForm, self).clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        #Verify the details of the account
        try:
            user = User.objects.get(username=username)
            if not user.check_password(password):
                self.add_error('password', "Password invalid")
        except:
            self.add_error('username', "Invalid Username and Password")
            self.add_error('password', "Invalid Username and Password")
            return

# Shows the form for users requesting a reset code
# Checks the data they enter is valid
class PasswordResetForm1(forms.Form):
    username = forms.CharField(label='Username', max_length=50, required=True)
    email = forms.EmailField(label='Account Email', max_length=50, required=True)

    def clean(self):
        cleaned_data = super(PasswordResetForm1, self).clean()
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")

        #Check the user exists
        try:
            user = User.objects.get(username=username)
        except:
            self.add_error('username', 'No account with that Username found.')
            self.add_error('email','')
            return

        #Check the emails match before sending a code
        if user.email != email:
            self.add_error('email', 'Account email is incorrect.')

# Shows form to users for resetting password
# Performs a lot of the validation
class PasswordResetForm2(forms.Form):
    username = forms.CharField(label='Username', max_length=50, required=True)
    code = forms.CharField(label='Reset Code', required=True)
    new_pass1 = forms.CharField(label='New Password', max_length=50, widget=forms.PasswordInput(), required=True)
    new_pass2 = forms.CharField(label='New Password (Again)', max_length=50, widget=forms.PasswordInput(), required=True)


    def clean(self):
        cleaned_data = super(PasswordResetForm2, self).clean()
        username = cleaned_data.get('username')
        code = cleaned_data.get('code')
        new_pass1 = cleaned_data.get('new_pass1')
        new_pass2 = cleaned_data.get('new_pass2')


        #Make sure the User exists
        try:
            user = User.objects.get(username=username)
        except:
            self.add_error('username', 'No account with that Username found.')
            return

        #Make sure they have requested a reset code
        try:
            userCode = UserReset.objects.get(username=username)
        except:
            self.add_error('username', 'Given username has not requested a code. If you require one, click the link at the top of the page.')
            return

        #Catching malformed codes, if they are strings or floats
        try:
            icode = int(code)
        except:
            self.add_error('code', 'Reset code must be a number')
            return

        #Making sure the code is correct and the new password is correct
        if userCode.code != icode:
            self.add_error('code', 'Reset code is invalid.')

        if new_pass1 != new_pass2:
            self.add_error('new_pass1', "Passwords didn't match")
            self.add_error('new_pass2', "Passwords didn't match")

# Allows user to change their password
# On creation MUST be passed with request=request as for cleaning.
class PasswordChangeForm(forms.Form):
    old_pass = forms.CharField(label='Old Password', max_length=50, widget=forms.PasswordInput(), required=True)
    new_pass1 = forms.CharField(label='New Password', max_length=50, widget=forms.PasswordInput(), required=True)
    new_pass2 = forms.CharField(label='New Password (Again)', max_length=50, widget=forms.PasswordInput(), required=True)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(PasswordChangeForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(PasswordChangeForm, self).clean()
        old_pass = cleaned_data.get('old_pass')
        new_pass1 = cleaned_data.get('new_pass1')
        new_pass2 = cleaned_data.get('new_pass2')

        #Check existing password is correct
        if not self.request.user.check_password(old_pass):
            self.add_error('old_pass', "Your current password is incorrect")

        #Check the new passwords are equal
        if new_pass1 != new_pass2:
            self.add_error('new_pass1', "Your passwords didn't match.")
            self.add_error('new_pass2', "Your passwords didn't match.")

class UserProfileUpdateForm(forms.Form):
    profile_picture = forms.ImageField(label='Profile Picture', required=False)
    bio = forms.CharField(label='About Me', initial='All about you', widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(UserProfileUpdateForm, self).__init__(*args, **kwargs)
