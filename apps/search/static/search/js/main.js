// Namespace for akorn js
var akorn = {
    // Storing set nice names for months
    // TODO Really!? In this century?
    month_names: [ "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December" ],
    // Append a given HTML Fragment to the articles list
    append_articles: function(data) {
        // Add in one go as fragment
        akorn.articles_container.append(data);
        // Add date lines
        akorn.add_date_lines();
        // Once we have finished adding, stop the pause on updates
        akorn.unpause_updates();
    },
    // Replaces the articles with a new set, rather than appending
    replace_articles: function(data) {
        // Remove prev article state
        akorn.prev_article = undefined;
        // Replace the current articles with new ones
        akorn.articles_container.html(data);
        // Add date lines
        akorn.add_date_lines();
        // Once we have finished adding, stop the pause on updates
        akorn.unpause_updates();
    },
    // Stop the scroll updates
    unpause_updates: function() {
        // Stick a delay in to mitigate scrollbar glitches
        window.setTimeout('akorn.pause_updates = false', 400);
    },
    // Get a specified number of articles
    get_articles: function(num, article_id, query, clear) {
        // Optionally pass an article id as the 2nd argument
        //      Function will return the articles after this article id
        // Optionally pass a query string as the 3rd argument
        //      Function will filter articles based on the query
        // Optionally pass a flag as the 4th argument
        //      Function will switch from appending to replacing articles
        var params = {};
        var callback;

        if(article_id !== undefined && article_id) {
            params['article'] = article_id;
        }
        if(query !== undefined && query) {
            params['q'] = query;
        }
        if(clear !== undefined && clear) {
            callback = akorn.replace_articles;
        }
        else {
            callback = akorn.append_articles;
        }
        $.get('/api/latest/'+num, params, callback, 'html');
    },
    // Add the next chunk of articles for the current query
    add_more_articles: function() {
            // Get the id of the last article
            var last_article = akorn.articles_container.find('li:last-child');
            // Stash this to use when adding date lines
            akorn.prev_article = last_article;
            // Get the current query, if set
            var query = akorn.query;
            // Get articles after the current last article
            akorn.get_articles(20, last_article.attr('id'), query);
    },
    // Cycle through the articles marking date changes
    // Also mark the users last visit
    // TODO Refactor this method
    add_date_lines: function() {
        var latest_articles, prev_date, prev_datetime, latest_article;
        var i, date_str, date_bits, last_visit_obj, date_obj, date_added;
        var ak = akorn; // Cache local ref
        var prev_article = ak.prev_article;
        var add_last_visit = false;
        var last_visit = ak.last_visit; // Get the users last visit

        if(prev_article === undefined) {
            // If it is not set then take the first in the whole list
            prev_article = ak.articles_container.find('li:first');
        }
        // Get all the articles that follow the last article before this set
        latest_articles = prev_article.nextAll();
        // Get the date of the previous article
        prev_datetime = prev_article
                .find('meta')
                .attr('content');
        prev_date = prev_datetime.substr(0,10);
        // If a last visit is set then add a line
        if(last_visit !== undefined) {
            last_visit_obj = new Date(last_visit);
            // Check against the first article
            prev_datetime_obj = new Date(prev_datetime);
            if(last_visit_obj > prev_datetime_obj) {
                // TODO Do something if there are no new articles
                console.warn('There are no new articles');
                // Unset last_visit to prevent further checking
                akorn.last_visit = undefined;
            }
            else {
                add_last_visit = true;
            }
        }

        for(i=0, len=latest_articles.length; i<len; i++) {
            date_added = false;
            latest_article = $(latest_articles[i]);
            // Get the date of the article
            datetime_str = latest_article
                .find('p.meta meta')
                .attr('content');
            // Get just the date
            date_str = datetime_str.substr(0,10);
            // If the date does not match
            if(date_str !== prev_date) {
                // Make a date line
                date_bits = date_str.split('-');
                date_added = $(['<h2>',date_bits[2],
                                ' ',
                                ak.month_names[parseInt(date_bits[1])-1],
                                '</h2>']
                                .join(''));
                date_added.insertBefore(latest_article);
            }
            // Are we looking for a last visit
            if(add_last_visit) {
                // Make a date object for fine comparison
                date_obj = new Date(datetime_str);
                // Check if line should go before this datetime?
                if(last_visit_obj > date_obj) {
                    // Add a last visit line
                    if(date_added) {
                        date_added.attr('id','last_visit')
                            .append(' — Your previous visit');
                    }
                    else {
                        $('<h2 id="last_visit">Your previous visit</h2>')
                            .insertBefore(latest_article);
                    }
                    // Unset last_visit to prevent further checking
                    akorn.last_visit = undefined;
                    // Turn off last visit checking
                    add_last_visit = false;
                }
            }
            // Reset the previous date
            prev_date = date_str;
        }
    },
    // Generic throttling function
    throttle: (function () {
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
    search_config: {
        allowSpaces: true,
        placeholderText: "Search for journals...",
        // Called when a tag is added
        onTagAdded: function(event, tag) {
            var query = akorn.search_box.tagit("assignedTags").join('+');
            akorn.query = query;
	        akorn.get_articles(20,
                    undefined,
                    query,
                    true);
        },
        // Called when a tag is removed
        onTagRemoved: function(event, tag) {
            // Get array of assigned tags
            var tags_arr = akorn.search_box.tagit("assignedTags");
            // Find the removed tag
            var tag_idx = $.inArray(tag, tags_arr);
            if(tag_idx) {
                    // Remove it
                tags_arr.splice(tag_idx, 1);
            }
            var query = tags_arr.join('+');
            akorn.query = query;
            akorn.get_articles(20,
                    undefined,
                    query,
                    true);
        },
        _highlight: function(s, t) {
            var matcher = new RegExp("("+$.ui.autocomplete.escapeRegex(t)+")", "ig" );
            return s.replace(matcher, "<strong>$1</strong>");
        },
        // Function to use for auto-completion
        tagSource: function(search, showChoices) {
            $.ajax({
                url: "/api/journals",
                data: {'term': search.term},
                dateType: "json",
                // TODO Copy and paste code, should be possible to improve
                success: function(data) {
                    var assigned = akorn.search_box.tagit("assignedTags");
                    var filtered = [];
                    for (var i=0, dlen=data.length; i < dlen; i++) {
                        if ($.inArray(data[i], assigned) == -1) {
                            filtered.push({label: akorn.search_config._highlight(data[i], search.term), value: data[i]});
                        }
                    }
                    showChoices(filtered);
                },
            });
        },
    },
    init: function() {
        // Get the place to stick articles
        // Set it as a static property to be accessible across instances
        akorn.articles_container = $('#latest_articles');
        // Get initial articles
        akorn.get_articles(20);
        // TODO Search input should be hidden before this point
        // Activate the search box
        akorn.search_box = $('#search');
        akorn.search_box.tagit(akorn.search_config);
        // Listen to window scroll events
        // Reduce spurious calls by adding a 250 ms delay between triggers
        $(window).scroll(akorn.throttle(function() {
            akorn.check_position();
        }, 250));
    },
};

// When the document has loaded start the show
$(document).ready(akorn.init);
