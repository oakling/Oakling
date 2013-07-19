from django_assets import Bundle, register

# Compile sass files to css and squash
sass = Bundle('simulator/sass/main.scss',\
    filters='scss,cssmin', output='gen/sim.css')

register('sim_css', sass)
