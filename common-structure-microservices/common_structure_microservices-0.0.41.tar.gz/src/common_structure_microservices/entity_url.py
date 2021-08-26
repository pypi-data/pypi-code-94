from common_structure_microservices.profiles import Profiles
from common_structure_microservices.utilities import Constants


class EntityUrlMap:
    config_profile = Profiles()
    _BASE_URL = 'api/'

    if config_profile.PROFILE == Constants.DEVELOP:
        _HOST_INSTITUTION = 'http://192.168.0.12:8091/institutions/'
        _HOST_USER = 'http://192.168.0.12:8092/users/'
        _HOST_PUBLICATION = 'http://192.168.0.12:8093/publications/'
        _HOST_CHAT = 'http://192.168.0.12:8097/chats/'
        _HOST_SECURITY = 'http://192.168.0.12:8094/securities/'
        _HOST_NOTIFICATION = 'http://192.168.0.12:8098/notifications/'
    else:
        _HOST_INSTITUTION = 'http://127.0.0.1:8091/institutions/'
        _HOST_USER = 'http://127.0.0.1:8092/users/'
        _HOST_PUBLICATION = 'http://127.0.0.1:8093/publications/'
        _HOST_CHAT = 'http://127.0.0.1:8097/chats/'
        _HOST_SECURITY = 'http://127.0.0.1:8094/securities/'
        _HOST_NOTIFICATION = 'http://127.0.0.1:8098/notifications/'

    USER = f'{_HOST_USER}{_BASE_URL}user/'
    COMMUNITY = f'{_HOST_USER}{_BASE_URL}community/'
    SECURITY = f'{_HOST_SECURITY}{_BASE_URL}security/'
    CONFIRMATION_ACCOUNT = f'{_HOST_SECURITY}{_BASE_URL}confirm_account/'
    CHAT = f'{_HOST_CHAT}{_BASE_URL}chat/'
    CONVERSATION = f'{_HOST_CHAT}{_BASE_URL}conversation/'
    INSTITUTION = f'{_HOST_INSTITUTION}{_BASE_URL}institution/'
    JOB_OFFER = f'{_HOST_INSTITUTION}{_BASE_URL}job_offer/'
    PUBLICATION = f'{_HOST_PUBLICATION}{_BASE_URL}publication/'
    NOTIFICATION = f'{_HOST_NOTIFICATION}{_BASE_URL}notification/'
