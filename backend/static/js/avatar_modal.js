document.addEventListener("DOMContentLoaded", function () {
    const avatar = document.querySelector(".user-avatar");
    const modal = document.getElementById("avatar-modal");
    const fullscreenView = document.getElementById("fullscreen-view");
    const isOwner = modal !== null;

    function restoreScroll() {
        document.body.style.overflow = "auto";
    }

    // ===== Клик по аватару =====
    avatar?.addEventListener("click", function (e) {
        e.stopPropagation();

        if (isOwner) {
            modal.style.display = "block";
            document.body.style.overflow = "hidden";
        } else {
            fullscreenView.style.display = "block";
            document.body.style.overflow = "hidden";
            document.querySelector(".fullscreen-avatar").src = this.src;
        }
    });

    // ===== Фуллскрин =====
    document.querySelector(".close-fullscreen")?.addEventListener("click", closeFullscreen);
    fullscreenView?.addEventListener("click", function (e) {
        if (e.target === this || e.target.classList.contains("fullscreen-avatar")) {
            closeFullscreen();
        }
    });
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && fullscreenView.style.display === "block") {
            closeFullscreen();
        }
    });

    function closeFullscreen() {
        fullscreenView.style.display = "none";
        restoreScroll();
    }

    // ===== Модальное окно управления аватаром =====
    if (isOwner) {
        const modal = document.getElementById("avatar-modal");
        const closeModalBtn = modal.querySelector(".close-modal");
        const viewFullscreenBtn = document.getElementById("view-fullscreen");
        const changeAvatarBtn = document.getElementById("change-avatar");
        const removeAvatarBtn = document.getElementById("remove-avatar");
        const avatarUploadModal = document.getElementById("avatar-upload-modal");
        const cancelUploadBtn = document.getElementById("cancel-upload");

        closeModalBtn.addEventListener("click", function () {
            modal.style.display = "none";
        });

        window.addEventListener("click", function (e) {
            if (e.target === modal) {
                modal.style.display = "none";
                restoreScroll();
            }
        });

        viewFullscreenBtn?.addEventListener("click", function () {
            modal.style.display = "none";
            fullscreenView.style.display = "block";
            document.body.style.overflow = "hidden";
            document.querySelector(".fullscreen-avatar").src = avatar.src;
        });

        // ===== Обработчик для кнопки "Загрузить новый" =====
        changeAvatarBtn?.addEventListener("click", function () {
            modal.style.display = "none"; // Скрываем основное модальное окно
            avatarUploadModal.style.display = "block"; // Показываем модальное окно загрузки
        });

        // Закрытие модального окна загрузки
        document.querySelector("#avatar-upload-modal .close-modal")?.addEventListener("click", function () {
            avatarUploadModal.style.display = "none";
            restoreScroll();
        });

        cancelUploadBtn?.addEventListener("click", function () {
            avatarUploadModal.style.display = "none";
            document.getElementById("avatar").value = "";
            document.getElementById("file-name").textContent = "Файл не выбран";
            document.getElementById("preview-avatar").style.display = "none";
            document.getElementById("upload-btn").disabled = true;
        });

        // ===== Предварительный просмотр и загрузка аватара =====
        const avatarInput = document.getElementById("avatar");
        const previewAvatar = document.getElementById("preview-avatar");
        const fileNameDisplay = document.getElementById("file-name");
        const avatarForm = document.getElementById("avatar-form");
        const uploadBtn = document.getElementById("upload-btn");

        // Предварительный просмотр
        avatarInput?.addEventListener("change", function (event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    previewAvatar.src = e.target.result;
                    previewAvatar.style.display = "block";
                };
                reader.readAsDataURL(file);
                fileNameDisplay.textContent = file.name;
            } else {
                fileNameDisplay.textContent = "Файл не выбран";
                previewAvatar.style.display = "none";
            }
        });

        // Активация кнопки после выбора файла
        avatarInput?.addEventListener("change", function () {
            uploadBtn.disabled = !this.files.length;
        });

        // Обработка формы
        avatarForm?.addEventListener("submit", async function (e) {
            e.preventDefault();

            const formData = new FormData(this);
            const originalBtnText = uploadBtn.innerHTML;

            uploadBtn.disabled = true;
            uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Загрузка...';

            try {
                const response = await fetch("/profile/avatar", {
                    method: "POST",
                    body: formData,
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    showToast(errorData.detail || "Ошибка при загрузке аватара", false);
                    return;
                }

                const result = await response.json();

                document.querySelectorAll(".user-avatar, .modal-avatar, .fullscreen-avatar, .post-author-avatar").forEach(
                    (img) => {
                        img.src = result.avatar_url;
                    }
                );

                // Скрываем модальное окно загрузки
                avatarUploadModal.style.display = "none";

                // Сбрасываем форму
                avatarForm.reset();
                previewAvatar.style.display = "none";
                fileNameDisplay.textContent = "Файл не выбран";
                uploadBtn.disabled = true;
                uploadBtn.innerHTML = originalBtnText;

                restoreScroll();
                showToast("Аватар успешно обновлён");

            } catch (error) {
                console.error("Ошибка:", error);
                showToast("Не удалось загрузить аватар", false);
                uploadBtn.disabled = false;
                uploadBtn.innerHTML = originalBtnText;
            }
        });

        // Удаление аватара
        removeAvatarBtn?.addEventListener("click", async function () {
            if (!confirm("Вы уверены, что хотите удалить аватар?")) return;

            try {
                const response = await fetch("/profile/avatar/remove", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    showToast(errorData.detail || "Ошибка при удалении аватара", false);
                    return;
                }

                const result = await response.json();

                // Обновляем аватар везде
                document.querySelectorAll(".user-avatar, .modal-avatar, .fullscreen-avatar, .post-author-avatar").forEach(
                    (img) => {
                        img.src = result.new_avatar;
                    }
                );

                // Скрываем кнопку удаления
                if (result.new_avatar.includes("default_avatar")) {
                    removeAvatarBtn.style.display = "none";
                }

                modal.style.display = "none";
                restoreScroll();
                showToast("Аватар успешно удален");

            } catch (error) {
                console.error("Ошибка:", error);
                showToast("Не удалось удалить аватар", false);
            }
        });
    }
});