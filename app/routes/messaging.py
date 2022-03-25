# These routes are an example of how to use data, forms and routes to create
# a forum where a posts and comments on those posts can be
# Created, Read, Updated or Deleted (CRUD)

from flask.helpers import url_for
from app import app, login
import mongoengine.errors
from flask import render_template, flash, redirect
from flask_login import current_user
from app.classes.data import Chat, Message
from app.classes.forms import ChatForm, MessageForm
from flask_login import login_required
import datetime as dt

# This is the route to list all posts
@app.route('/chat/list')
@login_required
def chatList():
    # This retrieves all of the 'posts' that are stored in MongoDB and places them in a
    # mongoengine object as a list of dictionaries name 'posts'.
    chats = Chat.objects()
    # This renders (shows to the user) the posts.html template. it also sends the posts object 
    # to the template as a variable named posts.  The template uses a for loop to display
    # each post.
    return render_template('chats.html',chats=chats)

# This route renders a form for the user to create a new post
@app.route('/chat/new', methods=['GET', 'POST'])
# This means the user must be logged in to see this page
@login_required
# This is a function that is run when the user requests this route.
def chatNew():
    # This gets a form object that can be displayed on the template
    form = ChatForm()

    # This is a conditional that evaluates to 'True' if the user submitted the form successfully 
    if form.validate_on_submit():

        # This stores all the values that the user entered into the new post form. 
        # Post() is a method for creating a new post. 'newPost' is the variable where the object
        # that is the result of the Post() method is stored.  
        newChat = Chat(
            # the left side is the name of the field from the data table
            # the right side is the data the user entered which is held in the form object.
            receiver = form.receiver.data,
            sender = current_user.id,
            modifydate = dt.datetime.utcnow
        )
        # This is a metod that saves the data to the mongoDB database.
        newChat.save()
        #use two users IDs together for chat ID?
        return redirect(url_for('chat',pchatID=newChat.id))

    return render_template('chatform.html',form=form)

@app.route('/chat/<chatID>')
@login_required
def chat(chatID):
    chat = Chat.objects.get(id=chatID)
    try:
        messages = Message.objects(chat=chat)
    except mongoengine.errors.DoesNotExist:
        messages = None

    return render_template('chat.html',chat=chat,messages=messages)

@app.route('/message/new/<chatID>', methods=['GET', 'POST'])
@login_required
def messageNew(chatID):
    chat = Chat.objects.get(id=chatID)
    #i dont wanna use new form page, input on chat page
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

@app.route('/message/edit/<messageID>', methods=['GET', 'POST'])
@login_required
def messageEdit(messageID):
    editMessage = Message.objects.get(id=messageID)
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
