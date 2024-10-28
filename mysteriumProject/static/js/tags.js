document.addEventListener('DOMContentLoaded', function () {
    const tagInput = document.querySelector('input[name="tags"]');
    const tagsContainer = document.createElement('div');
    tagsContainer.classList.add('tags-input');
    tagInput.parentNode.insertBefore(tagsContainer, tagInput);
    
    let tags = [];
    
    tagInput.addEventListener('keypress', function (e) {
        if (e.key === ',') {
            e.preventDefault();
            addTag(tagInput.value.trim());
            tagInput.value = '';
        }
    });

    function addTag(tag) {
        if (tag && !tags.includes(tag)) {
            tags.push(tag);
            const tagElement = document.createElement('span');
            tagElement.classList.add('tag');
            tagElement.innerHTML = `${tag} <button type="button">&times;</button>`;
            
            tagElement.querySelector('button').addEventListener('click', function () {
                tags = tags.filter(t => t !== tag);
                tagElement.remove();
                tagInput.value = tags.join(', ');
            });
            
            tagsContainer.appendChild(tagElement);
            tagInput.value = tags.join(', ');
        }
    }
});
