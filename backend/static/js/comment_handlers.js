document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('.comment-icon').forEach(icon => {
        icon.addEventListener('click', async function () {
            const postId = this.getAttribute('data-post-id');
            const container = document.querySelector(`.comments-section[data-post-id="${postId}"]`);

            // Если комментарии уже загружены — просто переключаем видимость
            if (container.innerHTML.trim() !== '') {
                container.style.display = container.style.display === 'none' ? 'block' : 'none';
                return;
            }

            try {
                const response = await fetch(`/posts/${postId}/comments?offset=0&limit=3`);
                const html = await response.text();

                // Вставляем HTML
                container.innerHTML = html;

                // Показываем блок
                container.style.display = 'block';

                // Подписываем событие на кнопку "Показать ещё"
                setupLoadMoreHandler(container);
            } catch (error) {
                console.error('Ошибка при загрузке комментариев:', error);
            }
        });
    });

    function setupLoadMoreHandler(container) {
        const button = container.querySelector('.load-more-comments');
        if (!button) return;

        button.addEventListener('click', async function () {
            const postId = this.getAttribute('data-post-id');
            const offset = parseInt(this.getAttribute('data-offset'));
            const limit = parseInt(this.getAttribute('data-limit'));

            try {
                const response = await fetch(`/posts/${postId}/comments?offset=${offset}&limit=${limit}`);
                const html = await response.text();

                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');

                // Извлекаем только новые комментарии (все .comment-item и .separator)
                const newCommentsList = doc.querySelector('.comments-list');
                const newCommentItems = newCommentsList.querySelectorAll('.comment-item, .separator');

                // Удаляем старую кнопку "Показать ещё"
                this.remove();

                // Добавляем новые комментарии к уже существующим
                const commentsList = container.querySelector('.comments-list');
                newCommentItems.forEach(item => commentsList.appendChild(item));

                // Проверяем наличие новой кнопки в ответе
                const newLoadMoreButton = newCommentsList.querySelector('.load-more-comments');
                if (newLoadMoreButton) {
                    commentsList.appendChild(newLoadMoreButton);
                    setupLoadMoreHandler(container);
                }
            } catch (error) {
                console.error('Ошибка при подгрузке комментариев:', error);
            }
        });
    }

});