def test_projects(live_client):
    projects = live_client.projects.all()
    assert isinstance(projects, list)
    assert all(isinstance(p, dict) for p in projects)

    if projects and len(projects) > 0:
        first_project = projects[0]
        project_id = first_project.get('id')
        print(f"Testing project with ID: {project_id}")
        assert project_id is not None

        project_details = live_client.projects.get(project_id)
        assert isinstance(project_details, dict)
        assert project_details.get('id') == project_id