FROM subuser-libhaskell-platform
RUN apt-get update
RUN TERM=linux apt-get install -y git libghc-terminfo-dev libghc-haskeline-dev
RUN TERM=linux cabal update
RUN git clone --branch dev https://github.com/evancz/Elm.git
#RUN git clone --branch dev https://github.com/evancz/elm-repl.git
RUN git clone --branch dev https://github.com/evancz/elm-get.git
RUN TERM=xterm cabal install --global /Elm/ /elm-get/
