from .forms import SearchForm

def search_form_processor(request):
    return {'search_form': SearchForm()}
