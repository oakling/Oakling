var akorn = {
    append_articles: function(data) {
        // Add in one go as fragment
        akorn.articles_container.append(data);
    },
    init: function() {
        // Get the place to stick articles
        akorn.articles_container = $('#latest_articles');

        // Get initial articles
        $.get('/api/latest/10', {}, akorn.append_articles, 'html');

        // TODO Search input should be hidden before this point
        // Activate the search box
        $('#search').tagsInput({
            autocomplete_url:'/api/journals',
            autocomplete:{selectFirst:true,width:'100px',autoFill:true},
            height: '15px',
            width: '800px',
            defaultText: 'Search',
        });
    },
};

$(document).ready(akorn.init);
