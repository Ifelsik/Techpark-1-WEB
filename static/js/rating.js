function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Forms a request
 * @param type 'question' or 'answer'
 * @param id number
 * @param activity 'like' or 'dislike'
 * @returns {Request}
 */
function form_request(type, id, activity) {
    return new Request('async_like',
    {
            method: 'post',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                type: type,
                id: id,
                activity: activity,
            }),
        }
    )
}

const init = () => {
    const elements = document.querySelectorAll('.card, .question')

    for (const element of elements) {
        const likeButton = element.querySelector('.like')
        const dislikeButton = element.querySelector('.dislike')
        const likeCounter = element.querySelector('.like-counter')

        const id = element.dataset.id
        const objectType = element.dataset.type


        likeButton.addEventListener('click', () => {
            const request = form_request(objectType, id, 'like')  // hardcode
            fetch(request)
                .then((response) => response.json())
                .then((data) => likeCounter.innerHTML = data.like_count)
                .catch(error => console.error('Ошибка:', error))
        })
        dislikeButton.addEventListener('click', () => {
            const request = form_request(objectType, id, 'dislike')
            fetch(request)
                .then((response) => response.json())
                .then((data) => likeCounter.innerHTML = data.like_count)
                .catch(error => console.error('Ошибка:', error))
        })
    }
}

// Script executes after document loading
document.addEventListener('DOMContentLoaded', () => {init()})

