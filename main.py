# This is the file that you run to start your app

from app import app
# import -m

if __name__ == "__main__":
    
    #os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
    
    app.run(debug="True", ssl_context=('cert.pem', 'key.pem'))