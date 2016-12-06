$(document).ready(function() {
    $('.materialboxed').materialbox();
    $(".button-collapse").sideNav();
    $(".dropdown-button").dropdown({
        belowOrigin: true,
        hover: true,
        alignment: 'bottom'
    });

});

function imgError(image) {
    image.onerror = "";
    image.src = "https://octodex.github.com/images/megacat.jpg";
    return true;
}
