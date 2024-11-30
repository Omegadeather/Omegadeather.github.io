## Spotify Wrapped Web App
Welcome to Rewindify, our Spotify Wrapped-inspired web application
-To start using, pull the project and run pip install -r requirements.txt in a virtual environment
-In your root directory, add file called .env (next to manage.py) and past your spotify and openai llm keys as shown in the .env.example file
-Enjoy!


## In order to view website on mobile:
- Ensure that in your firewall settings, Pycharm (or whatever IDE you are using) is allowed to communicate through firewall
- Make sure your phone and computer running the website are on the same wifi/hotspot
- Go to your favorite terminal/command prompt/shell and enter ipconfig (Windows, Rick go figure it out yourself)
- Look for the part that says "IPv4 Address" and record that number (eg 143.XXX.XX.XXX)
- In Pycharm, instead of running the server normally enter "python manage.py runserver 0.0.0.0:8000"
- On your mobile browser, enter your IPv4 address + ".8000", so "143.XXX.XX.XXX.8000"
- Enjoy!
