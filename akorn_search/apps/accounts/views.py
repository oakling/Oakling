from django.views.generic.edit import FormView

from .models import AkornUser
from .forms import AkornUserCreationForm

class RegisterView(FormView):
    """
    Custom registration view that attaches saved searches to
    our custom User objects
    """
    form_class = AkornUserCreationForm
    template_name = 'accounts/register.html'
    success_url = '/'

    def add_saved_searches(self):
        """
        Return dict representing the searches the user
        has saved before registering.
        """
        # Get structure from sessions or return None
        return self.request.session.get('saved_searches')

    def create_user(self, form):
        user = AkornUser.objects.create_user(
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password1'],
            # Attach information from session to user model
            settings=self.add_saved_searches()
        )

    def form_valid(self, form):
        self.create_user(form)
        return super(RegisterView, self).form_valid(form)
