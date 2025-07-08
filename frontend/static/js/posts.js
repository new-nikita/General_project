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

                const newPost = document.createElement("div");
                newPost.className = "post-item";
                newPost.id = `post-${result.post.id}`;
                newPost.innerHTML = `
    <div class="post-header">
        <img src="${result.post.author.profile.avatar}" alt="Автор" class="post-author-avatar">
        <div>
            <span class="post-author">${result.post.author.profile.full_name || result.post.author.username}</span>
        </div>
    </div>

    ${result.post.image ? `
        <div class="post-image-container">
            <img src="${result.post.image}" alt="Пост" class="post-image">
        </div>
    ` : ''}

    ${result.post.content ? `
        <div class="post-content">${result.post.content}</div>
    ` : ''}

    <div class="post-actions">
        <div class="like-container" data-post-id="${result.post.id}">
            <button class="like-button">
                <i class="fa-heart far"></i>
                <span class="like-text">Нравится</span>
            </button>
        </div>
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
    <!-- Кнопка редактирования -->
    <button class="edit-post-btn btn btn-sm btn-outline-primary"
            data-post-id="${result.post.id}" style="margin-left: 10px;">
        <i class="fas fa-edit"></i> Редактировать
    </button>
                            <!-- Скрытая форма редактирования -->
    <div class="post-edit-form" id="edit-form-${result.post.id}" style="display: none; margin-top: 15px;">
        <form class="edit-post-form" data-post-id="${result.post.id}" enctype="multipart/form-data">
            <textarea name="content" class="form-control mb-2">${result.post.content || ''}</textarea>

            <div class="current-image mb-2" style="position: relative; display: flex; align-items: center;">
                ${result.post.image ? `
                    <img src="${result.post.image}" alt="Текущее изображение" width="100" height="100" style="object-fit: cover;">
                    <button type="button" class="remove-current-image-btn btn btn-sm btn-danger" data-post-id="${result.post.id}" title="Удалить изображение" style="position: absolute; top: 8px; right: 8px; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; padding: 0; box-shadow: 0 2px 6px rgba(0,0,0,0.2);">
                        <i class="fas fa-trash-alt" style="color: #dc3545;"></i>
                    </button>
                ` : ''}
            </div>
             <input type="file" name="image" class="form-control mb-2" accept="image/*">
            
             <div class="d-flex gap-2">
                <button type="submit" class="btn btn-success btn-sm">Сохранить</button>
                <button type="button" class="btn btn-secondary btn-sm cancel-edit-btn"
                        data-post-id="${result.post.id}">Отмена
                </button>
            </div>
        </form>
    </div>
                            
    <div class="post-date">${new Date().toLocaleString('ru-RU', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                })}</div>
`;

                // Добавляем новый пост в начало списка
                postList.insertAdjacentElement("afterbegin", newPost);
                initLikeHandlers();

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

    postList?.addEventListener("click", function (e) {
        const editBtn = e.target.closest(".edit-post-btn");
        if (!editBtn) return;

        const postId = editBtn.dataset.postId;

        // 1. Скрываем все формы редактирования
        document.querySelectorAll(".post-edit-form").forEach(form => {
            form.style.display = "none";
        });

        // 2. Показываем все кнопки "Редактировать"
        document.querySelectorAll(".edit-post-btn").forEach(btn => {
            btn.style.display = "inline-block";
        });

        // 3. Скрываем кнопку "Редактировать" для текущего поста
        editBtn.style.display = "none";

        const postItem = document.getElementById(`post-${postId}`);
        const editForm = document.getElementById(`edit-form-${postId}`);
        const postContentEl = postItem.querySelector(".post-content");

        // Скрываем текущий контент поста
        if (postContentEl) {
            postContentEl.style.display = "none";
        }

        // Показываем нужную форму редактирования
        if (editForm) {
            editForm.style.display = "block";
            editForm.scrollIntoView({behavior: "smooth", block: "center"});
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