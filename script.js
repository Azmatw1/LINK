document.getElementById("bookbtn").addEventListener("click",function()
{
    alert("Slot booked!");
    window.location.href="token.html";

});
let token = 12;
document.getElementById("tokenNumber").textContent = "#" +token;