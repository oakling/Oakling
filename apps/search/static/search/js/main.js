// Namespace for akorn js
var akorn = {
    // TODO Really!? In this century?
    month_names: [ "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December" ],
    append_articles: function(data) {
        // Add in one go as fragment
        akorn.articles_container.append(data);
        // Add date lines
        if(akorn.prev_article !== undefined) {
            akorn.add_date_lines();
        }
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
            var last_article = akorn.articles_container.find('li:last-child');
            // Stash this to use when adding date lines
            akorn.prev_article = last_article;
            // Get articles after the current last article
            akorn.get_articles(20, last_article.attr('id'));
    },
    add_date_lines: function() {
        var prev_article = akorn.prev_article;
        // Get all the articles that follow the last article before this set
        var latest_articles = prev_article.nextAll();
        // Get the date of the previous article
        var prev_datetime = prev_article.find('meta').attr('content').substr(0,10);
        // TODO Remove... just for testing
        prev_datetime = "qfGQGE";
        for(var i=0, len=latest_articles.length; i<len; i++) {
            // Get the date of the article
            var date_str = $(latest_articles[i]).find('p.meta meta').attr('content').substr(0,10);
            // If the date does not match
            if(date_str !== prev_datetime) {
                // Make a date line
                var date_bits = date_str.split('-');
                $(['<h2>',date_bits[2],' ',akorn.month_names[parseInt(date_bits[1])-1],'</h2>'].join('')).insertBefore(latest_articles[i]);
            }
            // Reset the previous date
            prev_datetime = date_str;
        }
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
        // Trigger if scroll position is 400 px off the bottom
        if ($(window).scrollTop() >= $(document).height() - $(window).height() - 400) {
            // Check updating is not paused to wait for previous update
            if (!akorn.pause_updates)
            {
                // Pause updating
                akorn.pause_updates = true;
                // Add a new set of articles
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
