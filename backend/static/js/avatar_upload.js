document.addEventListener("DOMContentLoaded", function () {
    const avatarImage = document.querySelector(".user-avatar");
    const avatarForm = document.getElementById("avatar-upload-form");
    const avatarInput = document.getElementById("avatar");

    // Показываем форму при нажатии на аватар
    avatarImage.addEventListener("click", function () {
        if (avatarForm.style.display === "none" || avatarForm.style.display === "") {
            avatarForm.style.display = "block";
        } else {
            avatarForm.style.display = "none";
        }
    });

    // Обработка отправки формы аватара
    document.getElementById("avatar-form").addEventListener("submit", async function (event) {
        event.preventDefault();

        const formData = new FormData();
        formData.append("avatar", avatarInput.files[0]);

        try {
            const response = await fetch("/profile/avatar", {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();
                // Обновляем аватар на странице
                avatarImage.src = result.avatar_url;
                avatarForm.style.display = "none"; // Скрываем форму после успешной загрузки
                // alert(result.message); // Показываем сообщение об успехе
            } else {
                const errorData = await response.json();
                alert(errorData.detail || "Произошла ошибка при загрузке аватара.");
            }
        } catch (error) {
            console.error("Ошибка:", error);
            alert("Не удалось загрузить аватар.");
        }
    });
});