# this will act as a gateway to the node application
# exposed via ngrok
# the task of this application is to server
# webpages with dynamic redirect url
# the redirect url will be the ngrok tunnel
# needless to say if paid ngrok service is used then this is not required

import os


from flask import Flask, request, jsonify, make_response

NGROK_FILE_NAME = 'ngrok_url.txt'
API_KEY = os.environ.get('API_KEY')


app = Flask(__name__)




# defining a function that will read the dynamic url
def get_ngrok_url():
    try:
        if(os.path.isfile(NGROK_FILE_NAME)):
            return make_response(
                jsonify({
                "status": "success",
                "data": open(NGROK_FILE_NAME).read()
                   }), 200
                )
        else:
            return make_response(
                jsonify({
                    "status": "error",
                    "data": "file does not exists"
                    }), 404
                )
    except Exception as e:
        print(e)
        return make_response(
                jsonify({
                    "status": "error",
                    "data": "unable to read the file"
                    }), 500
                )


# defining a function to write the dynamic url
def set_ngrok_url(new_url):
    if(len(new_url) == 0):
        return make_response(
                jsonify({
                    "status": "error",
                    "data": "invalid new url"
                    }), 400
                )
    try:
        with open(NGROK_FILE_NAME, 'w') as f:
            f.write(new_url)
        return make_response(
                jsonify({
                    "status": "success",
                    "data": new_url
                    }), 200
                )
    except Exception as e:
        print(e)
        return make_response(
                jsonify({
                    "status": "error",
                    "data": "unable to write in file"
                    }), 500
                )


@app.route('/')
def hello_world():
    try:
        if(os.path.isfile(NGROK_FILE_NAME)):
            url = open(NGROK_FILE_NAME).read()
            return """<!DOCTYPE html>
                        <html>
                          <head>
                            <meta http-equiv="refresh" content="2; url='{}'" />
                            <title>Redirecting...</title>
                          </head>
                          <body>
                            <p>Please follow <a href="{}">this</a> link incase it doesn't refresh automatically.</p>
                          </body>
                        </html>""".format(url, url)
        else:
            raise Exception("file not found")
    except Exception as e:
        print(e)
        return """<!DOCTYPE html>
                <html>
                  <head>
                    <title>Error!</title>
                  </head>
                  <body>
                    <p>Oops, Something went wrong!</p>
                  </body>
                </html>""", 500


@app.route('/getNgrokUrl')
def get_ngrok_url_route():
    api_key = request.args.get('api_key')

    if (api_key and (api_key == API_KEY)):
        return get_ngrok_url()
    else:
        return make_response(
                jsonify({
                    "status": "error",
                    "data": "API key doesn't match or doesn't exists",
                    }), 401
                )


@app.route('/setNgrokUrl', methods=['POST'])
def set_ngrok_url_route():
    api_key = request.args.get('api_key')
    new_url = request.args.get('new_url')

    if (api_key and (api_key == API_KEY)):
        return set_ngrok_url(new_url)
    else:
        return make_response(
                    jsonify({
                        "status": "error",
                        "data": "API key doesn't match or doesn't exists"
                        }), 501
                    )



