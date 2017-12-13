# makolli_server
The makolli system needs to gather user's log in one server. 
So a central management server is required. 
This server should be installed Logstash and ElasticSearch to parse and store the log from user.
These three modules in this repository also should be installed in this server to communicate and share data with user server

- unzip.py
  - Unzip .zip file recieved from user server on the directory logstash watching to parse and send to elasticsearch.
  - This module run as daemon process
- alive_check.py
   - Collector send alive signal from user server regularly. That signal is caught by this module and store recieved time on the database.
   - This module run as daemon process
- user_check.py
   - If user makes an account at Makolli site, this module makes an account on the server
   - This module run as daemon process
