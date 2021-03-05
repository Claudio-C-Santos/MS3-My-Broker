let input_amount_sell = document.querySelector("#stock_amount_sell");
let purchase_price = document.querySelector("#purchase_price_sell");
let total_amount_sell = document.querySelector("#money_amount_sell");
let selling_price = document.querySelector("#selling_price");

// For the partial sell page to generate the result autmatically
input_amount_sell.addEventListener("input", function() {
    let incoming = (input_amount_sell.value * selling_price.value) + (selling_price.value - purchase_price.value * input_amount_sell.value)
    total_amount_sell.value = incoming.toFixed(2)
})