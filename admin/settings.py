SETTINGS = {
    'form': {
        'readonly_fields': ['created_at', 'updated_at']
    }
}


def get_setting(subject: str, name: str ) -> str:
    subject_ = SETTINGS.get(subject)
    if subject_ == None:
        raise ValueError(f'The subject: {subject} not found')
    setting = subject_.get(name)
    if setting == None:
        raise ValueError(f'The seting: {name} in {subject} not found')
    return setting
