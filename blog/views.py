from django.shortcuts import render, get_object_or_404,redirect,reverse
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from .forms import  CommentForm
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Post,Preference,Comment
import operator
from django.urls import reverse_lazy
from django.contrib.staticfiles.views import serve

from django.db.models import Q


def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'blog/home.html', context)

def search(request):
    template='blog/home.html'

    query=request.GET.get('q')

    result=Post.objects.filter(Q(title__icontains=query) | Q(author__username__icontains=query) | Q(content__icontains=query))
    paginate_by=2
    context={ 'posts':result }
    return render(request,template,context)
   


def getfile(request):
   return serve(request, 'File')


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 2


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'  # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 2

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/post_form.html'
    fields = ['title', 'content', 'file']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = 'blog/post_form.html'
    fields = ['title', 'content', 'file']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'
    template_name = 'blog/post_confirm_delete.html'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


@login_required
def postpreference(request, postid, userpreference):
        
        if request.method == "POST":
                eachpost= get_object_or_404(Post, id=postid)

                obj=''

                valueobj=''

                try:
                        obj= Preference.objects.get(user= request.user, post= eachpost)

                        valueobj= obj.value #value of userpreference


                        valueobj= int(valueobj)

                        userpreference= int(userpreference)
                
                        if valueobj != userpreference:
                                obj.delete()


                                upref= Preference()
                                upref.user= request.user

                                upref.post= eachpost

                                upref.value= userpreference


                                if userpreference == 1 and valueobj != 1:
                                        eachpost.likes += 1
                                        eachpost.dislikes -=1
                                elif userpreference == 2 and valueobj != 2:
                                        eachpost.dislikes += 1
                                        eachpost.likes -= 1
                                

                                upref.save()

                                eachpost.save()
                        
                        
                                context= {'eachpost': eachpost,
                                  'postid': postid,
                                  'pref':userpreference}

                                return render (request, 'blog/preference.html', context)

                        elif valueobj == userpreference:
                                obj.delete()
                        
                                if userpreference == 1:
                                        eachpost.likes -= 1
                                elif userpreference == 2:
                                        eachpost.dislikes -= 1

                                eachpost.save()

                                context= {'eachpost': eachpost,
                                  'postid': postid,
                                  'pref':userpreference}

                                return render (request, 'blog/preference.html', context)
                                
                        
        
                
                except Preference.DoesNotExist:
                        upref= Preference()

                        upref.user= request.user

                        upref.post= eachpost

                        upref.value= userpreference

                        userpreference= int(userpreference)

                        if userpreference == 1:
                                eachpost.likes += 1
                        elif userpreference == 2:
                                eachpost.dislikes +=1

                        upref.save()

                        eachpost.save()                            


                        context= {'eachpost': eachpost,
                          'postid': postid}

                        return render (request, 'blog/home.html', context)


        else:
                eachpost= get_object_or_404(Post, id=postid)
                context= {'eachpost': eachpost,
                          'postid': postid}

                return render (request, 'blog/home.html', context)



def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})

@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post-detail',pk=comment.post.pk)
#request,'blog/home',pk=comment.post.pk

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('post-detail',pk=comment.post.pk)
#request,'blog/home',pk=comment.post.pk


def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            context= {'id': post.pk}
            return redirect('post-detail',pk=comment.post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})