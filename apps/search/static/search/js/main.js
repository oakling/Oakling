var akorn = {
    make_article_item: function(doc) {
        // TODO Use a template on the server
        var abstract = '';
        // Parse the date
        var published = new Date(doc.date_published*1000);

        // TODO Make abstract shortening not stupid
        if(doc.abstract !== undefined) {
            abstract = ['<p class="abstract">',doc.abstract.substr(0,300),'...</p>'].join('');
        }
        return ['<li><h3><a href="',doc.ids.url,'">',doc['title'],
        '</a> [<a href="doc/',doc._id,'">akorn.org</a>]</h3><p><span class="authors">',
        doc.author_names.slice(0,3).join(', '),
        '</span> - <time datetime="',
        published.toISOString(),
        '" class="published">',
        published,
        '</time> in <span class="journal"><a href="#">',
        doc.citation.journal,
        '</a></span></p>',
        abstract,
        '</li>'].join('');
    },
    refresh_articles: function(data) {
        var article_len = data.length;
        var articles = $('#latest_articles');
        var doc, i;
        var fragment = [];

        // Process each article
        for(i=0; i < article_len; i += 1) {
            doc = data[i];
            fragment.push(akorn.make_article_item(doc));
        }
        // Add in one go as fragment
        articles.append(fragment.join(''));
        // TODO Should be done in akorn.make_article_item
        // Convert abs. times to relative
        articles.find('time').relativeTime();
    },
    init: function() {
        // TODO Get cached HTML fragment
        // Get initial articles
        $.get('/api/latest/100', {}, akorn.refresh_articles, 'json');

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
