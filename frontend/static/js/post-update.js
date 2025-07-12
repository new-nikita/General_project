function setupPostUpdateHandlers() {
    // === Показать форму редактирования поста ===
    document.querySelectorAll(".edit-post-btn").forEach(button => {
        button.addEventListener("click", function () {
            const postId = this.dataset.postId;

            // 1. Скрываем все формы редактирования
            document.querySelectorAll(".post-edit-form").forEach(form => {
                form.style.display = "none";
            });

            // 2. Показываем все кнопки "Редактировать"
            document.querySelectorAll(".edit-post-btn").forEach(btn => {
                btn.style.display = "inline-block";
            });

            // 3. Скрываем кнопку "Редактировать" для текущего поста
            this.style.display = "none";

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

                // Прокручиваем к форме
                editForm.scrollIntoView({behavior: "smooth", block: "center"});
            }
        });
    });

    // === Отмена редактирования ===
    document.addEventListener("click", function (e) {
        const cancelBtn = e.target.closest(".cancel-edit-btn");
        if (!cancelBtn) return;

        const postId = cancelBtn.dataset.postId;
        const postItem = document.getElementById(`post-${postId}`);
        const editForm = document.getElementById(`edit-form-${postId}`);
        const postContentEl = postItem.querySelector(".post-content");
        const editBtn = postItem.querySelector(".edit-post-btn");

        // Скрываем форму редактирования
        if (editForm) {
            editForm.style.display = "none";
        }

        // Восстанавливаем контент поста
        if (postContentEl) {
            postContentEl.style.display = "block";
        }

        // Показываем кнопку "Редактировать"
        if (editBtn) {
            editBtn.style.display = "inline-block";
        }
    });

    // === Отправка формы обновления ===
    document.addEventListener("submit", async function (e) {
        if (!e.target.classList.contains("edit-post-form")) return;
        e.preventDefault();

        const form = e.target;
        const postId = form.dataset.postId;
        const formData = new FormData(form);

        try {
            const response = await fetch(`/posts/update/${postId}`, {
                method: "PATCH",
                body: formData,
            });

            if (!response.ok) throw new Error("Ошибка при обновлении");

            const result = await response.json();
            const postItem = document.getElementById(`post-${postId}`);

            // === 1. Обновляем текстовое содержимое ===
            let postContentEl = postItem.querySelector(".post-content");

            if (result.post.content && result.post.content.trim()) {
                if (!postContentEl) {
                    // Создаем новый .post-content
                    postContentEl = document.createElement("div");
                    postContentEl.className = "post-content";
                    postContentEl.textContent = result.post.content;

                    // Вставляем после .post-header или перед .post-date
                    const header = postItem.querySelector(".post-header");
                    const dateEl = postItem.querySelector(".post-date");

                    if (dateEl) {
                        dateEl.insertAdjacentElement("beforebegin", postContentEl);
                    } else if (header) {
                        header.insertAdjacentElement("afterend", postContentEl);
                    } else {
                        postItem.appendChild(postContentEl);
                    }
                } else {
                    postContentEl.textContent = result.post.content;
                }
            } else if (postContentEl) {
                postContentEl.remove();
            }

            // === 2. Обновляем изображение ===
            const imageContainer = postItem.querySelector(".post-image-container");
            if (result.post.image) {
                if (!imageContainer) {
                    const imgHTML = `
                        <div class="post-image-container">
                            <img src="${result.post.image}" alt="Пост" class="post-image">
                        </div>`;
                    // Вставляем после .post-header или после контента
                    const header = postItem.querySelector(".post-header");
                    const content = postItem.querySelector(".post-content");

                    if (content) {
                        content.insertAdjacentHTML("afterend", imgHTML);
                    } else if (header) {
                        header.insertAdjacentHTML("afterend", imgHTML);
                    } else {
                        postItem.insertAdjacentHTML("afterbegin", imgHTML);
                    }
                } else {
                    imageContainer.querySelector("img").src = result.post.image;
                }
            } else if (imageContainer) {
                imageContainer.remove();
            }

            // === 3. Скрываем форму и показываем кнопку "Редактировать" и контент ===
            const editForm = document.getElementById(`edit-form-${postId}`);
            const editBtn = postItem.querySelector(".edit-post-btn");

            if (editForm) {
                editForm.style.display = "none";
            }
            if (postContentEl) {
                postContentEl.style.display = "block";
            }
            if (editBtn) {
                editBtn.style.display = "inline-block";
            }

            showToast("Пост успешно обновлён", true);
        } catch (error) {
            console.error("Ошибка:", error);
            showToast("Не удалось обновить пост", false);
        }
    });

    // === Удаление текущего изображения из формы ===
    document.addEventListener("click", async function (e) {
        const removeBtn = e.target.closest(".remove-current-image-btn");
        if (!removeBtn) return;

        const postId = removeBtn.dataset.postId;
        const currentImageWrapper = removeBtn.closest(".current-image");
        const postItem = document.getElementById(`post-${postId}`);
        const imageContainer = postItem.querySelector(".post-image-container");

        // 🔒 Сохраняем оригинальные данные
        const originalImageHTML = currentImageWrapper.innerHTML;
        const postContentInput = document.querySelector(`#edit-form-${postId} textarea[name="content"]`);
        const originalContent = postContentInput ? postContentInput.value : "";

        // 💡 Очищаем поле content, если там было "None"
        if (postContentInput && postContentInput.value === "None") {
            postContentInput.value = "";
        }

        // 🖼️ Убираем изображение с анимацией
        if (currentImageWrapper) {
            currentImageWrapper.innerHTML = "<div class='loading'>Загрузка...</div>";
        }

        try {
            const response = await fetch(`/posts/remove-image/${postId}`, {
                method: "POST",
            });

            if (!response.ok) throw new Error("Ошибка при удалении изображения");

            const data = await response.json();

            if (data.success) {
                showToast(data.message || "Изображение удалено", true);

                // Успешное удаление — удаляем блок изображения
                if (imageContainer) {
                    imageContainer.classList.add("fade-out");
                    setTimeout(() => imageContainer.remove(), 300);
                }
            } else {
                showToast(data.message, false);

                // ❌ Откатываем изменения: восстанавливаем изображение и значение поля
                if (currentImageWrapper) {
                    currentImageWrapper.innerHTML = originalImageHTML;
                }

                if (postContentInput && postContentInput.value === "") {
                    postContentInput.value = originalContent;
                }
            }
        } catch (error) {
            console.error("Ошибка:", error);
            showToast("Не удалось удалить изображение", false);

            // ❌ При ошибке восстанавливаем изображение и значение поля
            if (currentImageWrapper) {
                currentImageWrapper.innerHTML = originalImageHTML;
            }

            if (postContentInput && postContentInput.value === "") {
                postContentInput.value = originalContent;
            }
        }
    });

}
