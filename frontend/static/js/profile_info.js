document.addEventListener("DOMContentLoaded", function () {
    const profileBtn = document.getElementById("profile-info-btn");
    const modal = document.getElementById("profile-modal");
    const overlay = document.getElementById("modal-overlay");
    const closeModal = document.querySelector("#profile-modal .close-modal");

    // Открытие модального окна
    profileBtn.addEventListener("click", function () {
        modal.style.display = "block";
        overlay.style.display = "block";
        document.body.style.overflow = "hidden"; // Блокировка прокрутки
    });

    // Закрытие по клику на крестик
    closeModal.addEventListener("click", function () {
        modal.style.display = "none";
        overlay.style.display = "none";
        document.body.style.overflow = "auto";
    });

    // Закрытие по клику на затемнённый фон
    overlay.addEventListener("click", function () {
        modal.style.display = "none";
        overlay.style.display = "none";
        document.body.style.overflow = "auto";
    });

    // Закрытие по нажатию Escape
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && modal.style.display === "block") {
            modal.style.display = "none";
            overlay.style.display = "none";
            document.body.style.overflow = "auto";
        }
    });
});