FROM subuser-firefox

#ADD http://archive.canonical.com/pool/partner/a/adobe-flashplugin/adobe-flashplugin_11.2.202.378.orig.tar.gz flash-plugin
RUN echo "deb http://archive.ubuntu.com/ubuntu/ precise-security multiverse" >> /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y flashplugin-installer
#RUN mkdir -p /usr/lib/mozilla/plugins
#RUN cp flash-plugin/adobe-flashplugin-11.2.202.336/amd64/libflashplayer.so /usr/lib/mozilla/plugins/
#RUN chmod 655 /usr/lib/mozilla
#RUN chmod 655 /usr/lib/mozilla/plugins

