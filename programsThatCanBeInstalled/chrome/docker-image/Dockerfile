FROM subuser-libx11
ENV DEBIAN_FRONTEND noninteractive

ADD google-chrome-stable_current_amd64.deb /tmp/google-chrome-stable_current_amd64.deb
RUN dpkg -i /tmp/google-chrome-stable_current_amd64.deb || true
RUN apt-get install -fy

# Set up the launch wrapper
RUN echo 'google-chrome --no-sandbox' >> /usr/local/bin/chrome
RUN chmod 755 /usr/local/bin/chrome

#RUN echo "deb http://archive.ubuntu.com/ubuntu/ precise-security multiverse" >> /etc/apt/sources.list
#RUN apt-get update
#RUN apt-get install -y flashplugin-installer
