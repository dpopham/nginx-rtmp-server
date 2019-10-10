# nginx-rtmp-server
Python application demonstrating secure rtmp streaming

This is not intended to be a self contained app that you simply deploy and use - it is part of a tutorial I put together on setting up a secure rtmp service with nginx and OAuth (via Nextcloud Cloud server).

With nginx setup complete, this application configured and running with a valid OAuth service, then it is possible to stream from devices such as a GoPro or from a file using ffmpeg.  

As an example of streaming using Big Buck Bunny (I assume you hve your own copy downloaded somewhere) with no encryption:

ffmpeg \
 -stream_loop -1 \
 -re \
 -i bbb.mp4 \
 -c:v libx264 \
 -preset veryfast \
 -maxrate 3000k \
 -bufsize 6000k \
 -pix_fmt yuv420p \
 -g 50 \
 -c:a aac \
 -b:a 160k \
 -ac 2 \
 -ar 44100 \
 -f flv \
 rtmp://YOUR_SERVER_URL/live_clear/Big_Buck_Bunny

To change to an encrypted stream requiring users to login via your OAuth service, the publish URL changes from live_clear to live.  For example:

ffmpeg \
 -stream_loop -1 \
 -re \
 -i bbb.mp4 \
 -c:v libx264 \
 -preset veryfast \
 -maxrate 3000k \
 -bufsize 6000k \
 -pix_fmt yuv420p \
 -g 50 \
 -c:a aac \
 -b:a 160k \
 -ac 2 \
 -ar 44100 \
 -f flv \
 rtmp://YOUR_SERVER_URL/live/Big_Buck_Bunny
 
 
