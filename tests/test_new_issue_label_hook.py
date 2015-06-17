from ghi_assist.hooks.new_issue_label_hook import NewIssueLabelHook
import json

def test_no_labels():
    """Test no labels to apply."""
    hook = NewIssueLabelHook({
        "action": "opened",
        "issue": {
            "body": "foo bar baz",
            "assignee": None,
            "labels": [],
            "url": "http://",
        },
    })
    assert hook.should_perform_action(), "No labels: mark as untriaged"
    assert hook.actions()[0]["args"]["labels"] == ["status: untriaged"]

def test_labels_assigned():
    """Test with new labels."""
    hook = NewIssueLabelHook({
        "action": "opened",
        "issue": {
            "body": "##foo bar baz",
            "assignee": {},
            "labels": [],
            "url": "http://",
        },
    }, whitelist=["foo"])
    assert hook.should_perform_action(), "Got labels."
    assert hook.actions()[0]["args"]["labels"] == ["foo", "status: claimed"]

def test_labels_unassigned():
    """Test with new labels."""
    hook = NewIssueLabelHook({
        "action": "opened",
        "issue": {
            "body": "##foo bar baz",
            "assignee": None,
            "labels": [],
            "url": "http://",
        },
    }, whitelist=["foo"])
    assert hook.should_perform_action(), "Got labels."
    assert hook.actions()[0]["args"]["labels"] == ["foo"]

def test_invalid_action():
    """Test with action other than "opened"."""
    hook = NewIssueLabelHook({
        "action": "closed"
    })
    assert not hook.should_perform_action(), "Not newly opened."

def test_gh_labels_unassigned():
    """Test labelling using github's mechanism (not our adhoc parsing)."""
    hook = NewIssueLabelHook({
        "action": "opened",
        "issue": {
            "body": "some description",
            "assignee": {},
            "labels": ["bar", "baz"],
            "url": "http://",
        }
    })
    assert hook.should_perform_action(), "Got labels"
    assert hook.actions()[0]["args"]["labels"] == ["bar", "baz", "status: claimed"]

def test_gh_labels_assigned():
    """Test labelling using github's mechanism (not our adhoc parsing)."""
    hook = NewIssueLabelHook({
        "action": "opened",
        "issue": {
            "body": "some description",
            "assignee": None,
            "labels": ["bar", "baz"],
            "url": "http://",
        }
    })
    assert hook.should_perform_action(), "Got labels"
    assert hook.actions()[0]["args"]["labels"] == ["bar", "baz"]

def test_payload():
    """Test using "real" payload."""
    hook = NewIssueLabelHook(get_payload("new_issue_label.json"), whitelist=["foo"])
    assert hook.should_perform_action(), "New issue with labels"
    assert hook.actions()[0]["args"] == {
        "issue_url": "https://api.github.com/repos/user-foo/repo-bar/issues/10",
        "labels": ["foo"],
    }

def get_payload(input_filename):
    """Parse the JSON payload and return an object."""
    with open("tests/payloads/" + input_filename) as input_file:
        return json.load(input_file)