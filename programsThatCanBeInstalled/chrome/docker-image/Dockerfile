FROM subuser-libx11
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get install -y wget

# Add Google Chrome repository
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
RUN sudo sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'

RUN apt-get update
RUN apt-get install -y google-chrome-stable

# Set up the launch wrapper
RUN echo 'google-chrome --no-sandbox' >> /usr/local/bin/chrome
RUN chmod 755 /usr/local/bin/chrome
