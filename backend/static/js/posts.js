document.addEventListener("DOMContentLoaded", function () {
    const toggleButton = document.getElementById("toggle-post-form");
    const formContainer = document.getElementById("post-form-container");
    let isFormVisible = false;

    toggleButton.addEventListener("click", function () {
        if (!isFormVisible) {
            formContainer.style.display = "block";
            setTimeout(() => {
                formContainer.classList.add("show");
            }, 10);
            toggleButton.innerHTML = 'Свернуть';
            isFormVisible = true;
        } else {
            formContainer.classList.remove("show");
            setTimeout(() => {
                formContainer.style.display = "none";
            }, 10);
            toggleButton.innerHTML = '<i class="fas fa-plus me-2"></i>Создать новый пост';
            isFormVisible = false;
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("post-form");
    const postList = document.getElementById("post-list");

    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        const formData = new FormData(form);

        try {
            const response = await fetch("/posts/create", {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();
                form.reset();

                const newPost = `
                        <div class="post-item">
                            <div class="post-header">
                                <img src="${result.post.author.profile.avatar}" alt="Автор" class="post-author-avatar">
                                <div>
                                    <span class="post-author">${result.post.author.profile.full_name}</span>
                                </div>
                            </div>
                            <div class="post-content">${result.post.content}</div>
                            ${result.post.image ? `
                                <div class="post-image-container">
                                    <img src="${result.post.image}" alt="Пост" class="post-image">
                                </div>
                            ` : ""}
                            <div class="post-actions">
                                <div class="post-action">
                                    <i class="far fa-heart"></i>
                                    <span>Нравится</span>
                                </div>
                                <div class="post-action">
                                    <i class="far fa-comment"></i>
                                    <span>Комментировать</span>
                                </div>
                                <div class="post-action">
                                    <i class="far fa-trash-alt"></i>
                                    <span>Удалить</span>
                                </div>
                            </div>
                            <div class="post-date">
                                ${result.post.created_at}
                            </div>
                        </div>
                    `;
                postList.insertAdjacentHTML("afterbegin", newPost);
            } else {
                alert("Произошла ошибка при создании поста.");
            }
        } catch (error) {
            console.error("Ошибка:", error);
            alert("Не удалось создать пост.");
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const postList = document.getElementById("post-list");

    // Делегирование событий для кнопок удаления
    postList.addEventListener("click", async function (event) {
        // Проверяем, что клик был по кнопке удаления
        if (event.target.closest(".delete-post-btn")) {
            const button = event.target.closest(".delete-post-btn");
            const postId = button.getAttribute("data-post-id"); // Получаем ID поста
            const postElement = document.getElementById(`post-${postId}`); // Находим элемент поста

            try {
                // Отправляем запрос на удаление
                const response = await fetch(`/posts/delete/${postId}`, {
                    method: "POST",
                });

                if (response.ok) {
                    // Удаляем пост из DOM
                    postElement.remove();
                } else {
                    const errorData = await response.json();
                    alert(errorData.detail || "Произошла ошибка при удалении поста");
                }
            } catch (error) {
                console.error("Ошибка:", error);
                alert("Не удалось удалить пост. Попробуйте позже.");
            }
        }
    });
});