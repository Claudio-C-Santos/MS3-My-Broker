// This changes the color of the "Available Funds" number of the profile page
let funds_el_profile = document.querySelector("#funds_available_profile");
let funds_profile = document.querySelector("#funds_available_profile").innerHTML;

// This element's innerHTML is a string, this line of code removes the comma and turns it into an floater
int_funds_profile = parseFloat(funds_profile.replace(",", ""));

// Changes in the element's classes when the innerHTML is a negative number
if (int_funds_profile < 0) {
    funds_el_profile.removeAttribute("class", "text-gray-800");
    funds_el_profile.setAttribute("class", "negative_profile");
}

// This changes the color of the "Profit/Loss" number of the profile page
let profit_loss_el_profile = document.querySelector("#profit_loss_profile");
let profit_loss_profile = document.querySelector("#profit_loss_profile").innerHTML;

int_profit_loss_profile = parseFloat(profit_loss_profile.replace(",", ""));

if (int_profit_loss_profile < 0) {
    profit_loss_el_profile.removeAttribute("class", "text-gray-800");
    profit_loss_el_profile.setAttribute("class", "negative_profile");
} else if (int_profit_loss_profile > 0) {
    profit_loss_el_profile.removeAttribute("class", "text-gray-800");
    profit_loss_el_profile.setAttribute("class", "positive_profile");
}

