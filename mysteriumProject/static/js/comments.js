document.addEventListener('DOMContentLoaded', () => {
    // Retrieve the CSRF token
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Add event listeners for "Mark as Solved" and "Mark as Unsolved" buttons
    document.querySelectorAll('.mark-as-solved-btn').forEach(button => {
        button.addEventListener('click', event => {
            const commentId = button.getAttribute('data-comment-id');
            const postId = button.closest('.post-details').getAttribute('data-post-id');

            // Determine the URL and action
            const isUnsolved = button.textContent.trim() === 'Mark as Unsolved';
            const url = isUnsolved
                ? `/post/${postId}/unmark_as_solved/`
                : `/post/${postId}/mark_as_solved/comment/${commentId}/`;

            // Send the POST request
            fetch(url, {
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
                    if (data.post_is_solved) {
                        button.textContent = 'Mark as Unsolved';
                        alert('Post is now marked as solved.');
                        location.reload(); // Refresh the page
                    } else {
                        button.textContent = 'Mark as Solved';
                        alert('Post is no longer solved.');
                        location.reload(); // Refresh the page
                    }
                })
                .catch(error => {
                    console.error('An error occurred:', error.message);
                    alert(`An error occurred: ${error.message}`);
                });
        });
    });
});
