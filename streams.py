import time
import operator
import os
import stat
import shutil

import settings

"""
    Streams: a simple class to manage my streams

    Depends on: 
        settings:   STREAM_FOLDER

    File layout:

        The streams require three folders to operate:
            a) /live/ - where the encrypted live segments are put
            b) /keys/ - the location of the decryption keys
            c) /live_clear/ - the location for the clear (non-encrypted)
               stream segments

        ALl of the folders are relative to the settings value of STREAM_FOLDER

        So if STREAM_FOLDER = /var/www/tv/data, the resulting data folders will
        be:
            /var/www/tv/data/live
            /var/www/tv/data/keys
            /var/www/tv/data/live_clear


    nginx config notes:

        nginx (or your favorite web server) also needs to know these paths.
        Specifically for nginx, the rtmp config needs to know where to store
        its hls keys, since it is nginx that is creating these:

           hls_key_path /var/www/tv/streams/keys/;

        and

           hls_path /var/www/tv/streams/live/;
           ....
           hls_path /var/www/tv/streams/live_clear/;
           ....

        for the encrypted and clear sections (see example nginx config files).

"""

class Streams:
    """ Simple class to manage the list of active streams """

    _active_streams = []
    _active_clear_streams = []

    def __init__(self):
        self.check_streams()

    def file_age_in_seconds(self, pathname):
        """ Return age of file on disk """
        return time.time() - os.stat(pathname)[stat.ST_MTIME]

    def cleanup_stream_files(self, filename):
        for filetype in ["/live/", "/keys/"]:
            shutil.rmtree(settings.STREAM_FOLDER + filetype + filename,
                          ignore_errors=False,
                          onerror=None)

    def cleanup_clear_stream_files(self, filename):
        for filetype in ["/live_clear/"]:
            shutil.rmtree(settings.STREAM_FOLDER + filetype + filename,
                          ignore_errors=False,
                          onerror=None)

    def check_streams(self, stream_type='clear', server=settings.SERVER_URL):
        """ Check if any existing stream files are present.
            Reason for this is if this app had approved a stream
            allowing nginx to happily accept the segments, and then
            this app restarts, there is no record of accepting
            the stream in memory - so we check the disk.  The only
            problem is if the stream also stopped while this app
            was stopped, nginx does not clean up after itself, so
            we might find a stream that is actually not streaming """

        # Encrypted streams under the /live folder
        for filename in os.listdir(settings.STREAM_FOLDER + '/live'):
            # Check if need to add stream
            if self.file_age_in_seconds(settings.STREAM_FOLDER + '/live/' + filename) < 30:
                if filename not in self._active_streams:
                    self._active_streams.append(filename)
            # Remove inactive stream
            else:
                self.cleanup_stream_files(filename)
                self._active_streams.remove(filename)

        self._active_streams.sort()

        # Unencrypted streams under the /live_clear
        for filename in os.listdir(settings.STREAM_FOLDER + '/live_clear'):
            # Check if need to add stream
            if self.file_age_in_seconds(settings.STREAM_FOLDER + '/live_clear/' + filename) < 30:
                if filename not in self._active_clear_streams:
                    self._active_clear_streams.append(filename)
            # Remove inactive stream
            else:
                self.cleanup_clear_stream_files(filename)
                self._active_clear_streams.remove(filename)

        self._active_clear_streams.sort()

        return self.streams(stream_type, server)

    def streams(self, stream_type='clear', server=settings.SERVER_URL):
        """ Return sorted list of streams filtered by received URL 
            parameter stream_type reuqesting either 'encrypted', 'clear' or 'all' .

            The response contains two items:

                name: text name of stream to display on web page (also indicates whether 
                      encrypted or public stream)
                url:  the URL to the m3u8 playlist for the stream - i.e. the index of
                      playable segments
        """
        response = []
        if stream_type in ['clear', 'all']:
            for stream in self._active_clear_streams:
                response.append({"name": stream.replace('_', ' ') + " (public)", "url": server + "/live_clear/" + stream + "/index.m3u8"})
        if stream_type in ['encrypted', 'all']:
            for stream in self._active_streams:
                response.append({"name": stream.replace('_', ' '), "url": server + "/live/" + stream + "/index.m3u8"})
        response.sort(key=operator.itemgetter('name'))
        return response
