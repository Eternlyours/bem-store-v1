var style = {
    base: {
        color: "#32325d",
    }
};

var card = elements.create("card", {
    style: style
});
card.mount("#card-element");

card.on('change', function (event) {
    var displayError = document.getElementById('card-errors');
    if (event.error) {
        displayError.textContent = event.error.message;
    } else {
        displayError.textContent = '';
    }
});

stripe.confirmCardPayment(clientSecret, {
    payment_method: {
        card: card,
        billing_details: {
            name: 'Jenny Rosen'
        }
    },
    setup_future_usage: 'off_session'
}).then(function (result) {
    if (result.error) {
        // Show error to your customer
        console.log(result.error.message);
    } else {
        if (result.paymentIntent.status === 'succeeded') {

            // The PaymentMethod ID can be found on result.paymentIntent.payment_method
        }
    }
});