### Part 1
This directory contains a webserver.py, a mod_chatserver.py, an index.html, and a chat_history.txt
1) How to start mod_chatserver.py
  - First run the mod_chatserver.py to receive its location. 
  - The chat server accepts 2 arguments: [CHAT_PORT] and [SHORTLIVED_TCP]. 
  - Run with command: python3 mod_chatserver.py 8822 8823 where 8822 [CHAT_PORT] and 8823 is [SHORTLIVED_TCP] (change port if it is used).
  - The [CHAT_PORT] is where the chat server always listens to incoming message and connection from the terminal clients.
  - The [SHORTLIVED_TCP] is where the web server listens to incoming http request from the web clients, a short-lived TCP connection.
  - The chat server will also print out the interface it's listening on (ex: hawk.cs.umanitoba.ca) and 2 ports it's listening on
2) How to start webserver.py
   - The webserver accepts 2 arguments: [WEB_PORT] and [CHAT_HOST:SHORTLIVED_TCP]
   - Run with command: python3 webserver.py 8824 hawk.cs.umanitoba.ca:8823 where 8824 is the port used to serve webpage [WEB_PORT] and 8823 is the [SHORTLIVED_TCP] to communicate with the chat server.
   - The webserver will print out the interface it's listening on (ex: eagle.cs.umanitoba.ca:8824)
3) The webpage
   - Stored in index.html.
   - Use the link of the interface on the browser to serve the webpage. Go to browser, paste eagle.cs.umanitoba.ca:8824 and search.
   - The webpage will display the chat history and allow users to send messages.
   - Note: the webpage updates messages normally when running on its own, but if we open it in another tab, it would show current messages normally but doesn't synchronize messages like expected.
  