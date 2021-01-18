$(document).ready(function(){
    $(".collage").hover(function() {
        $(".collage").css("opacity", "0.8");
        $(this).css("opacity", "1.0");
    }, function() {
        $(".collage").css("opacity", "1.0");
    });
});
