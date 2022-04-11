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

# This is the route to list all chats
@app.route('/chats/list')
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
        return redirect(url_for('chat',chatID=newChat.id))

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
    form = MessageForm()
    if form.validate_on_submit():
        newMessage = Message(
            author = current_user.id,
            chat = chatID,
            content = form.content.data
        )
        newMessage.save()
        return redirect(url_for('chat',chatID=chatID))
    return render_template('messageform.html',form=form,chat=chat)

@app.route('/message/edit/<messageID>', methods=['GET', 'POST'])
@login_required
def messageEdit(messageID):
    editMessage = Message.objects.get(id=messageID)
    if current_user != editMessage.author:
        flash("You can't edit a message you didn't write.")
        return redirect(url_for('chat',chatID=editMessage.chat.id))
    chat = Chat.objects.get(id=editMessage.post.id)
    form = MessageForm()
    if form.validate_on_submit():
        editMessage.update(
            content = form.content.data,
            modifydate = dt.datetime.utcnow
        )
        return redirect(url_for('chat',chatID=editMessage.chat.id))

    form.content.data = editMessage.content

    return render_template('commentform.html',form=form,chat=chat)   

@app.route('/message/delete/<messageID>')
@login_required
def messageDelete(messageID): 
    deleteMessage = Message.objects.get(id=messageID)
    deleteMessage.delete()
    flash('The message was deleted.')
    return redirect(url_for('chat',chatID=deleteMessage.chat.id)) 
