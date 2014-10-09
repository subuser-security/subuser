What is subuser?
================

.. raw :: html

  <div id="marketingClaim"> <h1>Docker on the Desktop</h1> </div>
  <dif id="slide1"><h1>Bedrock linux meets Android permissions lists</h1></div>
  <div id="slide2"><h1>QubesOS light</h1></div>
  <div id="slide3"><h1>A package manager with an undo function</h1></div>
  <div id="slide4"><h1>Docker on the Desktop</h1></div>
 
  <script>
  slides = ["slide1"
           ,"slide2"
           ,"slide3"
           ,"slide4"]
  for(slide=0;slide<slides.length;slide++){
      currentSlideElement = document.getElementById(slides[slide])
      currentSlideElement.style.display = "none"
  }
  slide=0
  var interval = setInterval(function() {
      currentSlideElement = document.getElementById(slides[slide++])
      document.getElementById('marketingClaim').innerHTML = currentSlideElement.innerHTML;
      if(slide == slides.length) {
        slide = 0
      }
  
  }, 2000);
  </script>

Subuser is free open-source software
------------------------------------

Subuser is licenced under the LGPL v3. You can download the source code by clicking `here. <http://github.com/subuser-security/subuser>`_

`Dowload source  <http://github.com/subuser-security/subuser>`_
^^^^^^^^^^^^^^

The problem
-----------

As free software developers we like to share.  We surf the web and discover new code.  We are eager to try it out.  We live out an orgy of love and trust, unafraid that some code we cloned from git might be faulty or malicious.  We live in the 60s, carefree hippies.

This is utopia.

But sharing code isn't safe.  Every time we try out some strangers script we put ourselves at risk.  Despite the occasional claim that linux is a secure operating system, haphazardly sharing programs is NOT secure.

Furthermore, the fragmentation of linux desktop means that packaging work is needlessly repeated.  Programs that build and run on Fedora must be repackaged for Ubuntu.  This takes time away from creating great free open source software.

Subuser with Docker attack both problems symultaneously.  Docker provides an isolated and consistent environment for your programs to run in.  Subuser gives your desktop programs access to the reasources they need in order to function normally.

Subuser turns Docker containers into normal linux programs
------------------------------------------------------------

Right now I'm editing this file in `vim`.  `vim` is not installed on my computer though.  It is installed in a docker container.  However, in order to edit this file, all I had to do was type::

  $ vim README.md

Subuser turns a docker container into a normal program.  But this program is not fully privilaged.  It can only access the directory from which it was called, `not my entire home dir <http://xkcd.com/1200/>`_.  Each subuser is assigned a specific set of permissions, just like in Android.  You can see an example `permissions.json` file bellow::

  {
    "description"                : "Simple universal text editor."
    ,"maintainer"                : "Timothy Hobbs <timothyhobbs (at) seznam dot cz>"
    // Path to executable within the docker image.
    ,"executable"                : "/usr/bin/vim"
    // A list of directories the program should have Read/Write access to.
    // Paths are relative to your home. Ex: "Downloads" will access "$HOME/Downloads".
    ,"user-dirs"                 : [ 'Downloads', 'Documents' ]  // Default: []
    // Allowed the program to display x11 windows.
    ,"x11"                       : true        // Default: false
    // Allow the program access to your sound playing and recording.
    ,"sound-card"                : true        // Default: false
    // Allow the program access to Read/Write access to the directory from which it was initialized.
    ,"access-working-directory" : true        // Default: false
    // Allow the program access to the internet.
    ,"allow-network-access"      : true        // Default: false
  }
