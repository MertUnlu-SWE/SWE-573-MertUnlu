$(document).ready(function () {
    $('#search-form').on('submit', function (event) {
        event.preventDefault();

        let query = $('#search-input').val().trim();
        if (query !== '') {
            let tags = query.split(',').map(tag => tag.trim());
            console.log('Gönderilen Etiketler:', tags);

            $.ajax({
                url: '/fetch_wikidata/',
                data: { 'tags': JSON.stringify(tags) },
                method: 'GET',
                success: function (data) {
                    console.log('Gelen Yanıtın Yapısı:', JSON.stringify(data));
            
                    $('#search-results').empty();
                    if (data && data.results) {
                        for (let tag in data.results) {
                            $('#search-results').append(`<li><strong>${tag}</strong></li>`);
                            data.results[tag].forEach(function (item) {
                                $('#search-results').append(
                                    `<li><a href="${item[0]}" target="_blank">${item[1]}</a></li>`
                                );
                            });
                        }
                    } else {
                        $('#search-results').append('<li>No results found.</li>');
                    }
            
                    $('#search-results-container').removeClass('hidden');
                },
                error: function (xhr, status, error) {
                    console.log('Hata:', error);
                    $('#search-results').empty();
                    $('#search-results').append('<li>Error fetching data. Please try again.</li>');
                    $('#search-results-container').removeClass('hidden');
                }
            });
        }
    });

    $('#close-search-results').on('click', function () {
        $('#search-results-container').addClass('hidden');
    });
});
