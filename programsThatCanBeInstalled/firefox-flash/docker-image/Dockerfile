FROM subuser-firefox

ADD http://archive.canonical.com/pool/partner/a/adobe-flashplugin/adobe-flashplugin_11.2.202.336.orig.tar.gz flash-plugin
RUN mkdir -p /usr/lib/mozilla/plugins
RUN cp flash-plugin/adobe-flashplugin-11.2.202.336/amd64/libflashplayer.so /usr/lib/mozilla/plugins/
#RUN chmod 655 /usr/lib/mozilla
#RUN chmod 655 /usr/lib/mozilla/plugins
