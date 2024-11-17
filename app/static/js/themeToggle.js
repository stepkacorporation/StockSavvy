// Функция для обновления интерфейса на основе текущей темы
const updateUI = (theme) => {
    const themeText = document.getElementById("themeText");
    const dayIcon = document.getElementById("dayIcon");
    const nightIcon = document.getElementById("nightIcon");

    themeText.textContent = theme === "dim" ? "День" : "Ночь";
    if (theme === "dim") {
        dayIcon.classList.add("hidden");
        nightIcon.classList.remove("hidden");
    } else {
        dayIcon.classList.remove("hidden");
        nightIcon.classList.add("hidden");
    }
};

// Функция для переключения темы
const toggleTheme = () => {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const newTheme = currentTheme === "dim" ? "emerald" : "dim";
    document.documentElement.setAttribute("data-theme", newTheme);
    localStorage.setItem("theme", newTheme);
    updateUI(newTheme);
};

// Применяем сохранённую тему сразу при загрузке скрипта, чтобы избежать моргания
const applyThemeImmediately = () => {
    const savedTheme = localStorage.getItem("theme") || "dim";
    document.documentElement.setAttribute("data-theme", savedTheme);
};

// Настраиваем UI после полной загрузки DOM
document.addEventListener("DOMContentLoaded", () => {
    const savedTheme = localStorage.getItem("theme") || "dim";
    updateUI(savedTheme);
});

// Применяем тему немедленно
applyThemeImmediately();
