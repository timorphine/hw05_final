from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Comment, Follow
from .pagination import paginator_context, paginator_context_follow


@cache_page(20, key_prefix='home_page')
def index(request):
    context = paginator_context(Post.objects.all(), request)
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    context = {
        "group": group
    }
    context.update(paginator_context(
        Post.objects.all().filter(group=group),
        request)
    )
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_count = Post.objects.all(
    ).filter(author=author).count()
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=author
        ).exists()
    else:
        following = False
    context = {
        "author": author,
        "post_count": post_count,
        "following": following
    }
    context.update(paginator_context(
        Post.objects.all().filter(author=author),
        request)
    )
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    comments = Comment.objects.all()
    post_list = Post.objects.all().filter(author_id=post.author).count()
    context = {
        "post": post,
        "post_list": post_list,
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
    follow_list = Follow.objects.filter(user=request.user)
    post_list = Post.objects.filter(
        author__following__user=request.user)
    context = {
        'follow_list': follow_list,
        'post_list': post_list
    }
    context.update(
        paginator_context_follow(
            post_list,
            request
        )
    )
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    post_author = get_object_or_404(User, username=username)
    if request.user == post_author:
        return redirect('posts:profile', username=username)
    if Follow.objects.filter(user=request.user, author=post_author).exists():
        return redirect('posts:profile', username=username)
    Follow.objects.create(
        user=request.user,
        author=post_author
    )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    post_author = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user=request.user,
        author=post_author
    ).delete()
    return redirect('posts:profile', username=username)
