document.addEventListener("DOMContentLoaded", function () {
    const avatar = document.querySelector(".user-avatar");
    const modal = document.getElementById("avatar-modal");
    const fullscreenView = document.getElementById("fullscreen-view");
    const closeFullscreen = document.querySelector(".close-fullscreen");
    const isOwner = modal !== null; // Проверяем, есть ли модальное окно (значит это владелец)

    // Функция для восстановления прокрутки страницы
    function restoreScroll() {
        document.body.style.overflow = "auto";
    }

    // Обработчик клика на аватар
    avatar?.addEventListener("click", function (e) {
        e.stopPropagation();

        if (isOwner) {
            // Для владельца - показываем меню
            modal.style.display = "block";
            document.body.style.overflow = "hidden";
        } else {
            // Для других - сразу фуллскрин
            fullscreenView.style.display = "block";
            document.body.style.overflow = "hidden";
            document.querySelector(".fullscreen-avatar").src = this.src;
        }
    });

    // Закрытие фуллскрина
    function closeFullscreenView() {
        fullscreenView.style.display = "none";
        restoreScroll();
    }

    // Кнопка закрытия фуллскрина
    closeFullscreen?.addEventListener("click", closeFullscreenView);

    // Закрытие по клику на затемненную область
    fullscreenView?.addEventListener("click", function (e) {
        if (e.target === this || e.target.classList.contains("fullscreen-avatar")) {
            closeFullscreenView();
        }
    });

    // Закрытие по ESC
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && fullscreenView.style.display === "block") {
            closeFullscreenView();
        }
    });

    // Остальной код для владельца (если isOwner)
    if (isOwner) {
        const closeModal = document.querySelector(".close-modal");
        const viewFullscreenBtn = document.getElementById("view-fullscreen");
        const changeAvatarBtn = document.getElementById("change-avatar");
        const removeAvatarBtn = document.getElementById("remove-avatar");
        const avatarUploadForm = document.getElementById("avatar-upload-form");
        const cancelUploadBtn = document.getElementById("cancel-upload");
        const avatarForm = document.getElementById("avatar-form");

        // Закрытие модального окна
        closeModal?.addEventListener("click", function () {
            modal.style.display = "none";
            restoreScroll();
        });

        // Закрытие модального окна по клику вне его
        window.addEventListener("click", function (e) {
            if (e.target === modal) {
                modal.style.display = "none";
                restoreScroll();
            }
        });

        // Открытие фуллскрина из модального окна
        viewFullscreenBtn?.addEventListener("click", function () {
            modal.style.display = "none";
            fullscreenView.style.display = "block";
            document.body.style.overflow = "hidden";
            document.querySelector(".fullscreen-avatar").src = avatar.src;
        });

        // Открытие формы загрузки аватара
        changeAvatarBtn?.addEventListener("click", function () {
            document.querySelector(".modal-actions").style.display = "none";
            avatarUploadForm.style.display = "block";
        });

        // Отмена загрузки аватара
        cancelUploadBtn?.addEventListener("click", function () {
            document.querySelector(".modal-actions").style.display = "flex";
            avatarUploadForm.style.display = "none";
            document.getElementById("avatar").value = "";
        });

        // Обработчик отправки формы аватара
        avatarForm?.addEventListener("submit", async function (e) {
            e.preventDefault();

            const submitBtn = this.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;

            try {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Загрузка...';

                const formData = new FormData(this);
                const response = await fetch("/profile/avatar", {
                    method: "POST",
                    body: formData,
                });

                if (response.ok) {
                    const result = await response.json();

                    // Обновляем аватар везде
                    document.querySelectorAll(".user-avatar, .modal-avatar, .fullscreen-avatar").forEach(
                        (img) => (img.src = result.avatar_url)
                    );

                    // Сбрасываем форму
                    this.reset();
                    document.querySelector(".modal-actions").style.display = "flex";
                    avatarUploadForm.style.display = "none";
                    modal.style.display = "none";

                    // Восстанавливаем прокрутку
                    restoreScroll();

                    // Показываем уведомление
                    showToast("Аватар успешно обновлен");
                } else {
                    const error = await response.json();
                    showToast(error.detail || "Ошибка при загрузке аватара", false);
                }
            } catch (error) {
                console.error("Ошибка:", error);
                showToast("Не удалось загрузить аватар", false);
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
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

                if (response.ok) {
                    const result = await response.json();

                    // Обновляем аватар на всех экземплярах
                    document.querySelectorAll(".user-avatar, .modal-avatar, .fullscreen-avatar").forEach(
                        (img) => (img.src = result.new_avatar)
                    );

                    // Скрываем кнопку удаления, если установлен дефолтный аватар
                    if (result.new_avatar.includes("default_avatar")) {
                        removeAvatarBtn.style.display = "none";
                    }

                    // Закрываем модальное окно
                    modal.style.display = "none";

                    // Восстанавливаем прокрутку
                    restoreScroll();

                    showToast("Аватар успешно удален");
                } else {
                    const error = await response.json();
                    showToast(error.detail || "Ошибка при удалении аватара", false);
                }
            } catch (error) {
                console.error("Ошибка:", error);
                showToast("Не удалось удалить аватар", false);
            }
        });
    }
});