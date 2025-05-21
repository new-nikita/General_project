document.addEventListener("DOMContentLoaded", function () {
    // Инициализация обработчиков лайков
    initLikeHandlers();
});

function initLikeHandlers() {
    document.querySelectorAll('.like-container').forEach(container => {
        const button = container.querySelector('.like-button');
        if (!button.dataset.initialized) {
            button.addEventListener('click', likeButtonHandler);
            button.dataset.initialized = 'true'; // Защита от дублирования обработчиков
        }

        const heartIcon = button.querySelector('.fa-heart');
        const counter = button.querySelector('.like-counter');

        // Инициализация начального состояния
        if (button.classList.contains('liked')) {
            heartIcon.classList.add('fas');
            heartIcon.classList.remove('far');
            if (counter) counter.style.display = 'inline';
        }

        button.addEventListener('click', likeButtonHandler);
    });
}

async function likeButtonHandler(e) {
    e.preventDefault();
    const button = e.currentTarget;

    if (!button || button.style.pointerEvents === 'none') return;

    const container = button.closest('.like-container');
    if (!container) return;

    const postId = container.dataset.postId;
    const heartIcon = button.querySelector('.fa-heart');
    if (!heartIcon) return;

    let counter = button.querySelector('.like-counter');
    const wasLiked = button.classList.contains('liked');

    // Получаем текущее значение из счетчика (или 0)
    let likesCount = parseInt(counter?.textContent) || 0;

    // Блокируем кнопку
    button.style.pointerEvents = 'none';

    // Мгновенно обновляем UI
    const isNowLiked = !wasLiked;
    button.classList.toggle('liked', isNowLiked);
    heartIcon.classList.toggle('fas', isNowLiked);
    heartIcon.classList.toggle('far', !isNowLiked);

    animateElement(heartIcon, 'like-animate');

    // Обновляем счётчик локально
    if (!isNowLiked && likesCount > 0) {
        likesCount--;
    } else if (isNowLiked) {
        likesCount++;
    }

    // Показываем/скрываем счётчик
    if (likesCount > 0) {
        if (!counter) {
            counter = createCounter(button, likesCount);
        } else {
            updateCounter(counter, likesCount);
        }
    } else if (counter) {
        removeCounter(counter);
    }

    try {
        const response = await fetch(`/posts/${postId}/like`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            credentials: 'include'
        });

        if (!response.ok) throw new Error('Network error');

        const data = await response.json();
        const serverLikesCount = parseInt(data.likes_count) || 0;

        // Если данные с сервера отличаются от предположения — обновляем
        if (serverLikesCount !== likesCount) {
            if (serverLikesCount > 0) {
                updateCounter(counter, serverLikesCount);
            } else if (counter) {
                removeCounter(counter);
            }
        }

    } catch (error) {
        console.error('Error:', error);

        // Откатываем изменения при ошибке
        button.classList.toggle('liked', wasLiked);
        heartIcon.classList.toggle('fas', wasLiked);
        heartIcon.classList.toggle('far', !wasLiked);

        if (wasLiked && likesCount > 0 && counter) {
            updateCounter(counter, likesCount);
        } else if (!wasLiked && counter) {
            removeCounter(counter);
        }
    } finally {
        setTimeout(() => {
            button.style.pointerEvents = '';
        }, 600);
    }
}

// Вспомогательные функции
function createCounter(button, count) {
    const counter = document.createElement('span');
    counter.className = 'like-counter counter-animate';
    counter.textContent = count;
    button.appendChild(counter);
    animateElement(counter, 'counter-animate');
    return counter;
}

function updateCounter(counter, count) {
    counter.textContent = count;
    counter.style.display = 'inline';
    animateElement(counter, 'counter-animate');
}

function removeCounter(counter) {
    counter.classList.add('animate-up');
    setTimeout(() => counter.remove(), 300);
}

function animateElement(element, animationClass) {
    element.classList.remove(animationClass);
    void element.offsetWidth; // Trigger reflow
    element.classList.add(animationClass);
    setTimeout(() => {
        element.classList.remove(animationClass);
    }, 600);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}