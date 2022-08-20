from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User
from .pagination import paginator_context


@cache_page(20, key_prefix='home_page')
def index(request):
    obj = paginator_context(
        Post.objects.select_related('group').all(), request
    )
    context = {"page_obj": obj}
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    obj = paginator_context(
        group.posts.all(),
        request)
    context = {
        "group": group,
        "page_obj": obj
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_count = author.posts.count()
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=author
    ).exists()
    obj = paginator_context(
        author.posts.all(),
        request)
    context = {
        "author": author,
        "post_count": post_count,
        "following": following,
        "page_obj": obj
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post_id=post_id)
    posts_count = Post.objects.filter(author_id=post.author).count()
    context = {
        "post": post,
        "posts_count": posts_count,
        "form": form,
        "comments": comments
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.id and request.user != post.author:
        return redirect('posts:profile', request.user)
    is_edit = True
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id)
    context = {
        "form": form,
        "is_edit": is_edit
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, id=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    obj = paginator_context(Post.objects.select_related('author').filter(
        author__following__user=request.user), request
    )
    context = {
        'page_obj': obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    post_author = get_object_or_404(User, username=username)
    if request.user != post_author:
        Follow.objects.get_or_create(user=request.user, author=post_author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    post_author = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user=request.user,
        author=post_author
    ).delete()
    return redirect('posts:profile', username=username)
