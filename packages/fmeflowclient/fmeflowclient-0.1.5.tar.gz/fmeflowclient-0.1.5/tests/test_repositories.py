def test_repositories(live_client):
    repositories = live_client.repositories.all()
    assert isinstance(repositories, list)
    assert all(isinstance(r, dict) for r in repositories)

    if repositories and len(repositories) > 0:
        first_repo = repositories[0]
        repo_name = first_repo.get('name')
        print(f"Testing repository with name: {repo_name}")
        assert repo_name is not None

        repo_details = live_client.repositories.get(repo_name)
        assert isinstance(repo_details, dict)
        assert repo_details.get('name') == repo_name