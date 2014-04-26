FROM jayofdoom/docker-ubuntu-14.04
ENV DEBIAN_FRONTEND noninteractive
RUN dpkg --add-architecture i386
RUN TERM=linux apt-get update
RUN TERM=linux apt-get dist-upgrade -y
RUN TERM=linux apt-get install -y x11-common x11-utils libx11-6 xterm mesa-utils libgtk2.0-0:i386 libpangox-1.0-0:i386 libpangoxft-1.0-0:i386 libidn11:i386 libglu1-mesa:i386 libudev1 libudev1:i386 libglu1-mesa strace joe htop
RUN apt-get clean
RUN rm -rf /var/cache/apt/* 

