document.addEventListener('DOMContentLoaded', function () {
    const tagInput = document.querySelector('input[name="tags"]');
    const tagsContainer = document.createElement('div');
    tagsContainer.classList.add('tags-input');
    tagInput.parentNode.insertBefore(tagsContainer, tagInput);

    let tags = new Set();

    // Initialize existing tags from the input field (if any)
    const initialTags = tagInput.value.split(',').map(tag => tag.trim()).filter(tag => tag !== '');
    initialTags.forEach(tag => {
        if (tag) addTag(tag); // Add to tags container and Set
    });

    // Event listener for Enter or comma key
    tagInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter' || e.key === ',') {
            e.preventDefault();
            processNewTag(tagInput.value.trim());
            tagInput.value = ''; // Clear input field
        }
    });

    // Process a new tag
    function processNewTag(newTag) {
        if (newTag && !isDuplicate(newTag)) {
            fetchWikidataTag(newTag);
        }
    }

    // Check if a tag is already in the Set
    function isDuplicate(tag) {
        return Array.from(tags).some(t => t.toLowerCase() === tag.toLowerCase());
    }

    // Add a tag to the DOM and Set
    function addTag(tag, qNumber = null) {
        const formattedTag = qNumber ? `${tag} (${qNumber})` : tag;
        if (!isDuplicate(formattedTag)) {
            tags.add(formattedTag);

            // Create the tag element
            const tagElement = document.createElement('span');
            tagElement.classList.add('tag');
            tagElement.innerHTML = `${formattedTag} <button type="button">&times;</button>`;

            // Add event listener to remove tag
            tagElement.querySelector('button').addEventListener('click', function () {
                tags.delete(formattedTag);
                tagElement.remove();
                updateInputValue();
            });

            tagsContainer.appendChild(tagElement); // Add to DOM
            updateInputValue();
        }
    }

    // Fetch tag data from Wikidata
    function fetchWikidataTag(tag) {
        console.log(`Fetching Wikidata info for tag: ${tag}`);
        fetch(`/fetch_wikidata/?tags=${encodeURIComponent(tag)}`)
            .then(response => response.json())
            .then(data => {
                if (data && data.results && data.results[tag] && data.results[tag].length > 0) {
                    const firstResult = data.results[tag][0];
                    addTag(firstResult.label, firstResult.qNumber);
                } else {
                    addTag(tag); // Add tag without qNumber
                }
            })
            .catch(() => {
                addTag(tag); // Add tag without qNumber if fetch fails
            });
    }

    // Update the input field value with tags from Set
    function updateInputValue() {
        tagInput.value = Array.from(tags).join(', '); // Join tags from Set
    }
});
