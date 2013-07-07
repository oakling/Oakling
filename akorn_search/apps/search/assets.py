from django_assets import Bundle, register

# Compile sass files to css and squash
sass = Bundle('search/sass/main.scss',\
    'search/sass/index.scss',\
    'search/sass/flatpage.scss',\
    'search/sass/recruitment.scss',\
    filters='scss,cssmin')

css = Bundle(
    'search/css/bootstrap.css',\
    sass,\
    filters="cssmin", output="gen/packed.css")

# Pack js libraries
libs = Bundle('search/js/jquery.min.js',\
    'search/js/bootstrap.min.js',\
    'search/select2/select2.js',\
    output='gen/packed.js')

register('search_css', css)
register('search_js_libs', libs)
