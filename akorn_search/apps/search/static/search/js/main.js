// Namespace for akorn js
var akorn = {
    query: {},
    // Storing set nice names for months
    month_names: [ "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December" ],
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
    },
    // Stop the scroll updates
    unpause_updates: function() {
        // Stick a delay in to mitigate scrollbar glitches
        window.setTimeout('akorn.pause_updates = false', 400);
    },
    make_keyword_query: function(query_obj) {
    // Take a query object and return a string for use in get_articles
        queries = [];
        for(q in query_obj) {
            if (query_obj[q]['type'] === 'keyword') {
                queries.push(q);
            }
        }
        return queries.join('+');
    },
    make_journal_query: function(query_obj) {
    // Take a query object and return a string for use in get_articles
        queries = [];
        for(q in query_obj) {
            if (query_obj[q]['type'] === 'journal') {
                queries.push(q);
            }
        }
        return queries.join('+');
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
            params['last_ids'] = article_id;
        }
        if(query !== undefined && query) {
            var keyword_str = akorn.make_keyword_query(query);
            if(keyword_str !== '') {
                params['k'] = keyword_str;
            }
            var journal_str = akorn.make_journal_query(query);
            if(journal_str !== '') {
                params['j'] = journal_str;
            }
        }
        if(clear !== undefined && clear) {
            callback = akorn.replace_articles;
        }
        else {
            callback = akorn.append_articles;
        }
        $.get('/api/articles', params, callback, 'html');
    },
    // Add the next chunk of articles for the current query
    add_more_articles: function() {
            var ak = akorn;
            // Get the ids of the last articles of each journal
            var last_article = ak.articles_container
                    .find('meta[itemprop="last_ids"]:last')
                    .attr("content");
            // Get the last article for use later
            ak.prev_article = ak.articles_container
                    .find('li:last-child');
            // Get the current query, if set
            var query = ak.query;
            // Get articles after the current last article
            ak.get_articles(20, last_article, query);
    },
    insert_date_line: function(date_str, latest_article) {
        var content = 'Today';
        // Is it today?
        if(arguments[2] === undefined || !arguments[2]) {
            var date_bits = date_str.split('-');
            content = [date_bits[2],
            ' ',
            akorn.month_names[parseInt(date_bits[1])-1]].join('');
        }
        // Make a date line
        date_added = $(['<h2>',
            content,
            '</h2>']
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
    search_config: {
        allowSpaces: true,
        placeholderText: "Search for journals...",
        // Called when a tag is added
        afterTagAdded: function(event, ui) {
            var tag = $(ui.tag);
            var ak = akorn;
            // Initialise search object
            var search_obj = {'type': 'journal'};
            // Get the text content of the tag
            var tag_label = tag.find('span.tagit-label').text();
            // Retrieve journal data
            var tag_data = tag.data('search_string');
            // Check if it is marked as a journal
            var journal_flag = tag.hasClass('journal');
            // If not a journal, then it is a keyword
            if(!journal_flag) {
                tag_data = tag_label;
                search_obj['type'] = 'keyword';
            }
            // If no tag defined look for current selection
            else if(!tag_data) {
                tag_data = ak.current_selection;
                // Attach journal data to tag
                tag.data('search_string', tag_data);
                // Unset the current selection
                delete ak.current_selection;
            }
            search_obj['label'] = tag_label;
            search_obj['query'] = tag_data;
            // Save search
            ak.query[tag_data] = search_obj;
            // Enable save search button
            ak.save_search.removeAttr('disabled');
            // Refresh the list
	        ak.get_articles(20,
                undefined,
                ak.query,
                true);
        },
        // Stop non autocomplete tags from being created
        beforeTagAdded: function(event, ui) {
            var initilized = ui.duringInitialization;
            // Check if tag is being added by a user
            if(initilized === undefined || initilized === false) {
                // Get the text of the tag
                var tag_value = ui.tag.find('.tagit-label').text();
                // Check text against all choices
                try {
                    for(var i=0, choices_len = akorn.choices.length; i<choices_len; i++) {
                        // If there is a match then add the tag
                        if(tag_value===akorn.choices[i]['value']) {
                            // TODO Do something less stupid?
                            $(ui.tag).addClass('journal');
                            return true;
                        }
                    }
                }
                catch (e) {
                    // TypeError throw in choices does not exist
                    // pass
                }
            }
            // Otherwise mark the tag as a keyword
            $(ui.tag).addClass('keyword');
        },
        // Called when a tag is removed
        afterTagRemoved: function(event, ui) {
            var search;
            var ak = akorn;
            var tag = $(ui.tag);
            if(tag.hasClass('journal')) {
                // Find the journal id
                search = tag.data('search_string');
            }
            else {
                search = tag.find('.tagit-label').text();
            }
            // Remove from stored query
            delete ak.query[search];
            // Refresh the articles list
            ak.get_articles(20,
                    undefined,
                    ak.query,
                    true);
        },
        _highlight: function(s, t) {
            var matcher = new RegExp("("+$.ui.autocomplete
                .escapeRegex(t)+")", "ig" );
            return s.replace(matcher, "<strong>$1</strong>");
        },
        make_label: function(value, search, full) {
            var label = this._highlight(value, search);
            return [label,' <span class="full">', full, '</span>'].join('');
        },
        // Function to use for auto-completion
        autocomplete: {
            focus: function(e, ui) {
                akorn.current_selection = ui.item['search'];
            },
            source: function(search, showChoices) {
                $.ajax({
                        url: "/api/journals_new",
                        data: {'term': search.term},
                        dateType: "json",
                        // TODO Copy and paste code, should be possible to improve
                        success: function(data) {
                            var ak = akorn;
                            var assigned = ak.search_box.tagit("assignedTags");
                            var filtered = [];
                            for (var i=0, dlen=data.length; i < dlen; i++) {
                                full = data[i][0];
                                val = data[i][1];
                                query_val = data[i][2];
                                if ($.inArray(val, assigned) == -1) {
                                    filtered.push({label: ak.search_config
                                        .make_label(val, search.term, full),
                                        value: val,
                                        search: query_val});
                                }
                            }
                            akorn.choices = filtered;
                            showChoices(filtered);
                        }
                    }
                );
            }
        },
    },
    populate_search_from_query: function(query_obj) {
        var aks = akorn.search_box;
        // Clean the search box
        aks.tagit('removeAll', false);
        // Create each in order
        for(keyword in query_obj) {
            akorn.current_selection = $.trim(query_obj[keyword]['query']);
            // Add journal class, turn off the completion check and events
            aks.tagit('createTag',
                $.trim(query_obj[keyword]['label']),
                'journal', true);
        }
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
        ak.get_articles(20,
                    undefined,
                    query,
                    true);
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
                $(['#',query_id].join('')).parent('li').remove();
            }, 'html');
        return false;
    },
    shorten_query: function(query_obj) {
    // Takes a query string and produces a pretty HTML rendering of it
        var b;
        var output = [];
        // Split the query into each journal
        for(keyword in query_obj) {
            b = query_obj[keyword]['label'];
            // Check if the journal name is longer than we want
            if(b.length <= 42) {
                output.push(b);
            }
            else {
                output.push(['<span title="',b,'">',
                    b.substr(0,40),'&hellip;</span>'].join(''));
            }
        }
        return output.join(' +<br />');
    },
    add_saved_search: function(query, query_id) {
        var ak = akorn;
        // Make item element
        var el = $(['<li><div class="tools">',
                    '<i data-queryid="',
                    query_id,
                    '"  class="delete icon-trash"></i></div>',
                    '<a id="',query_id,'">',
                    ak.shorten_query(query),
                    '</a></li>'].join(''));
        el.children('a').data('query', $.extend(true, {}, query));
        // Add to list of saved searches
        ak.saved_searches.append(el);
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
        // Check if button is disabled
        if(ak.save_search.attr('disabled') === 'disabled') {
            return true;
        }
        // Get the search terms
        ak.post_saved_search(ak.query);
        return false;
    },
    activate_search_box: function() {
        var ak = akorn;
        // Add handler for save search button
        var save_search = $('#save_search');
        save_search.on('click', ak.save_search_handler);
        // Add handler for saved search links
        saved_searches = $('#saved_searches');
        saved_searches.on('click', 'li a',
            ak.saved_search_handler);
        // Add handler for deleted saved search links
        saved_searches.on('click', '.tools i.delete',
            ak.delete_saved_search_handler);
        ak.saved_searches = saved_searches;
        ak.save_search = save_search;
        // Activate the search box
        ak.search_box = $('#search');
        ak.search_box.tagit(ak.search_config);
    },
    init: function() {
        var ak = akorn;
        // Get the place to stick articles
        // Set it as a static property to be accessible across instances
        ak.articles_container = $('#latest_articles');
        // Get initial articles
        ak.get_articles(20);
        // Activate search box
        ak.activate_search_box();

        // Listen to window scroll events
        // Reduce spurious calls by adding a 250 ms delay between triggers
        $(window).scroll(ak.throttle(function() {
            ak.check_position();
        }, 250));
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
