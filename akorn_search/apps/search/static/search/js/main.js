var format = function(state, len) {
        var text = state.text;
        if (text.length-3 > len) {
            text = text.substring(0, len)+'…';
        }

        return ['<i class="icon-',
            state.type,
            '"></i>',
            '<span title="',
            state.text,
            '">',
            text,
            '</span>'
        ].join('');
    }

var select_format = function(state) {
        return format(state, 70);
    }

var tag_format = function(state) {
        return format(state, 25);
    }

var select2_options = {
    tags: true,
    multiple: true,
    width: "off",
    minimumInputLength: 2,
    formatResult: select_format,
    formatSelection: tag_format,
    escapeMarkup: function(m) { return m; },
    createSearchChoice: function(term, data) {
        // Check whether user supplied term matches a choice
        if ($(data).filter(function() {
            return this.text.localeCompare(term)===0;
        }).length===0) {
            // If it does not then 'create' a new choice and return it
            // Mark it as a keyword
            return {id:term, text:term, type: 'keyword'};
        }
    },
    ajax: {
        url: '/api/journals',
        dataType: 'json',
        data: function(term, page) {
            return {
                // ?term=<user input>
                term: term
            };
        },
        results: function(data, page) {
            return {
                results: data
            };
        }
    }
}

// Namespace for akorn js
var akorn = {
    query: {},
    limit: 10,
    skip: 0,
    // Storing set nice names for months
    month_names: [ "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" ],
    load_pane: function(pane_url, pane_el) {
        var ak = akorn;
        var container = pane_el.find('.accordion-inner');
        $.jsonp({
            "url": pane_url+"?jsonp=?",
            "success": function(data) {
                akorn.show_pane(data.key, container);
            },
            "error": function(data, msg) {
                container.html('No results found.');
            }
        });
    },
    show_pane: function(data, container) {
        // Replace the current articles with new ones
        container.html(data);
    },
    // Append a given HTML Fragment to the articles list
    append_articles: function(data) {
        var ak = akorn;
        // Add in one go as fragment
        ak.articles_container.append(data);
        // Add date lines
        ak.add_date_lines();
        // Once we have finished adding, stop the pause on updates
        ak.unpause_updates();
        // Increment the skip counter
        ak.skip += ak.limit;
    },
    // Replaces the articles with a new set, rather than appending
    replace_articles: function(data) {
        var ak = akorn;
        // Remove prev article state
        ak.prev_article = undefined;
        // Replace the current articles with new ones
        ak.articles_container.html(data);
        // Add date lines
        ak.add_date_lines();
        // Once we have finished adding, stop the pause on updates
        ak.unpause_updates();
        // Increment the skip counter
        ak.skip += ak.limit;
    },
    // Stop the scroll updates
    unpause_updates: function() {
        // Stick a delay in to mitigate scrollbar glitches
        window.setTimeout('akorn.pause_updates = false', 400);
    },
    make_keyword_query: function(query) {
    // Take a query object and return a string for use in get_articles
        return this.make_query(query, 'keyword');
    },
    make_journal_query: function(query) {
    // Take a query object and return a string for use in get_articles
        return this.make_query(query, 'journal');
    },
    make_query: function(query, type) {
    // Take a query object and return a string for use in get_articles
        var query_bit, article_query = [];
        for(var i=0, len=query.length; i<len; i++) {
            query_bit = query[i];
            if (query_bit['type'] === type) {
                article_query.push(query_bit['id']);
            }
        }
        return article_query.join('|');
    },
    // Get a specified number of articles
    get_articles: function(query, replace) {
        // Optionally pass a flag as the 2nd argument
        //      Function will switch from appending to replacing articles
        var ak = akorn;
        var callback;

        if(replace !== undefined && replace) {
            callback = ak.replace_articles;
            // We are clearing, so reset the skip counter
            ak.skip = 0;
        }
        else {
            callback = ak.append_articles;
        }

        var params = {
            'skip': ak.skip,
            'limit': ak.limit
        };

        if(query !== undefined && query) {
            var keyword_str = ak.make_keyword_query(query);
            if(keyword_str !== '') {
                params['k'] = keyword_str;
            }
            var journal_str = ak.make_journal_query(query);
            if(journal_str !== '') {
                params['j'] = journal_str;
            }
        }
        $.get('/api/articles', params, callback, 'html');
        // Save the query state
        ak.save_state();
    },
    // Add the next chunk of articles for the current query
    add_more_articles: function() {
            var ak = akorn;
            // Get the last article for use later
            ak.prev_article = ak.articles_container
                .find('li:last-child');
            // Get articles after the current last article
            var tags = ak.search_box.select2("data");
            ak.get_articles(tags);
    },
    insert_date_line: function(date_str, latest_article) {
        var content = 'Today', month, day;
        // Is it today?
        if(arguments[2] === undefined || !arguments[2]) {
            var date_bits = date_str.split('-');
            day = date_bits[2];
            month = akorn.month_names[parseInt(date_bits[1])-1];
        }
        // Make a date line
        date_added = $(['<h2><span class="month">',
            month,
            '</span><span class="day">',
            day,
            '</span></h2>']
            .join(''));
        date_added.insertBefore(latest_article);
        return;
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
        var first_run = false;

        if(prev_article === undefined) {
            // If it is not set then take the first in the whole list
            prev_article = ak.articles_container.find('li:first');
            first_run = true;
        }
        // Get all the articles that follow the last article before this set
        latest_articles = prev_article.nextAll('li');
        // Get the date of the previous article
        prev_datetime = prev_article
                .find('meta')
                .attr('content');

        if(prev_datetime === undefined) {
            return;
        }

        prev_date = prev_datetime.substr(0,10);

        if(first_run) {
            // Is it today?
            var today = false;
            if(new Date(prev_datetime) === new Date()) {
                today = true;
            }
            // and print an initial date/today line
            ak.insert_date_line(prev_date, prev_article, today);
        }

        // If a last visit is set then add a line
        if(last_visit !== undefined) {
            last_visit_obj = new Date(last_visit);
            // Check against the first article
            prev_datetime_obj = new Date(prev_datetime);
            if(last_visit_obj > prev_datetime_obj) {
                // TODO Do something if there are no new articles
                console.warn('There are no new articles');
                // Unset last_visit to prevent further checking
                ak.last_visit = undefined;
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
                .find('meta')
                .attr('content');
            // Get just the date
            date_str = datetime_str.substr(0,10);
            // If the date does not match
            if(date_str !== prev_date) {
                ak.insert_date_line(date_str, latest_article);
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
                    ak.last_visit = undefined;
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
            var ak = akorn;
            // Check updating is not paused to wait for previous update
            if (!ak.pause_updates)
            {
                // Pause updating
                ak.pause_updates = true;
                // Add a new set of articles
                ak.add_more_articles();
            }
            return true;
        }
    },
    get_articles_for_query: function() {
    // Get articles based on tags in search box
        var ak = akorn;
        var tags = ak.search_box.select2("data");
        ak.get_articles(tags, true);
    },
    populate_search_from_query: function(query_obj) {
        var ak = akorn;
        // Clean the search box
        ak.search_box.select2("val", "");
        // Create each in order
        ak.search_box.select2("data", query_obj);
        return this;
    },
    decode_unicode: function(encoded_str) {
    // Used to decode strings encoded with django filter escapejs
        // TODO Replace with compiled regex
        var regx = /\\u([\d\w]{4})/gi;
        var decoded_str = encoded_str.replace(regx, function(match, grp) {
            return String.fromCharCode(parseInt(grp, 16));
        });
        return decoded_str;
    },
    saved_search_handler: function(e) {
    // Handles clicks on the individual saved search queries
        var ak = akorn;
        // Get the saved query from the target link
        var target = $(e.currentTarget);
        var query = target.data('query');
        // TODO Check for way to avoid decoding
        if($.type(query) === "string") {
            query = JSON.parse(ak.decode_unicode(query));
        }
        ak.query = query;
        // Change tags displayed in search box
        ak.populate_search_from_query(query);
        // Do a new query
        ak.get_articles(query, true);
        // Stop the event from propagating
        return false;
    },
    delete_saved_search_handler: function(e) {
        var query_id = $(e.currentTarget).attr('data-queryid');
        var params = {};
        params['query_id'] = query_id;
        // TODO Make removal and deletion async and enable undoing
        $.get('/api/remove_search', params,
            function(data) {
                $(['#',query_id].join('')).remove();
            }, 'html');
        return false;
    },
    shorten_query: function(query_obj) {
    // Takes a query string and produces a pretty HTML rendering of it
        var output = [];
        // Split the query into each journal
        for(var i=0, len=query_obj.length; i<len; i++) {
            // Format the name
            output.push(format(query_obj[i], 13));
        }
        return output.join('<br />');
    },
    add_saved_search: function(query, query_id) {
        var ak = akorn;
        // Make item element
        var el = $(['<li id="',query_id,'">',
                    '<span data-queryid="',
                    query_id,
                    '" class="delete">&times;</span></div>',
                    '<div class="terms"><p>',
                    ak.shorten_query(query),
                    '</p></div></li>'].join(''));
        el.children('a').data('query', $.extend(true, {}, query));
        // Add to list of saved searches
        ak.saved_searches.prepend(el);
    },
    post_saved_search: function(query) {
    // Take a given query and save it to the server
        $.post('/api/save_search', {query: JSON.stringify(query)},
            function(data){
                console.log('Query saved successfully');
                akorn.add_saved_search(query, data['query_id']);
            }, 'json');
    },
    save_search_handler: function(e) {
    // Handles clicks on the save this query button
        var ak = akorn;
        // Get the tags
        var tags = ak.search_box.select2("data");
        // Save the search
        ak.post_saved_search(tags);
        return false;
    },
    activate_search_box: function() {
        var ak = akorn;
        // Add handler for save search button
        var save_search = $('#save_search');
        save_search.on('click', ak.save_search_handler);
        // Add handler for saved search links
        saved_searches = $('#saved_searches');
        saved_searches.on('click', 'li',
            ak.saved_search_handler);
        // Add handler for deleted saved search links
        saved_searches.on('click', '.delete',
            ak.delete_saved_search_handler);
        ak.saved_searches = saved_searches;
        ak.save_search = save_search;
        // Activate the search box
        var search_box = $('#search');
        search_box.select2(select2_options);
        ak.search_box = search_box;
        // Listen for changes on search box
        search_box.on('change', ak.get_articles_for_query);
    },
    state: function() {
        return {'query': akorn.query};
    },
    save_state: function() {
        // We need to store the query and saved searches
        // This is so we don't break the back button
        history.replaceState(akorn.state(), "");
    }, 
    load_state: function(e) {
        // Set the state using state passed by popstate event
        var state = e.state;
        // Check for state
        if(!state) {
            return;
        }
        // Use the query property to get articles
        if(state.query !== undefined) {
            akorn.get_articles(state.query, true);
        }
    },
    init: function() {
        var ak = akorn;
        // Get the place to stick articles
        // Set it as a static property to be accessible across instances
        ak.articles_container = $('#articles');
        // Activate search box
        ak.activate_search_box();

        // Listen to window scroll events
        // Reduce spurious calls by adding a 250 ms delay between triggers
        $(window).scroll(ak.throttle(function() {
            ak.check_position();
        }, 250));

        // Listen to window popstate events
        $(window).on('popstate', ak.load_state);
    }
};

jQuery(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});
