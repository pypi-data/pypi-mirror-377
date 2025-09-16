import pytest

def test_automations(live_client):
    automations = live_client.automations.all()
    assert isinstance(automations, list)
    assert all(isinstance(a, dict) for a in automations)

    tags = live_client.automations.tags()
    assert isinstance(tags, list)

    if automations and len(automations) > 0:
        first_automation = automations[0]
        workflow_id = first_automation.get('id')
        print(f"Testing automation with ID: {workflow_id}")
        assert workflow_id is not None

        automation_details = live_client.automations.get(workflow_id)
        assert isinstance(automation_details, dict)
        assert automation_details.get('id') == workflow_id

        log = live_client.automations.get_log(workflow_id)
        assert isinstance(log, dict)

        status = live_client.automations.get_status(workflow_id)
        assert isinstance(status, dict)