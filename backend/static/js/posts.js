document.addEventListener("DOMContentLoaded", function () {
    // Переменные для формы создания поста
    const toggleButton = document.getElementById("toggle-post-form");
    const formContainer = document.getElementById("post-form-container");
    const form = document.getElementById("post-form");
    const postList = document.getElementById("post-list");
    let isFormVisible = false;

    // Переключение видимости формы
    toggleButton?.addEventListener("click", function () {
        isFormVisible = !isFormVisible;
        formContainer.style.display = isFormVisible ? "block" : "none";

        if (isFormVisible) {
            setTimeout(() => {
                formContainer.classList.add("show");
                formContainer.scrollIntoView({behavior: "smooth", block: "center"});
            }, 10);
            toggleButton.innerHTML = '<i class="fas fa-minus me-2"></i>Свернуть';
        } else {
            formContainer.classList.remove("show");
            toggleButton.innerHTML = '<i class="fas fa-plus me-2"></i>Создать новый пост';
        }
    });

    // Обработка отправки формы
    form?.addEventListener("submit", async function (event) {
        event.preventDefault();
        const submitButton = form.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.innerHTML;

        try {
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Создание...';

            const formData = new FormData(form);
            const response = await fetch("/posts/create", {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();
                form.reset();

                // Удаляем блок "Постов пока нет", если он есть
                const noPostsBlock = postList.querySelector(".no-posts");
                if (noPostsBlock) {
                    noPostsBlock.remove();
                }

                // Создаем новый элемент поста
                const newPost = document.createElement("div");
                newPost.className = "post-item";
                newPost.id = `post-${result.post.id}`;
                newPost.innerHTML = `
                <div class="post-header">
                    <img src="${result.post.author.profile.avatar}" alt="Автор" class="post-author-avatar">
                    <span class="post-author">${result.post.author.profile.full_name}</span>
                </div>
                ${result.post.content ? `<div class="post-content">${result.post.content}</div>` : ''}
                ${result.post.image ? `<div class="post-image-container"><img src="${result.post.image}" alt="Пост" class="post-image"></div>` : ''}
                <div class="post-date">${result.post.created_at}</div>
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
                        <button class="delete-post-btn" data-post-id="${result.post.id}"
                                style="background: none; border: none; color: red; cursor: pointer;">
                            Удалить
                        </button>
                    </div>
                </div>
            `;

                // Добавляем новый пост в начало списка
                postList.insertAdjacentElement("afterbegin", newPost);

                // Скрываем форму после успешного создания
                formContainer.style.display = "none";
                formContainer.classList.remove("show");
                toggleButton.innerHTML = '<i class="fas fa-plus me-2"></i>Создать новый пост';
                isFormVisible = false;
            } else {
                const errorData = await response.json();
                showToast(errorData.detail || "Произошла ошибка при создании поста.", false);
            }
        } catch (error) {
            console.error("Ошибка:", error);
            showToast("Не удалось создать пост.", false);
        } finally {
            submitButton.disabled = false;
            submitButton.innerHTML = originalButtonText;
        }
    });

    // Обработка удаления поста (делегирование событий)
    postList?.addEventListener("click", async function (event) {
        const deleteButton = event.target.closest(".delete-post-btn");
        if (!deleteButton) return;

        const postId = deleteButton.getAttribute("data-post-id");
        const postElement = document.getElementById(`post-${postId}`);

        if (!postElement) {
            console.error(`Элемент с id "post-${postId}" не найден.`);
            return;
        }

        try {
            deleteButton.disabled = true;
            deleteButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

            const response = await fetch(`/posts/delete/${postId}`, {
                method: "POST",
            });

            if (response.ok) {
                // Добавляем анимацию удаления
                postElement.classList.add("fade-out");

                // Удаляем элемент из DOM после завершения анимации
                setTimeout(() => {
                    postElement.remove();

                    // Проверяем, остались ли посты в списке
                    const remainingPosts = postList.querySelectorAll(".post-item");
                    if (remainingPosts.length === 0) {
                        // Добавляем блок "Постов пока нет"
                        postList.innerHTML = `
        <div class="no-posts text-center">
            <i class="far fa-newspaper fa-2x mb-3"></i>
            <p>Постов пока нет</p>
            <p>Создайте первый пост, чтобы поделиться новостями</p>
        </div>
    `;
                    }

                }, 50);
            } else {
                const errorData = await response.json();
                showToast(errorData.detail || "Произошла ошибка при удалении поста", false);
            }
        } catch (error) {
            console.error("Ошибка:", error);
            showToast("Не удалось удалить пост. Попробуйте позже.", false);
        } finally {
            deleteButton.disabled = false;
            deleteButton.innerHTML = 'Удалить';
        }
    });
});