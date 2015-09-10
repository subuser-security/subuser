
Subuser - Portability, Security, Maintainability
================================================

.. raw :: html

  <script>
  var numSlides = 19
  var slide = 1
  var autoplay = true
  function moveSlidePointerNext(){
    slide++
    if(slide > numSlides) {
      slide = numSlides
    }
  }
  function moveSlidePointerPrevious(){
    slide--
    if(slide < 1) {
      slide = 1
    }
  }
  function getCurrentSlide(){
    var presentationSVG1 = document.getElementById("presentationSVG")
    var presentationSVG  = presentationSVG1.getSVGDocument()
    return presentationSVG.getElementById("id"+slide)
  }
  function redrawSlides(){
    currentSlide = slide
    // Clear
    slide = 1
    for(;slide<=numSlides;slide++){
      getCurrentSlide().setAttribute("visibility","hidden")
    }
    slide = currentSlide
    // Show current slide
    getCurrentSlide().setAttribute("visibility","visible")
  }
  function changeSlide(moveSlidePointer){
    moveSlidePointer()
    redrawSlides()
  }
  function previousSlide(){
    changeSlide(moveSlidePointerPrevious);
  }
  function nextSlide(){
    changeSlide(moveSlidePointerNext);
  }
  function toggleAutoplay(){
    playPauseButton = document.getElementById("playPauseButton")
    playPauseButtonText = "Play";
    autoplay = !autoplay 
    if(autoplay){
      playPauseButtonText = "Pause"
    }
    playPauseButton.innerHTML = playPauseButtonText
  }

  var interval = setInterval(function() {
    if(autoplay){
      nextSlide()
    }
  }, 4500);
  </script>
  <center><embed id="presentationSVG" src="_static/images/subuser-website.svg" onload="redrawSlides()" width="80%"></embed></center>
  <center><button onclick="previousSlide()">&lt;--</button><button id="playPauseButton" onclick="toggleAutoplay()">Pause</button><button onclick="nextSlide()">--&gt;</button></center>

The subuser vision
------------------

This is a talk I did back before subuser 0.3 came out. Back before I had the `XPRA X11 bridge working ` and before I had improved the update system to include "pull" style updates.

.. raw :: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/mnZ2gWRsz8Y" frameborder="0" allowfullscreen></iframe>

Howerver, the vision remains...

Unfulfilled.


Index
-----

.. toctree::
  :maxdepth: 2

  what-is-subuser
  news
  security
  installation
  Download source <https://github.com/subuser-security/subuser>
  tutorial-use
  commands/index
  packaging
  subuser-standard/standard
  developers/index
  community
  community-guidelines
  flaws
  related-projects
