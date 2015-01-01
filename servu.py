#!/usr/bin/python3

import sys
import http.server
import socketserver
import juutuub
from urllib.parse import urlparse, parse_qs

if len(sys.argv) < 3:
    print("Errori: Bad arguments")
    exit()
port = int(sys.argv[1])

class myRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        print('do_GET', 'path', self.path)
        print(urlparse(self.path)[2])
        exts = ['.css', '.js', '.ico', '.png']
        if any(urlparse(self.path)[2].endswith(ext) for ext in exts):
            try:
                f = open('.'+urlparse(self.path)[2],'rb')
                if f:
                    print('tiedosto löytyi')
                self.send_response(200)
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return
            except IOError:
                self.send_error(404,'File Not Found: %s' % self.path)
                return
        if(urlparse(self.path)[2]) != '/':
            self.send_error(401,'No access to %s, only .css and .js files are accessible' % self.path)
            return
        print(parse_qs(urlparse(self.path).query))
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write('''
<html>
<head>
<title>Youtube-video-haku</title>
<link rel="stylesheet" type="text/css" href="uijui.css"/>
<script src="http://code.jquery.com/jquery-2.1.3.min.js"></script>
<script src="/jquery.jrumble.1.3.min.js"></script>
<link rel="shortcut icon" href="/favicon.png" />
<meta charset="UTF-8">
</head>
<body>
<div id="haku">
<form method=\"GET\">
<input type=\"text\" name=\"hakusana\">
<input type=\"submit\"/>
</form>
</div>
<div id="perkele"><iframe name="jepa" id="pleieri" src="https://www.google.com/logos/2014/rubiks/rubiks.html" allowfullscreen></iframe></div>
<div id="videot">
'''.encode('utf-8'))
        if 'hakusana' in parse_qs(urlparse(self.path).query):
            #self.wfile.write('Hakusana löytyi<br/>'.encode('utf-8'))
            hakusana = parse_qs(urlparse(self.path).query)['hakusana'][0]
            tulokset = juutuub.hae(100, hakusana, sys.argv[2])
            self.wfile.write(('<h1>'+hakusana+'</h1>').encode('utf-8'))
            for video in tulokset:
                #self.wfile.write(('<iframe style=\"width:25%;height:25%\" frameborder=\"0\" src=\"http://youtube.com/embed/' + video[0]+'?controls=1&autohide=1&fs=1&modestbranding=1&showinfo=0\" allowfullscreen></iframe>').encode('utf-8'))
                #self.wfile.write(('<a href=\"http://youtube.com/watch?v='+video[0]+'\" target=\"jepa\"><div class=\"vidio\" style=\"background-image: url('+video[5]+')\" /><div class=\"fader\">'+video[1]+'</div></div></a>').encode('utf-8'))
                self.wfile.write(('<a href=\"http://youtube.com/embed/'+video[0]+'?controls=1&autoplay=1&autohide=1&fs=1&modestbranding=1&showinfo=0\" target=\"jepa\"><div class=\"vidio\" style=\"background-image: url('+video[5]+')\" /><div class=\"fader\">'+video[1]+'<hr/>Views: '+str(video[2])+'<hr/>Likes: '+str(video[3])+'</div></div></a>').encode('utf-8'))
        self.wfile.write('''
        </div>
        <script>
        $('.vidio').bind({
            'mouseenter': function(){
            $(this).jrumble({x:10, y:10, rotation:4});
            },
            'mousedown': function(){
                $(this).trigger('startRumble');
            },
            'mouseup': function(){
                $(this).trigger('stopRumble');
            }
        });
        </script>
</body>
</html>
        '''.encode('utf-8'))
        return

try:
    server = socketserver.TCPServer(('', port), myRequestHandler)
    server.serve_forever()
except KeyboardInterrupt:
    print('KeyboardInterrupt: server shutting down')
    server.socket.close()
