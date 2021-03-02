$(document).ready(function(){
$('.modal').modal();
});

let input_amount = document.querySelector("#stock_amount");
let stock_quote = document.querySelector("#purchase_price");
let total_amount = document.querySelector("#money_amount")

input_amount.addEventListener("input", function() {
    console.log(input_amount.value)
    console.log(stock_quote.value)
    let price = input_amount.value * stock_quote.value
    total_amount.value = price.toFixed(2);
})



