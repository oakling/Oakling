// Namespace for akorn js
var akorn = {
    append_articles: function(data) {
        // Add in one go as fragment
        akorn.articles_container.append(data);
        // Once we have finished adding, stop the pause on updates
        // Stick a delay in to mitigate scrollbar glitches
        window.setTimeout('akorn.pause_updates = false', 400);
    },
    get_articles: function(num, article_id) {
        // Get a specified number of articles
        // Optionally pass an article id as the 2nd argument
        //      Function will return the articles after this article id
        var params = {};
        if(article_id !== undefined) {
            params['article'] = article_id;
        }
        $.get('/api/latest/'+num, params, akorn.append_articles, 'html');
    },
    add_more_articles: function() {
            // Get the id of the last article
            var last_article = akorn.articles_container.find('li:last-child').attr('id');
            akorn.get_articles(20, last_article);
    },
    throttle: (function () {
        // Generic throttling function
        return function (fn, delay) {
            delay || (delay = 100);
            var last = +new Date;
            return function () {
                var now = +new Date;
                if (now - last > delay) {
                    fn.apply(this, arguments);
                    last = now;
                }
            };
        };
    })(),
    check_position: function() {
        if ($(window).scrollTop() >= $(document).height() - $(window).height() - 400) {
            if (!akorn.pause_updates)
            {
                akorn.pause_updates = true;
                akorn.add_more_articles();
            }
            return true;
        }
    },
    init: function() {
        // Get the place to stick articles
        // Set it as a static property to be accessible across instances
        akorn.articles_container = $('#latest_articles');
        // Get initial articles
        akorn.get_articles(20);
        // TODO Search input should be hidden before this point
        // Activate the search box
        $('#search').tagsInput({
            autocomplete_url:'/api/journals',
            autocomplete:{selectFirst:true,width:'100px',autoFill:true},
            height: '15px',
            width: '800px',
            defaultText: 'Search',
        });
        // Listen to window scroll events
        // Reduce spurious calls by adding a 250 ms delay between triggers
        $(window).scroll(akorn.throttle(function() {
            akorn.check_position();
        }, 250));
    },
};

// When the document has loaded start the show
$(document).ready(akorn.init);
