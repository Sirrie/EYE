from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.http import HttpResponseRedirect
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.generic import CreateView
from django_images.models import Image

from django.contrib.auth.decorators import login_required

from braces.views import JSONResponseMixin, LoginRequiredMixin
from django_images.models import Thumbnail

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

# Used to generate a one-time-use token to verify a user's email address
from django.contrib.auth.tokens import default_token_generator

from django.shortcuts import get_object_or_404
# Used to send mail from within Django
from django.core.mail import send_mail


#from forms import ImageForm
from django.views.decorators.csrf import csrf_exempt
import os
import json
import glob
from django.http import Http404
from django.conf import settings
import hashlib
import uuid
from io import FileIO, BufferedWriter
from forms import *


class qqFileUploader(object):

    BUFFER_SIZE = 10485760  # 10MB
    UPLOAD_DIRECTORY = os.path.join(settings.MEDIA_ROOT ,"upload/")

    def __init__(self, request, uploadDirectory=None, allowedExtensions=None, sizeLimit=None):
        self.allowedExtensions = allowedExtensions or []
        self.sizeLimit = sizeLimit or settings.FILE_UPLOAD_MAX_MEMORY_SIZE
        self.inputName = 'qqfile'
        self.chunksFolder = os.path.join(settings.MEDIA_ROOT, "chunks/")
        self.request = request
        self.uploadDirectory = uploadDirectory if uploadDirectory else self.UPLOAD_DIRECTORY
        self.uploadName = ''

    def getName(self):
        retName = None
        if self.request.REQUEST.get('qqfilename', None):
            if retName:
                return self.request.REQUEST['qqfilename']
            else:

                if self.request.FILES.get(self.inputName, None):
                    retName = self.request.FILES[self.inputName].name
                    
                    if retName == "blob":
                        return self.request.POST.get('qqfilename')
                    else:
                        return retName
        
        if self.request.GET.get(self.inputName, None):
            return self.request.GET.get(self.inputName)
        else:
            return self.request.FILES[self.inputName].name

    def isRaw(self):
        return False if self.request.FILES else True

    def getUploadName(self):
        return self.uploadName


    def handleUpload(self, name=None):

        if not os.access(self.uploadDirectory, os.W_OK):
            return json.dumps({"error": "Server error. Uploads directory isn't writable or executable."})


        if 'CONTENT_TYPE' not in self.request.META:
            return json.dumps({"error": "No files were uploaded."})  
        """    
        if not self.request.FILES:
            return json.dumps({"error": "Server error. Not a multipart request. Please set forceMultipart to default value (true)."})
        """

        if not self.isRaw():
            uFile = self.request.FILES[self.inputName]
            uSize = uFile.size
        else:
            uFile = self.request.REQUEST[self.inputName]
            uSize = int(self.request.META['CONTENT_LENGTH'])

        uuid_f = ''
        try:
            uuid_f = self.request.REQUEST['qquuid']
        except KeyError:
            uuid_f = hashlib.md5(str(uuid.uuid4())).hexdigest()

        if name is None:
            name = self.getName()

        # temp modification here for easy show
        #name = "%s_%s" % (uuid_f, name)

        if uSize == 0:
            return json.dumps({"error": "File is empty."})

        if uSize > self.sizeLimit:
            return json.dumps({"error": "File is too large."})

        if not (self._getExtensionFromFileName(name) in self.allowedExtensions or ".*" not in self.allowedExtensions):
            return json.dumps({"error": "File has an invalid extension, it should be one of %s." % ",".join(self.allowedExtensions)})            

        totalParts = int(self.request.REQUEST['qqtotalparts']) if 'qqtotalparts' in self.request.REQUEST else 1

        if totalParts > 1:
            chunksFolder = self.chunksFolder
            partIndex = int(self.request.REQUEST['qqpartindex'])

            if not os.access(chunksFolder, os.W_OK):
                return json.dumps({"error": "Server error. Chunks directory isn't writable or executable."})

            targetFolder = os.path.join(chunksFolder, uuid_f)  
            
            if not os.path.exists(targetFolder):
                os.mkdir(targetFolder)  

            target = os.path.join("%s/" % targetFolder, str(partIndex))

            with open(target, "wb+") as destination:
                for chunk in uFile.chunks():
                    destination.write(chunk)

            if totalParts - 1 == partIndex:
                target = os.path.join(self.uploadDirectory, name)
                self.uploadName = os.path.basename(target)

                target = open(target, "ab")

                for i in range(totalParts):
                    chunk = open("%s/%s" % (targetFolder, i), "rb")
                    target.write(chunk.read())
                    chunk.close()

                target.close()
                return json.dumps({"success": True})

            return json.dumps({"success": True})

        else:
            target = os.path.join(self.uploadDirectory, name)

            if target:
                self.uploadName = os.path.basename(target)

                try:
                    if self.isRaw():
                        chunk = self.request.read(self.BUFFER_SIZE)
                        with open(target, "wb+") as destination:
                            while len(chunk) > 0:
                                destination.write(chunk)

                                if int(destination.tell()) > self.sizeLimit:
                                    destination.close()
                                    os.unlink(target)
                                    raise

                                chunk = self.request.read(self.BUFFER_SIZE)
                    else:
                        with open(target, "wb+") as destination:
                            for chunk in uFile.chunks():
                                destination.write(chunk)

                    destination.close()
                    
                    return json.dumps({"success": True})
                except:
                    pass

            return json.dumps({"error": "Could not save uploaded file. The upload was cancelled, or server error encountered"})                

    def _getExtensionFromFileName(self, fileName):
        filename, extension = os.path.splitext(fileName)
        return extension.lower()

    @staticmethod
    def deleteFile(uuid_f):
        """
        Please add security here.....
        """
        fileToDelete = os.path.join(qqFileUploader.UPLOAD_DIRECTORY, "%s_*.*" % uuid_f.replace("?",""))

        try:
            os.unlink(glob.glob(fileToDelete)[0])
        except Exception as e:
            raise Http404

        return True

