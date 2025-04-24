window.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("button_js");
    const div_cache = document.getElementById("cache");

    btn.addEventListener("click", function () {
        if (div_cache.style.display === "block") {
            div_cache.style.display = "none";
            console.log("Cache div hidden");
        } else {
            div_cache.style.display = "block";
            console.log("Cache div shown");
        }
    });
});