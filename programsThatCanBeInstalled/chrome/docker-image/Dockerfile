FROM subuser-libx11
ENV DEBIAN_FRONTEND noninteractive

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -P /tmp/
RUN dpkg -i /tmp/google-chrome-stable_current_amd64.deb || true
RUN apt-get install -fy

# Set up the launch wrapper
RUN echo 'google-chrome --no-sandbox' >> /usr/local/bin/chrome
RUN chmod 755 /usr/local/bin/chrome
