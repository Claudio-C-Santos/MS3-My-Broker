let funds_el_profile = document.querySelector("#funds_available_profile")
let funds_profile = document.querySelector("#funds_available_profile").innerHTML

int_funds_profile = parseFloat(funds_profile.replace(",", ""))

if (int_funds_profile < 0) {
    funds_el_profile.removeAttribute("class", "text-gray-800")
    funds_el_profile.setAttribute("class", "negative_wallet_profile");
}


let funds_el_bar = document.querySelector("#funds_available_bar")
let funds_bar = document.querySelector("#funds_available_bar").innerHTML

int_funds_bar = parseFloat(funds_bar.replace(",", ""))

if (int_funds_bar < 0) {
    funds_el_bar.removeAttribute("class", "text-gray-800")
    funds_el_bar.setAttribute("class", "negative_wallet_bar");
}
