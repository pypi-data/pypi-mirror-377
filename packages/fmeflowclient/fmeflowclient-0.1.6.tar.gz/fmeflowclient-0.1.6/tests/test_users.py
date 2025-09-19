from fmeflowclient import User

def test_users(live_client):
    users = live_client.users.all()
    assert(isinstance(users, list))

    if len(users) > 0:
        first_user = users[0]
        assert(isinstance(first_user, User))
        assert(hasattr(first_user, "name"))