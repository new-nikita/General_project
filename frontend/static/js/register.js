document.addEventListener("DOMContentLoaded", function () {
    const avatarInput = document.getElementById('avatar');
    const avatarPreview = document.querySelector('.avatar-image');
    const avatarDefault = document.querySelector('.avatar-default');
    const removeBtn = document.getElementById('remove-avatar');
    const uploadContainer = document.querySelector('.avatar-upload-container');

    // Обработчик выбора файла
    avatarInput.addEventListener('change', function () {
        if (this.files && this.files[0]) {
            const file = this.files[0];

            // Проверка типа файла
            const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
            if (!validTypes.includes(file.type)) {
                showToast('Пожалуйста, выберите изображение в формате JPG, PNG или GIF', false);
                return;
            }

            // Проверка размера файла (макс 5MB)
            if (file.size > 5 * 1024 * 1024) {
                showToast('Размер файла не должен превышать 5MB', false);
                return;
            }

            const reader = new FileReader();

            reader.onload = function (e) {
                avatarPreview.src = e.target.result;
                avatarPreview.style.display = 'block';
                avatarDefault.style.display = 'none';
                removeBtn.disabled = false;

                // Добавляем класс при наличии аватара
                uploadContainer.classList.add('has-avatar');
            }

            reader.readAsDataURL(file);
        }
    });

    // Удаление аватара
    removeBtn.addEventListener('click', function () {
        avatarInput.value = '';
        avatarPreview.src = '#';
        avatarPreview.style.display = 'none';
        avatarDefault.style.display = 'block';
        this.disabled = true;
        uploadContainer.classList.remove('has-avatar');
    });

    // Drag and drop функционал
    uploadContainer.addEventListener('dragover', function (e) {
        e.preventDefault();
        this.classList.add('dragover');
    });

    uploadContainer.addEventListener('dragleave', function () {
        this.classList.remove('dragover');
    });

    uploadContainer.addEventListener('drop', function (e) {
        e.preventDefault();
        this.classList.remove('dragover');

        if (e.dataTransfer.files.length) {
            avatarInput.files = e.dataTransfer.files;
            const event = new Event('change');
            avatarInput.dispatchEvent(event);
        }
    });

    // Функция для показа уведомлений
    function showToast(message, isSuccess = true) {
        // Ваша реализация toast-уведомлений
    }
});