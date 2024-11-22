document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.mark-as-solved-btn').forEach(button => {
        button.addEventListener('click', event => {
            const commentId = button.getAttribute('data-comment-id');
            const postId = button.closest('.post-details').getAttribute('data-post-id');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            // Determine the action based on button text
            const isUnsolved = button.textContent.trim() === 'Mark as Unsolved';
            const url = isUnsolved
                ? `/post/${postId}/unmark_as_solved/`
                : `/post/${postId}/mark_as_solved/comment/${commentId}/`;

            console.log(`Constructed URL: ${url}`);

            console.log(`Button Text: ${button.textContent.trim()}`);

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                },
            })
                .then(response => {
                    console.log(`CSRF Token: ${csrfToken}`);
                    if (!response.ok) {
                        throw new Error(`Failed to update post. Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log("Response Data:", data);
                    if (data.post_is_solved) {
                        button.textContent = 'Mark as Unsolved';
                        const badge = button.closest('.comment').querySelector('.badge');
                        if (!badge) {
                            const newBadge = document.createElement('span');
                            newBadge.className = 'badge bg-success me-2';
                            newBadge.textContent = 'Solved';
                            button.parentElement.insertBefore(newBadge, button);
                        }
                        alert(`Post solved with comment: ${data.solved_comment_text}`);
                    } else {
                        button.textContent = 'Mark as Solved';
                        const badge = button.closest('.comment').querySelector('.badge');
                        if (badge) {
                            badge.remove();
                        }
                        alert('Post is no longer marked as solved.');
                    }
                })
                .catch(error => {
                    console.error('An error occurred:', error.message);
                    alert(`An error occurred: ${error.message}`);
                });
        });
    });
});
