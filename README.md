# nginx-rtmp-server
Python application demonstrating secure rtmp streaming with nginx and OAuth

This is not intended to be a self contained app that you simply deploy and use - it is part of a tutorial I put together on setting up a secure rtmp service with nginx and OAuth (via Nextcloud Cloud server).  For more information, see the tutorial on my server https://darrenpopham.com.  Most of what you need is here, but many of the files are templates that need to be integrated into your environment.

Once you have the completed nginx setup, this application glues nginx together with an OAuth server and makes it possible to serve encrypted RTMP streams that are generated from a device, such as a GoPro, or from a video file pushed using ffmpeg.

I initially created this in response to YouTube changing its rules on publishing RTMP streams directly from devices like a GoPro.  Where once I could publish a stream only for my friends and family, I now have to have more than 1000 followers to publish from my GoPro.  I doubt I can easily create 900 different accounts for my Mom, so I came up with another solution - do it myself.  After a fair bit of digging I discovered there were few solutions for setting up your own RTMP server that also included encrypting the streams and controlling who has access to them, so I did it myself.

Publishing a stream from a device such as a GoPro follows the standard RTMP URL format, namely rtmp://YOUR_SERVER_URL/live/Stream_Name.  

Publishing a file such as Big Buck Bunny (I assume you have your own copy downloaded somewhere and saved as bbb.mp4) with no encryption:

ffmpeg -stream_loop -1 -r -i bbb.mp4 -c:v libx264 -preset veryfast -maxrate 3000k -bufsize 6000k -pix_fmt yuv420p -g 50 -c:a aac -b:a 160k -ac 2 -ar 44100 -f flv rtmp://YOUR_SERVER_URL/live_clear/Big_Buck_Bunny

To change to an encrypted stream requiring users to login via the OAuth service, the publish URL changes from live_clear to live.  For example:

ffmpeg -stream_loop -1 -re -i bbb.mp4 -c:v libx264 -preset veryfast -maxrate 3000k -bufsize 6000k -pix_fmt yuv420p -g 50 -c:a aac -b:a 160k -ac 2 -ar 44100 -f flv rtmp://YOUR_SERVER_URL/live/Big_Buck_Bunny
 
 
