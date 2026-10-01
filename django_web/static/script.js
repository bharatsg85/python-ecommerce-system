function toggleMenu(){
    const nav = document.getElementById("navMenu");
    if(nav) nav.classList.toggle("open");
}
function confirmCancel(){
    return confirm("Are you sure you want to cancel this order?");
}
setTimeout(() => {
    document.querySelectorAll(".alert").forEach(el => {
        el.style.transition = "opacity .4s";
        el.style.opacity = "0";
        setTimeout(() => el.remove(), 450);
    });
}, 3500);
