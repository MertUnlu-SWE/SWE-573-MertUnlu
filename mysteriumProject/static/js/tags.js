document.addEventListener('DOMContentLoaded', function () {
    const searchTagBtn = document.getElementById('searchTagBtn');
    const tagInput = document.getElementById('tags');
    const tagsContainer = document.getElementById('added-tags');
    const searchResultsContainer = document.getElementById('search-results');
    let tags = new Set();

    // Tag Arama
    searchTagBtn.addEventListener('click', function () {
        const query = tagInput.value.trim();
        if (query) {
            fetch(`/fetch_wikidata/?tags=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    searchResultsContainer.innerHTML = ''; // Önceki sonuçları temizle
                    if (data.results && Object.keys(data.results).length > 0) {
                        for (const tag of Object.values(data.results)[0]) {
                            const li = document.createElement('li');
                            li.className = 'list-group-item';
                            li.innerHTML = `<strong>${tag.label} (${tag.qNumber})</strong><br>${tag.description || 'No description available.'}`;
                            li.addEventListener('click', function () {
                                addTag(tag.label, tag.qNumber);
                                $('#tagSearchModal').modal('hide');
                            });
                            searchResultsContainer.appendChild(li);
                        }
                    } else {
                        searchResultsContainer.innerHTML = '<li class="list-group-item">No results found.</li>';
                    }
                })
                .catch(() => {
                    searchResultsContainer.innerHTML = '<li class="list-group-item">Error fetching data. Try again later.</li>';
                });
            $('#tagSearchModal').modal('show'); // Modal'ı göster
        }
    });

    // Tag Ekleme
    function addTag(label, qNumber) {
        const formattedTag = `${label} (${qNumber.startsWith('Q') ? qNumber : 'Q' + qNumber})`;
        if (!tags.has(formattedTag)) {
            tags.add(formattedTag);
            const tagElement = document.createElement('div');
            tagElement.className = 'tag';
            tagElement.innerHTML = `
                ${formattedTag} 
                <button type="button" class="btn btn-sm btn-danger ms-2 remove-tag">&times;</button>
            `;
            tagElement.querySelector('.remove-tag').addEventListener('click', function () {
                tags.delete(formattedTag);
                tagElement.remove();
                updateInputValue();
            });
            tagsContainer.appendChild(tagElement);
            updateInputValue();
        }
    }

    // Tagleri Input Alanına Yaz
    function updateInputValue() {
        tagInput.value = Array.from(tags).join(', ');
    }
});
