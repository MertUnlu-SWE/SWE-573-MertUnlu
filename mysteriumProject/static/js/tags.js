document.addEventListener('DOMContentLoaded', function () {
    const tagInput = document.querySelector('input[name="tags"]');
    const tagsContainer = document.createElement('div');
    tagsContainer.classList.add('tags-input');
    tagInput.parentNode.insertBefore(tagsContainer, tagInput);
    
    let tags = [];


    tagInput.addEventListener('keypress', function (e) {
        if (e.key === ',' || e.key === 'Enter') {
            e.preventDefault();
            const newTag = tagInput.value.trim();
            if (newTag) {
                fetchWikidataTag(newTag);
            }
            tagInput.value = '';
        }
    });


    function addTag(tag, qNumber = null) {
        if (tag && !tags.includes(tag)) {
            let formattedTag = tag;
            if (qNumber) {
                if (!qNumber.startsWith('Q')) {
                    formattedTag += ` (Q${qNumber})`;
                } else {
                    formattedTag += ` (${qNumber})`;
                }
            }
    
            tags.push(formattedTag);
            const tagElement = document.createElement('span');
            tagElement.classList.add('tag');
            tagElement.innerHTML = `${formattedTag} <button type="button">&times;</button>`;
    
            tagElement.querySelector('button').addEventListener('click', function () {
                tags = tags.filter(t => t !== formattedTag);
                tagElement.remove();
                tagInput.value = tags.join(', ');
            });
    
            tagsContainer.appendChild(tagElement);
            tagInput.value = tags.join(', ');
        }
    }        


    function fetchWikidataTag(tag) {
        fetch(`/fetch_wikidata/?tag=${encodeURIComponent(tag)}`)
            .then(response => response.json())
            .then(data => {
                console.log("Received Data from Backend:", data);  // Ekleme
                if (data && data.qNumber) {
                    addTag(tag, data.qNumber);
                } else {
                    console.warn("No qNumber found for tag:", tag);  // Uyarı ekleyin
                    addTag(tag);
                }
            })
            .catch(error => console.error('Error fetching Wikidata tag:', error));
    }    
});
