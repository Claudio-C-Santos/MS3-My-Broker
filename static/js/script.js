$(document).ready(function(){
$('.modal').modal();
});

let input_amount = document.querySelector("#stock_amount");
let stock_quote = document.querySelector("#purchase_price");
let total_amount = document.querySelector("#money_amount")

// For the purchase page to generate the result autmatically
input_amount.addEventListener("input", function() {
    console.log(input_amount.value)
    console.log(stock_quote.value)
    let price = input_amount.value * stock_quote.value
    total_amount.value = price.toFixed(2);
})

let input_amount_sell = document.querySelector("#stock_amount_sell");
let stock_quote_sell = document.querySelector("#purchase_price_sell");
let total_amount_sell = document.querySelector("#money_amount_sell")

// For the partial sell page to generate the result autmatically
input_amount_sell.addEventListener("input", function() {
    console.log(input_amount_sell.value)
    console.log(stock_quote_sell.value)
    let price_sell = input_amount_sell.value * stock_quote_sell.value
    total_amount_sell.value = price_sell.toFixed(2);
})



