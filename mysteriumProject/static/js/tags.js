document.addEventListener('DOMContentLoaded', function () {
    const searchTagBtn = document.getElementById('searchTagBtn');
    const tagInput = document.querySelector('#tags');
    const tagsContainer = document.getElementById('added-tags');
    const searchResultsContainer = document.getElementById('search-results'); // Eksik tanım eklendi
    const existingTagsContainer = document.getElementById('existing-tags');
    let tags = new Set();

    // Open Modal and Fetch Results
    searchTagBtn.addEventListener('click', function () {
        const tagQuery = tagInput.value.trim();
        if (tagQuery) {
            fetch(`/fetch_wikidata/?tags=${encodeURIComponent(tagQuery)}`)
                .then(response => response.json())
                .then(data => {
                    searchResultsContainer.innerHTML = ''; // Clear old results
                    if (data.results && data.results[tagQuery]) {
                        const tags = data.results[tagQuery];
                        tags.forEach(tag => {
                            const li = document.createElement('li');
                            li.className = 'list-group-item';
                            li.innerHTML = `<strong>${tag.label} (${tag.qNumber})</strong><br>${tag.description || 'No description available.'}`;
                            li.addEventListener('click', function () {
                                addTag(tag.label, tag.qNumber);
                                $('#tagSearchModal').modal('hide'); // Hide modal
                            });
                            searchResultsContainer.appendChild(li);
                        });
                    } else {
                        searchResultsContainer.innerHTML = '<li class="list-group-item">No results found.</li>';
                    }
                })
                .catch(() => {
                    searchResultsContainer.innerHTML = '<li class="list-group-item">Error fetching data. Try again later.</li>';
                });
            $('#tagSearchModal').modal('show'); // Show modal
        }
    });

    // Add Tag to Input
    function addTag(tagLabel, qNumber = null) {
        const formattedTag = qNumber ? `${tagLabel} (${qNumber})` : tagLabel;

        if (!isDuplicate(formattedTag)) {
            tags.add(formattedTag);

            // Yeni Tag için HTML Elementi Oluştur
            const tagElement = document.createElement('div');
            tagElement.classList.add('tag');
            tagElement.innerHTML = `
                ${formattedTag} <button type="button" class="remove-tag">&times;</button>
            `;

            // Silme Butonuna Event Listener Ekle
            tagElement.querySelector('.remove-tag').addEventListener('click', function () {
                tags.delete(formattedTag);
                tagElement.remove();
                updateInputValue();
            });

            // Tag'i Görüntüleme Alanına Ekle
            tagsContainer.appendChild(tagElement);
            updateInputValue();
        }
    }

    // Taglerin Input Alanına Güncellenmesi
    function updateInputValue() {
        tagInput.value = Array.from(tags).join(', ');
    }

    // Duplicate Kontrolü
    function isDuplicate(tag) {
        return Array.from(tags).some(existingTag => existingTag.toLowerCase() === tag.toLowerCase());
    }

    // Mevcut tagleri input alanına ekle
    function updateInput() {
        const tags = Array.from(existingTagsContainer.children).map(tag => tag.querySelector('span').textContent.trim());
        tagInput.value = tags.join(', ');
    }

    existingTagsContainer.addEventListener('click', function (e) {
        if (e.target.classList.contains('remove-tag')) {
            e.target.parentElement.remove();
            updateInput();
        }
    });
});
