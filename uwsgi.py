module = wsgi

socket = '/tmp/uwsgi.sock' #<- 소켓 경로(추후 nginx가 이 소켓과 소통을 할 것이다.)
chmod-socket = 666
vacuum = True

daemonize = '/home/ubuntu/flask/uwsgi.log' #<- 에러 로그를 남길 부분

die-on-term = true