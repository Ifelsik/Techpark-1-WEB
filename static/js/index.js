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
 * @param handler name of controller in 'urls.py'
 * @param type 'question' or 'answer'
 * @param id number
 * @param activity 'like' or 'dislike'
 * @returns {Request}
 */
function form_request(handler, type, id, activity) {
    return new Request(handler,
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
        const likeButton = element.querySelector('.like, .like-active')
        const dislikeButton = element.querySelector('.dislike, .dislike-active')
        const likeCounter = element.querySelector('.like-counter')
        const checkbox = element.querySelector('.form-check-input')

        const id = Number(element.dataset.id)
        const objectType = element.dataset.type

        let isLikeButtonPushed = likeButton.classList.contains('like-active')
        let isDislikeButtonPushed = dislikeButton.classList.contains('dislike-active')

        likeButton.addEventListener('click', () => {
            const request = form_request('async_like', objectType, id, 'like')  // hardcode
            fetch(request)
                .then((response) => response.json())
                .then((data) => {
                        likeCounter.innerHTML = data.like_count
                        if (isDislikeButtonPushed) {
                            dislikeButton.classList.remove("dislike-active")
                            dislikeButton.classList.add("dislike")
                            isDislikeButtonPushed = false
                        }
                        likeButton.classList.toggle("like")
                        likeButton.classList.toggle("like-active")
                        isLikeButtonPushed = true
                    }
                )
                .catch(error => console.error('Ошибка:', error))
        })
        dislikeButton.addEventListener('click', () => {
            const request = form_request('async_like', objectType, id, 'dislike')
            fetch(request)
                .then((response) => response.json())
                .then((data) => {
                        likeCounter.innerHTML = data.like_count
                        if (isLikeButtonPushed) {
                            likeButton.classList.remove("like-active")
                            likeButton.classList.add("like")
                            isLikeButtonPushed = false
                        }
                        dislikeButton.classList.toggle("dislike")
                        dislikeButton.classList.toggle("dislike-active")
                        isDislikeButtonPushed = true
                    }
                )
                .catch(error => console.error('Ошибка:', error))
        })

        if (checkbox && !checkbox.disabled) {
            checkbox.addEventListener('change', () =>
                {
                    if (checkbox.checked) {
                        const request = form_request('',objectType, id, 'checked')
                        fetch(request)
                    } else {
                        const request = form_request(objectType, id, 'unchecked')
                        fetch(request)
                    }
                }
            )
        }
    }
}

// Script executes after document loading
document.addEventListener('DOMContentLoaded', () => {init()})

