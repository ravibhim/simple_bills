import logging
from google.appengine.api import users
from google.appengine.ext import ndb

from models import Profile, AccountUnauthorizedAccess


def userProfile(user):
    if not user:
        raise users.UserNotFoundError("From userProfile(user)")

    user_email = user.email()
    p_key = ndb.Key(Profile, user_email)
    profile = p_key.get()
    # TODO: Instead use Model.create_or_get to wrap the get/update operation in a transaction.

    if not profile:
        profile = Profile(
            key = p_key,
            userId = user.user_id(),
            nickname = user.nickname()
        )
        logging.info('METRIC:USER_ADD - {}'.format(user_email))
        profile.put()

    return profile

def user_owns_account_check(user, account_id):
    profile = getProfile(user)
    if (account_id not in profile.accountIds):
        raise AccountUnauthorizedAccess("{} tried to access account id {}.".format(profile.key.id(), account_id))
