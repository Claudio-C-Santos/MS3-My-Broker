// This changes the color of the "Available Funds" number of the profile page
let funds_el_profile = document.querySelector("#funds_available_profile")
let funds_profile = document.querySelector("#funds_available_profile").innerHTML

int_funds_profile = parseFloat(funds_profile.replace(",", ""))

if (int_funds_profile < 0) {
    funds_el_profile.removeAttribute("class", "text-gray-800")
    funds_el_profile.setAttribute("class", "negative_wallet_profile");
}

// This changes the color of the "Available Funds" number of the top nav bar
let funds_el_bar = document.querySelector("#funds_available_bar")
let funds_bar = document.querySelector("#funds_available_bar").innerHTML

int_funds_bar = parseFloat(funds_bar.replace(",", ""))

if (int_funds_bar < 0) {
    funds_el_bar.removeAttribute("class", "text-gray-800")
    funds_el_bar.setAttribute("class", "negative_wallet_bar");
}

// This changes the color of the "Profit/Loss" number of the profile page
let profit_loss_el_profile = document.querySelector("#profit_loss_profile")
let profit_loss_profile = document.querySelector("#profit_loss_profile").innerHTML

int_profit_loss_profile = parseFloat(profit_loss_profile.replace(",", ""))

if (int_profit_loss_profile < 0) {
    profit_loss_el_profile.removeAttribute("class", "text-gray-800")
    profit_loss_el_profile.setAttribute("class", "negative_wallet_profile");
}

// This changes the color of the "Profit/Loss" number of the top nav bar
let profit_loss_el_bar = document.querySelector("#profit_loss_bar")
let profit_lossfunds_bar = document.querySelector("#profit_loss_bar").innerHTML

int_profit_loss_bar = parseFloat(profit_loss_bar.replace(",", ""))

if (int_profit_loss_bar < 0) {
    profit_loss_el_bar.removeAttribute("class", "text-gray-800")
    profit_loss_el_bar.setAttribute("class", "negative_wallet_bar");
}
