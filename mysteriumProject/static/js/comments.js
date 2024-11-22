document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.mark-as-solved-btn').forEach(button => {
        button.addEventListener('click', event => {
            const commentId = button.getAttribute('data-comment-id');
            const postId = button.closest('.post-details').getAttribute('data-post-id');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch(`/post/${postId}/mark_as_solved/${commentId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                },
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Failed to update post. Status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    alert(`Post solved with comment: ${data.solved_comment_text}`);
                    window.location.reload();
                })
                .catch(error => {
                    console.error('An error occurred:', error.message);
                    alert(`An error occurred: ${error.message}`);
                });
        });
    });
});