@login_required
def home(request):
    un = request.user
    print un
    photos = Photo.objects.all()
    return render(request, 'eyeapp/public.html', {'photos' : photos})

@login_required
def you(request):
    un = request.user
    photos = Photo.objects.filter(user=un)
    return render(request, 'eyeapp/you.html', {'photos' : photos})

@login_required
def explore(request):
	errors = []
	keyword = ''
	photos = []

	if not 'keyword' in request.GET or not request.GET['keyword']:
		errors.append('Please add a keyword')
	else:
		keyword = request.GET['keyword']

	if not 'keyword' in request.POST or not request.POST['keyword']:
		errors.append('Please add a keyword')
	else:
		keyword = request.POST['keyword']
        
	if keyword == '':
		photos = []
	else:
		photos = Photo.objects.filter(tags__name__in=[keyword])		#photos = Photo.objects.filter(description__contains = keyword)

	return render(request, 'eyeapp/explore.html', {'photos' : photos, 'keyword':keyword})

@login_required
def user(request):
    errors = []
    uname = ''
    photos = []

    if not 'uname' in request.GET or not request.GET['uname']:
        errors.append('Please add a uname')
    else:
        uname = request.GET['uname']
        
    if uname == '':
        photos = []
    else:
        searchUser = User.objects.get(username=uname)
        photos = Photo.objects.filter(user=searchUser)     #photos = Photo.objects.filter(description__contains = keyword)

    return render(request, 'eyeapp/user.html', {'photos' : photos})

@login_required
def findByTag(request):
    un = request.user
    print un
    photos = Photo.objects.all()
    return render(request, 'eyeapp/explore.html', {'photos' : photos})

@login_required
def findByKeyWord(request):
    un = request.user
    print un
    photos = Photo.objects.all()
    return render(request, 'eyeapp/explore.html', {'photos' : photos})

def gallery(request):
    un = request.user
    print un
    photos = Photo.objects.all()
    return render(request, 'eyeapp/gallery.html', {'photos' : photos})


