document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.mark-as-solved-btn').forEach(button => {
        button.addEventListener('click', event => {
            const commentId = button.getAttribute('data-comment-id');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch(`/comment/${commentId}/mark_as_solved/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json',
                },
            })
                .then(response => response.json())
                .then(data => {
                    if (data.is_solved) {
                        button.textContent = 'Mark as Unsolved';
                        button.previousElementSibling?.classList.add('badge', 'bg-success');
                        button.previousElementSibling.textContent = 'Solved';
                    } else {
                        button.textContent = 'Mark as Solved';
                        button.previousElementSibling?.classList.remove('badge', 'bg-success');
                        button.previousElementSibling.textContent = '';
                    }
                })
                .catch(error => {
                    alert('An error occurred: ' + error.message);
                });
        });
    });
});
