document.addEventListener("DOMContentLoaded", function () {
    const stars = document.querySelectorAll('.add-or-remove-favourite');
    stars.forEach(star => {
        star.addEventListener('click', function () {
            const userId = this.getAttribute('data-user-id');
            const stockTicker = this.getAttribute('data-stock-ticker');
            const starSrc = this.getAttribute('data-star-src');
            const starFillSrc = this.getAttribute('data-star-fill-src');
            const hideOnDelete = this.getAttribute('data-hide-on-delete');

            const csrftoken = getCookie('csrftoken');

            const xhr = new XMLHttpRequest();
            xhr.open("POST", "/api/stocks/favourites/");
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
            xhr.onreadystatechange = () => {
                if (xhr.readyState === 4) {
                    if (xhr.status === 200) {
                        const response = JSON.parse(xhr.responseText);

                        if (hideOnDelete && hideOnDelete.toLowerCase() === "true") {
                            const parentContainer = this.closest('.stock-item-container');
                            parentContainer.remove();
                            checkFavoritesList();
                        } else {
                            star.src = starSrc;
                            star.title = "Add to Favorites";
                        }

                        showToast(response.message, 'info');
                    } else if (xhr.status === 201) {
                        const response = JSON.parse(xhr.responseText);

                        star.src = starFillSrc;
                        star.title = "In Favourites";

                        showToast(response.message, 'info');
                    } else {
                        showToast("Error: " + xhr.status, 'error');
                    }
                }
            };

            xhr.send(JSON.stringify({ 'user': userId, 'stock': stockTicker }));
        });
    });
});

const checkFavoritesList = () => {
    const listGroup = document.querySelector('.list-group');
    const emptyFavouritesText = document.querySelector('.empty-favorites-text');
    const headerContainer = document.querySelector('.header-container');

    if (listGroup && emptyFavouritesText) {
        const items = listGroup.querySelectorAll('.stock-item-container');
        if (items.length === 0) {
            headerContainer.remove();
            emptyFavouritesText.style.display = 'block';
        }
    }
};