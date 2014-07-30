#This Dockerfile is used for testing subuser.  It is here due to the lack of relative add paths in Docker.
FROM debian
RUN apt-get update && apt-get install -y python
ADD ./ /root/subuser/
RUN /root/subuser/logic/subuser test
