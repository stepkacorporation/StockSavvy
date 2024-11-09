const toggleTheme = () => {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const newTheme = currentTheme === "dim" ? "light" : "dim";
    document.documentElement.setAttribute("data-theme", newTheme);
    localStorage.setItem("theme", newTheme);

    const themeText = document.getElementById("themeText");
    themeText.textContent = newTheme === "dim" ? "День" : "Ночь";
}

document.addEventListener("DOMContentLoaded", () => {
    const savedTheme = localStorage.getItem("theme") || "dim";
    document.documentElement.setAttribute("data-theme", savedTheme);

    const themeText = document.getElementById("themeText");
    themeText.textContent = savedTheme === "dim" ? "День" : "Ночь";
});
