$(document).ready(function(){
  $('.materialboxed').materialbox();

  
});

function imgError(image) {
    image.onerror = "";
    image.src = "https://octodex.github.com/images/megacat.jpg";
    return true;
}