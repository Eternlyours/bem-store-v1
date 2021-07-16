window.onload = function () {
    new WOW({
        live: true
    }).init();

    $('.single-item').slick({
        dots: true,
        infinite: true,
        arrows: false
    });
    $('.most-popular-product').slick({
        infinite: true,
        slidesToShow: 3,
        slidesToScroll: 3,
        arrows: true,
        autoplay: true,
        autoplaySpeed: 3500,
        nextArrow: $('.right-arrow-most-popular'),
        prevArrow: $('.left-arrow-most-popular'),
        responsive: [{
                breakpoint: 1200,
                settings: {
                    arrows: true,
                    centerMode: true,
                    centerPadding: '20px',
                    slidesToShow: 2,
                    slidesToScroll: 2,
                }
            },
            {
                breakpoint: 770,
                settings: {
                    arrows: true,
                    centerMode: true,
                    centerPadding: '30px',
                    slidesToShow: 1,
                    slidesToScroll: 1
                }
            },
            {
                breakpoint: 480,
                settings: {
                    arrows: false,
                    centerMode: false,
                    slidesToShow: 1,
                    slidesToScroll: 1,
                    
                }
            }
        ]
    });
    $('.most-popular-product').css('visibility', 'visible');

    if (document.getElementById('button_filter') || document.getElementById('button_close_filter')) {
        document.getElementById('button_filter').onclick = function () {
            document.getElementById('panel_filter').classList.toggle('hidden-panel');
        }
        document.getElementById('button_close_filter').onclick = function () {
            baseUrl = window.location.href.split("?")[0];
            window.history.pushState('name', '', baseUrl);
            document.getElementById('panel_filter').classList.toggle('hidden-panel');
            window.location.reload();
        }
    }

    if (document.getElementById('category-toggle')) {
        document.getElementById('category-toggle').onclick = function () {
            document.getElementById('category-toggle').classList.toggle('hide-attr-filter');
        }
    }

    function clearForm(myFormElement) {

        var elements = myFormElement.elements;

        myFormElement.reset();

        for (i = 0; i < elements.length; i++) {

            field_type = elements[i].type.toLowerCase();

            switch (field_type) {

                case "text":
                case "password":
                case "textarea":
                case "hidden":

                    elements[i].value = "";
                    break;

                case "radio":
                case "checkbox":
                    if (elements[i].checked) {
                        elements[i].checked = false;
                    }
                    break;

                case "select-one":
                case "select-multi":
                    elements[i].selectedIndex = -1;
                    break;

                default:
                    break;
            }
        }
    }
}