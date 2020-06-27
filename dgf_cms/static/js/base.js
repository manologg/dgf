$(window).on("load", function() {
    desktopStickyOffset = $('#navigation-bar').offset().top;
    mobileStickyOffset = $('#mobile-navigation-bar').offset().top;

    var sticky = false;
    $(window).scroll(function(){

        var scroll = $(window).scrollTop();

        if (mobileNavigationBarIsVisible()) {

            // MOBILE
            console.log("scroll: " + scroll);
            console.log("mobileStickyOffset: " + mobileStickyOffset);
            if (scroll > mobileStickyOffset) {
                $("#mobile-navigation-bar").addClass("sticky");
                if (!sticky) {
                    $("#mobile-navigation-bar-language-chooser").slideDown("slow");
                    sticky = true;
                }
            }
            else {
                $("#mobile-navigation-bar").removeClass("sticky");
                if (sticky) {
                    $("#mobile-navigation-bar-language-chooser").hide("slow");
                    sticky = false;
                }
            }
        }
        else {

            // DESKTOP

            if (scroll > desktopStickyOffset) {
                $("#navigation-bar").addClass("sticky");
                if (!sticky) {
                    $("#navigation-bar-header").show("slow");
                    $("#navigation-bar-language-chooser").slideDown("slow");
                    $("#navigation-bar").slideDown("slow");
                    sticky = true;
                }
            }
            else {
                $("#navigation-bar").removeClass("sticky");
                if (sticky) {
                    $("#navigation-bar-header").hide("slow");
                    $("#navigation-bar-language-chooser").hide("slow");
                    sticky = false;
                }
            }
        }
    });

    $("#mobile-navigation-bar-header a").click(function(e){
        e.preventDefault();
    });

    $(document).click(function(e) {
        target=e.target;
        if ($.contains($("#mobile-navigation-bar-header")[0], e.target)
            || $.contains($(".bar-container")[0], e.target)) {
            $(".bar-container").toggleClass("change");
            $(".navbar-collapse").toggle();
        }
        else if (!$.contains($("#navbarResponsive")[0], e.target)) {
            $(".navbar-collapse").hide();
            $(".bar-container").removeClass("change");
        }
    });

    $(".dropdown-toggle").click(function(){
        $(this).toggleClass("open");
        $(this).siblings().toggle();
    });

});

function mobileNavigationBarIsVisible() {
    return $('#mobile-navigation-bar').is(":visible");
}