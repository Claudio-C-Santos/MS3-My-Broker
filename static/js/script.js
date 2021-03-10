let input_amount = document.querySelector("#stock_amount");
let stock_quote = document.querySelector("#purchase_price");
let total_amount = document.querySelector("#money_amount");

// For the purchase page to generate the result autmatically
input_amount.addEventListener("input", function() {
    let price = input_amount.value * stock_quote.value
    total_amount.value = price.toFixed(3);
})