@login_required
@csrf_exempt
def upload(request):
	uploader = qqFileUploader(request, os.path.join(settings.MEDIA_ROOT ,"upload/"), [".jpg", ".png", ".ico", ".*", ".avi"], 2147483648)
	print uploader.getName()
    
	print os.path.join(settings.MEDIA_ROOT ,"upload/")
	return HttpResponse(uploader.handleUpload())

@login_required
@csrf_exempt
def pinfo(request):
    pid = ''
    if not 'pid' in request.POST or not request.POST['pid']:
        errors.append('pid')
    else:
        pid = request.POST['pid']
    curPhoto = Photo.objects.get(id=pid)
    response_data = {}
    response_data['pid'] = pid
    response_data['imgurl'] = curPhoto.imgurl
    response_data['description'] = curPhoto.description
    items = Comments.objects.filter(photo=curPhoto)
    print 'the length' + str(len(items))
    response_data['items'] = [item.as_json() for item in items]
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required
@csrf_exempt
def post(request):
    description = ''
    imgurl = ''
    tagstring = ''
    tags = []
    errors=[]
    if not 'description' in request.POST or not request.POST['description']:
        errors.append('Please add a description')
    else:
        description = request.POST['description']

    if not 'imgurl' in request.POST or not request.POST['imgurl']:
        errors.append('Please add a imgurl')
    else:
        imgurl = request.POST['imgurl']

    if not 'tags' in request.POST or not request.POST['tags']:
        errors.append('Please add a tag')
    else:
        tagstring = request.POST['tags']
	tags = tagstring.split()  
	new_photo = Photo.objects.create(user = request.user, description=description, imgurl=imgurl, thumbnail="tmp")
    for tag in tags:
        new_photo.tags.add(tag)
    new_photo.save()
    return HttpResponse()

@login_required
@csrf_exempt
def comment(request):
    errors = []
    pid = ''
    comment = ''
    if not 'pid' in request.POST or not request.POST['pid']:
        errors.append('Please add a pid')
    else:
        pid = request.POST['pid']

    if not 'comment' in request.POST or not request.POST['comment']:
        errors.append('Please add a comment')
    else:
        comment = request.POST['comment']

    c_photo = Photo.objects.get(id=pid)

    new_comment = Comments(photo=c_photo, text=comment, user=request.user)
    new_comment.save()

    context = {'comment':new_comment}
    return render(request,'eyeapp/com.html',context)

def sign_in(request):

    if request.method == 'GET':
        return render(request,'eyeapp/login.html')
    print(request.POST)
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    error=[];
    if user is not None:
        if user.is_active:
            login(request,user)
            print("this is the right user "+ user.username)
            # Redirect to a success page.
            return redirect('/')
        else:
            error=['disabled accoutn']
            return render(request,'eyeapp/login.html',error)
            # Return a 'disabled account' error message
    else:
        error=['invalid login']
        return render(request,'eyeapp/login.html',error)
        # Return an 'invalid login' error message.

def register(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'eyeapp/register.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = RegistrationForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'eyeapp/register.html', context)

    # If we get here the form data was valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password1'],
                                        email=form.cleaned_data['email'],)
    new_user.save()

    print "hello finished"
    print new_user.username
    print new_user.email
    # Logs in the new user and redirects to his/her todo list
   # new_user = authenticate(username=form.cleaned_data['username'], \
    #                        password=form.cleaned_data['password1'])
    #login(request, new_user)
    # return redirect('/eye/')
# Generate a one-time use token and an email message body
    token = default_token_generator.make_token(new_user)

    email_body = """
Welcome to the EyE~.  Please click the link below to
verify your email address and complete the registration of your account:

  http://%s%s
""" % (request.get_host(), 
       reverse('confirm', args=(new_user.username, token)))

    send_mail(subject="Verify your email address",
              message= email_body,
              from_email="eyeapp@CMU.edu",
              recipient_list=[new_user.email])

    #context['email'] = form.cleaned_data['email']
    return render(request,'eyeapp/need_confirm.html',context)


@transaction.commit_on_success
def confirm_registration(request, username, token):
    user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    # Otherwise token was valid, activate the user.
    user.is_active = True
    user.save()
    return render(request, 'eyeapp/confirmed.html', {})




