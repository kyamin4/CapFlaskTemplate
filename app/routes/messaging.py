# These routes are an example of how to use data, forms and routes to create
# a forum where a posts and comments on those posts can be
# Created, Read, Updated or Deleted (CRUD)

from flask.helpers import url_for
from sqlalchemy import false
import win32api
from app import app, login
import mongoengine.errors
from flask import render_template, flash, redirect, session
from flask_login import current_user
from app.classes.data import Chat, Message, User
from app.classes.forms import ChatForm, MessageForm
from flask_login import login_required
import datetime as dt

from app.routes.default import posts

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
    existingChat = False
    allChats = Chat.objects()
    form = ChatForm()

    # This is a conditional that evaluates to 'True' if the user submitted the form successfully 
    if form.validate_on_submit():
        try:
            receiver = User.objects.get(username=form.receivername.data)
        except:
            win32api.MessageBox(0, 'User not found, check for exactness!', 'Error', 0x00001000)
            return redirect(url_for('chatNew'))

        # This stores all the values that the user entered into the new post form. 
        # Post() is a method for creating a new post. 'newPost' is the variable where the object
        # that is the result of the Post() method is stored.  
        newChat = Chat(
            # the left side is the name of the field from the data table
            # the right side is the data the user entered which is held in the form object.
            receivername = form.receivername.data,
            receiverid = getuserid(form.receivername.data),
            sendername = current_user.username,
            senderid = current_user.id,
            modifydate = dt.datetime.utcnow
        )
        #check if theres an existing chat between the two users. 
        for chat in allChats:
            if((current_user.id == chat.senderid and newChat.receivername == chat.receivername) or (current_user.id == chat.receiverid and chat.sendername == newChat.receivername)):
                existingChat = True
                chatID=chat.id
                return redirect(url_for('chat',chatID = chatID))
            else:
                existingChat = False

        if existingChat:
            win32api.MessageBox(0, 'A chat between you and target user already exists!', 'Error', 0x00001000)
            return redirect(url_for('chatNew'))
        else:
            newChat.save()
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
    form = MessageForm()
    if form.validate_on_submit():
        newMessage = Message(
            author = current_user.id,
            chat = chat,
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


def getuserid(username):
    allUsers = User.objects()
    for user in allUsers:
        if username == user.username:
            return user.id

