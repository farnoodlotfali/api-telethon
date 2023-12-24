from django.shortcuts import render,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from PostAnalyzer.models import Channel, PostInitial

@login_required(login_url='login')
def home(request):
    return render(request, 'Home/home.html')
class CustomLoginView(LoginView):
    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            return '/panel'

@login_required(login_url='login')
def channel_list(request):
    channels = Channel.objects.all()
    return render(request, 'Channel/channelList.html', {'channels': channels})

@login_required(login_url='login')
def channel_detail(request, channel_id):
    channel = get_object_or_404(Channel, channel_id=channel_id)
    return render(request, 'Channel/channelDetail.html', {'channel': channel})

@login_required(login_url='login')
def post_list(request):
    posts = PostInitial.objects.all().order_by('-id')
    return render(request, 'Post/postList.html', {'posts': posts})

@login_required(login_url='login')
def post_detail(request, post_id):
    post = PostInitial.objects.get(pk=post_id)
    return render(request, 'Post/postDetail.html', {'post': post})