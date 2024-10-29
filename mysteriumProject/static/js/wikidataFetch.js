$(document).ready(function(){
    $('#search-form').on('submit', function(event){
        event.preventDefault();

        let query = $('#search-input').val().trim();
        if (query !== '') {
            let tags = query.split(',').map(tag => tag.trim());
            console.log('Gönderilen Etiketler:', tags);

            $.ajax({
                url: '/fetch_wikidata/',  // Django URL
                data: { 'tags': JSON.stringify(tags) },
                method: 'GET',
                success: function(data) {
                    console.log('Gelen Yanıt:', data);
                    let results = data.results;
                    $('#search-results').empty();

                    if (results.length > 0) {
                        results.forEach(function(item){
                            $('#search-results').append(`<li><a href="${item[0]}" target="_blank">${item[1]}</a></li>`);
                        });
                    } else {
                        $('#search-results').append('<li>No results found.</li>');
                    }

                    $('#search-results-container').removeClass('hidden');
                },
                error: function(xhr, status, error) {
                    console.log('Hata:', error);
                    $('#search-results').append('<li>Error fetching data. Please try again.</li>');
                    $('#search-results-container').removeClass('hidden');
                }
            });
        }
    });

    $('#close-search-results').on('click', function(){
        $('#search-results-container').addClass('hidden');
    });
});
