$(document).ready(function () {
    const csrfToken = $('meta[name="csrf-token"]').attr('content');

    // "Mark as Solved" ve "Mark as Unsolved" butonları için event handler
    $('.mark-as-solved-btn').on('click', function () {
        const button = $(this);
        const commentId = button.data('comment-id');
        const postId = button.closest('.post-details').data('post-id');

        // URL'yi belirle
        const isUnsolved = button.text().trim() === 'Mark as Unsolved';
        const url = isUnsolved
            ? `/post/${postId}/unmark_as_solved/?_=${new Date().getTime()}`
            : `/post/${postId}/mark_as_solved/comment/${commentId}/?_=${new Date().getTime()}`;

        // AJAX isteği gönder
        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            },
            success: function (data) {
                if (data.post_is_solved) {
                    button.text('Mark as Unsolved');
                    alert('Post is now marked as solved.');
                } else {
                    button.text('Mark as Solved');
                    alert('Post is no longer solved.');
                }
            },
            error: function (xhr, status, error) {
                console.error('Error:', error);
                alert(`An error occurred: ${xhr.statusText}`);
            },
        });
    });
});
