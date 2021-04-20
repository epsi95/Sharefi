#!/usr/bin/env python
# coding: utf-8

# In[4]:


# import pygrok
# install it via
# pip install pyngrok
# or
# conda install -c conda-forge pyngrok
# more about it here https://pyngrok.readthedocs.io/en/latest/index.html#installation
import os
import time

from pyngrok import conf,ngrok
import requests


# In[5]:


API_KEY = os.environ.get('API_KEY')
NGROK_AUTH_TOKEN = os.environ.get('NGROK_AUTH_TOKEN')
if(not (API_KEY and NGROK_AUTH_TOKEN)):
    raise Exception('Some of the keys are missing')


# In[2]:


# configure tunnel location ex: india 'in'
# tunnels at the same time
# you get this authtoken by signing up
# to ngrok portal here https://dashboard.ngrok.com/
# if you don't have AUTH_TOKEN your tunnel will be closed
# after fixed amount of time
# so auth token is recommended

ngrok.set_auth_token(NGROK_AUTH_TOKEN)
conf.get_default().region = "in"

# stopping monitoring thread as I don't need it
# it eats up resource
conf.get_default().monitor_thread = False


# In[ ]:


# this code starts monitoring
# if you don't need this don't use it
# as it can eat some resources

# def log_event_callback(log):
#     print(str(log))

# conf.get_default().log_event_callback = log_event_callback

# to stop the monitoring

# conf.get_default().monitor_thread = False

# for running process

# ngrok.get_ngrok_process().stop_monitor_thread()


# In[3]:


http_tunnel = ngrok.connect(addr='8080', proto='http', bind_tls=True)


# In[14]:


def start_a_tunnel(port= 8080, retry_count = 0):
    """
    This function will start a tunnel in port given port, default is 8080
    By default ngrok opens two tunnels 1. http 2. https
    I don't need http
    bind_tls=True tells ngrok to open only https tunnel
    """
    # first I will check if there is any tunnel active
    # if there is any active tunnel we will disconnect it
    for each_tunnel in ngrok.get_tunnels():
        print('Shutting down: ' + each_tunnel.public_url)
        ngrok.disconnect(each_tunnel.public_url)
        
    # now that it is made sure that there is no tunnels
    # we can open a new_tunnel
    tunnel = ngrok.connect(addr=port, proto='http', bind_tls=True)
    print('Started new tunnel @' + tunnel.public_url)
    
    # if a new tunnel started we need to update the python_anywhere url also
    url = f"https://cat95.pythonanywhere.com/setNgrokUrl?api_key={API_KEY}&new_url={tunnel.public_url}"
    response = requests.post(url)
    print(response.text)
    if(response.status_code != 200):
        retry_count += 1
        if(retry_count > 5):
            print('Failure')
            ngrok.kill()
            return
        print('Ah crap! unable to update pythonanywhere')
        print('retry count: ' + str(retry_count))
        time.sleep(5)
        start_a_tunnel((port, retry_count))
    else:
        return tunnel.public_url


# In[15]:


start_a_tunnel()

# Opening a tunnel will start the ngrok process. 
# This process will remain alive, and the tunnels open, 
# until kill is invoked, or until the Python process terminates.
ngrok_process = ngrok.get_ngrok_process()
ngrok_process.proc.wait() # we will wait till the process terminates


# In[16]:


# to shutdown ngrok process

# ngrok.kill()

