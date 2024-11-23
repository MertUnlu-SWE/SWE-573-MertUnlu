document.addEventListener('DOMContentLoaded', function () {
    const tagInput = document.querySelector('input[name="tags"]');
    const tagsContainer = document.createElement('div');
    tagsContainer.classList.add('tags-input');
    tagInput.parentNode.insertBefore(tagsContainer, tagInput);

    let tags = [];


    tagInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
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
                formattedTag += ` (${qNumber})`; // Assume qNumber is already formatted correctly
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
        console.log(`Fetching Wikidata info for tag: ${tag}`);
        fetch(`/fetch_wikidata/?tags=${encodeURIComponent(tag)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Failed to fetch tag info. Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Wikidata response data:", data);
                if (data && data.results && data.results[tag] && data.results[tag].length > 0) {
                    const firstResult = data.results[tag][0]; // Use the first result by default
                    console.log(`Fetched qNumber for tag "${tag}":`, firstResult.qNumber);
                    addTag(firstResult.label, firstResult.qNumber);
                } else {
                    console.warn("No qNumber found for tag:", tag);
                    addTag(tag); // Add tag without qNumber if no results are found
                }
            })
            .catch(error => {
                console.error("Error fetching Wikidata tag:", error);
                alert(`Error fetching Wikidata tag: ${error.message}`);
                addTag(tag); // Add tag without qNumber in case of error
            });
    }    
    
});
