import requests

session = requests.Session()

# The system requires authentication, so we will do a fast login first 
# Actually, wait, let's login first if there is a known easy dev account
# We will just construct a request assuming we need login
# Or we can look at the terminal logs to see what error the Flask app threw.
