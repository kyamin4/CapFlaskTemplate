# The purpose of this file is to hold sensitive information that you don't want to 
# post publicly to GitHub.  This file is excluded from being sent to github by .gitignore

def getSecrets():
    secrets = {
        'MAIL_PASSWORD':'Admin',
        'MAIL_USERNAME':'JonathanYimCapstone',
        'MONGO_HOST':'mongodb+srv://JonathanYim:<password>@cluster0.jmywb.mongodb.net/myFirstDatabase?retryWrites=true&w=majority',
        'MONGO_DB_NAME':'JonathanYimCapstone'
        }
    return secrets