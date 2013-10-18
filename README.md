### Required Dependencies:
 - python dev headers (sudo apt-get install python2.7-dev)	
 - Twisted==11.0.0
 - httplib2==0.7.4
 - oauth2==1.5.170
 - pyOpenSSL==0.13
 - wsgiref==0.1.2
 - zope.interface==3.6.3

### TWITTER
 * Any user of this script will need to register an application with twitter: https://dev.twitter.com/apps/new 
 * When the script is run, a browser window should open prompting authorization of the user

### SHELL SCRIPT
 * There is a trivial shell script 'twitter_proc.sh' that uses a regex to display only the text elements of the generated .json

### SOURCES
#### Tweet filtering
	- [1]: https://dev.twitter.com/docs/api/1.1/post/statuses/filter
	- [2]: http://mike.teczno.com/notes/streaming-data-from-twitter.html
#### Sentiment analysis
	- [1]: http://www.laurentluce.com/posts/twitter-sentiment-analysis-using-python-and-nltk/
