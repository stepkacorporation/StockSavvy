const toastClassMap = {
    'error': 'bg-danger',
    'info': 'bg-secondary',
};

const showToast = (message, type) => {
    const toastContainer = document.getElementById('toast-container');

    const toastClass = type in toastClassMap ? toastClassMap[type] : toastClassMap['info'];

    const toastHTML = `
            <div class="toast align-items-center text-white ${toastClass}" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Закрыть"></button>
                </div>
            </div>
    `;

    const toastElement = document.createElement('div');
    toastElement.innerHTML = toastHTML;
    toastContainer.appendChild(toastElement);

    const toast = new bootstrap.Toast(toastElement.querySelector('.toast'));

    toast.show();

    toastElement.querySelector('.btn-close').addEventListener('click', () => {
        toastElement.remove();
    });
};