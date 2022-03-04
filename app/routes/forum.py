# These routes are an example of how to use data, forms and routes to create
# a forum where a posts and comments on those posts can be
# Created, Read, Updated or Deleted (CRUD)

from flask.helpers import url_for
from app import app, login
import mongoengine.errors
from flask import render_template, flash, redirect
from flask_login import current_user
from app.classes.data import Post, Comment
from app.classes.forms import PostForm, CommentForm
from flask_login import login_required
import datetime as dt

# This is the route to list all posts
@app.route('/post/list')
# This means the user must be logged in to see this page
@login_required
def postList():
    # This retrieves all of the 'posts' that are stored in MongoDB and places them in a
    # mongoengine object as a list of dictionaries name 'posts'.
    posts = Post.objects()
    # This renders (shows to the user) the posts.html template. it also sends the posts object 
    # to the template as a variable named posts.  The template uses a for loop to display
    # each post.
    return render_template('posts.html',posts=posts)

# This route renders a form for the user to create a new post
@app.route('/post/new', methods=['GET', 'POST'])
# This means the user must be logged in to see this page
@login_required
# This is a function that is run when the user requests this route.
def postNew():
    # This gets a form object that can be displayed on the template
    form = PostForm()

    # This is a conditional that evaluates to 'True' if the user submitted the form successfully 
    if form.validate_on_submit():

        # This stores all the values that the user entered into the new post form. 
        # Post() is a method for creating a new post. 'newPost' is the variable where the object
        # that is the result of the Post() method is stored.  
        newPost = Post(
            # the left side is the name of the field from the data table
            # the right side is the data the user entered which is held in the form object.
            subject = form.subject.data,
            content = form.content.data,
            author = current_user.id,
            # This sets the modifydate to the current datetime.
            modifydate = dt.datetime.utcnow
        )
        # This is a metod that saves the data to the mongoDB database.
        newPost.save()

        return redirect(url_for('post',postID=newPost.id))

    return render_template('postform.html',form=form)

@app.route('/post/<postID>')
@login_required
def post(postID):
    post = Post.objects.get(id=postID)
    try:
        comments = Comment.objects(post=post)
    except mongoengine.errors.DoesNotExist:
        comments = None

    return render_template('post.html',post=post,comments=comments)

@app.route('/post/delete/<postID>')
@login_required
def postDelete(postID):
    deletePost = Post.objects.get(id=postID)
    if current_user == deletePost.author:
        deletePost.delete()
        flash('The Post was deleted.')
    else:
        flash("You can't delete a post you don't own.")
    posts = Post.objects()  
    return render_template('posts.html',posts=posts)

@app.route('/post/edit/<postID>', methods=['GET', 'POST'])
@login_required
def postEdit(postID):
    editPost = Post.objects.get(id=postID)
    if current_user != editPost.author:
        flash("You can't edit a post you don't own.")
        return redirect(url_for('post',postID=postID))
    form = PostForm()
    if form.validate_on_submit():
        editPost.update(
            subject = form.subject.data,
            content = form.content.data,
            modifydate = dt.datetime.utcnow
        )
        return redirect(url_for('post',postID=postID))

    form.subject.data = editPost.subject
    form.content.data = editPost.content

    return render_template('postform.html',form=form)

@app.route('/comment/new/<postID>', methods=['GET', 'POST'])
@login_required
def commentNew(postID):
    post = Post.objects.get(id=postID)
    form = CommentForm()
    if form.validate_on_submit():
        newComment = Comment(
            author = current_user.id,
            post = postID,
            content = form.content.data
        )
        newComment.save()
        return redirect(url_for('post',postID=postID))
    return render_template('commentform.html',form=form,post=post)

@app.route('/comment/edit/<commentID>', methods=['GET', 'POST'])
@login_required
def commentEdit(commentID):
    editComment = Comment.objects.get(id=commentID)
    if current_user != editComment.author:
        flash("You can't edit a comment you didn't write.")
        return redirect(url_for('post',postID=editComment.post.id))
    post = Post.objects.get(id=editComment.post.id)
    form = CommentForm()
    if form.validate_on_submit():
        editComment.update(
            content = form.content.data,
            modifydate = dt.datetime.utcnow
        )
        return redirect(url_for('post',postID=editComment.post.id))

    form.content.data = editComment.content

    return render_template('commentform.html',form=form,post=post)   

@app.route('/comment/delete/<commentID>')
@login_required
def commentDelete(commentID): 
    deleteComment = Comment.objects.get(id=commentID)
    deleteComment.delete()
    flash('The comments was deleted.')
    return redirect(url_for('post',postID=deleteComment.post.id)) 
