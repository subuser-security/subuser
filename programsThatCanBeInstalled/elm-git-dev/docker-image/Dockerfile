FROM subuser-libelm-platform-git-dev
RUN cd Elm ; git pull
RUN TERM=linux cabal install --global /Elm/
ADD elm-git-dev /usr/bin/elm-git-dev
RUN chmod +x /usr/bin/elm-git-dev
