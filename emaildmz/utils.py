from django.contrib import messages


def get_form_errors(request, form):
    # put the errors into a dictionary to strip the html
    # this produces a key, value pair
    # where key is the field name and value is a list of errors
    for field, error_list in form.errors.get_json_data().items():
        for error in error_list:
            # get the message from the list element
            # and add it to the site messages as an error
            messages.add_message(request, messages.ERROR, error['message'])

