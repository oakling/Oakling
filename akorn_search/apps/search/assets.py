from django_assets import Bundle, register

# Compile sass files to css and squash
sass = Bundle('search/sass/main.scss',\
    'search/sass/index.scss',\
    'search/sass/recruitment.scss',\
    'search/sass/font-awesome.scss',\
    filters='scss,cssmin', output='gen/packed.css')

# Pack js libraries
libs = Bundle('search/js/jquery.min.js',\
    'search/js/jquery.jsonp-2.4.0.min.js',\
    'search/js/bootstrap.min.js',\
    'search/js/jquery-ui-1.8.22.custom.js',\
    output='gen/packed.js')

register('search_css', sass)
register('search_js_libs', libs)