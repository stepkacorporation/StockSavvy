document.addEventListener("DOMContentLoaded", function () {
    const favourites = document.querySelectorAll('.add-or-remove-favourite');

    favourites.forEach(favourite => {
        favourite.addEventListener('click', function () {
            const userId = this.getAttribute('data-user-id');
            const stockTicker = this.getAttribute('data-stock-ticker');
            const isFavourite = this.getAttribute('data-favourite-status') === 'true';
            const csrftoken = getCookie('csrftoken');

            const xhr = new XMLHttpRequest();
            xhr.open("POST", "/api/stocks/favourites/");
            xhr.setRequestHeader("Content-Type", "application/json");
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
            xhr.onreadystatechange = () => {
                if (xhr.readyState === 4) {
                    const response = JSON.parse(xhr.responseText);

                    if (xhr.status === 200 || xhr.status === 201) {
                        if (isFavourite) {
                            // Удалить из избранного
                            this.setAttribute('data-favourite-status', 'false');
                            this.title = "Добавить в избранное";
                            this.querySelector('svg path').setAttribute('d', "M2.866 14.85c-.078.444.36.791.746.593l4.39-2.256 4.389 2.256c.386.198.824-.149.746-.592l-.83-4.73 3.522-3.356c.33-.314.16-.888-.282-.95l-4.898-.696L8.465.792a.513.513 0 0 0-.927 0L5.354 5.12l-4.898.696c-.441.062-.612.636-.283.95l3.523 3.356-.83 4.73zm4.905-2.767-3.686 1.894.694-3.957a.56.56 0 0 0-.163-.505L1.71 6.745l4.052-.576a.53.53 0 0 0 .393-.288L8 2.223l1.847 3.658a.53.53 0 0 0 .393.288l4.052.575-2.906 2.77a.56.56 0 0 0-.163.506l.694 3.957-3.686-1.894a.5.5 0 0 0-.461 0z");

                            this.classList.add('hidden');
                            this.classList.add('group-hover:flex');
                        } else {
                            // Добавить в избранное
                            this.setAttribute('data-favourite-status', 'true');
                            this.title = "Удалить из избранного";
                            this.querySelector('svg path').setAttribute('d', "M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z");

                            this.classList.remove('hidden');
                            this.classList.remove('group-hover:flex');
                        }
                    } else {
                        console.log("Ошибка: " + xhr.status);
                    }
                }
            };

            xhr.send(JSON.stringify({ 'user': userId, 'stock': stockTicker }));
        });
    });
});
