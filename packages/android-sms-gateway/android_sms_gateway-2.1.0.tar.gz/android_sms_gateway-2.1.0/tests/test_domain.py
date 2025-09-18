import pytest

from android_sms_gateway.enums import WebhookEvent, MessagePriority
from android_sms_gateway.domain import MessageState, RecipientState, Webhook, Message


# Test for successful instantiation from a dictionary
def test_message_state_from_dict():
    payload = {
        "id": "123",
        "state": "Pending",
        "recipients": [
            {"phoneNumber": "123", "state": "Pending"},
            {"phoneNumber": "456", "state": "Pending"},
        ],
        "isHashed": True,
        "isEncrypted": False,
    }

    message_state = MessageState.from_dict(payload)
    assert message_state.id == payload["id"]
    assert message_state.state.name == payload["state"]
    assert all(
        isinstance(recipient, RecipientState) for recipient in message_state.recipients
    )
    assert len(message_state.recipients) == len(payload["recipients"])
    assert message_state.is_hashed == payload["isHashed"]
    assert message_state.is_encrypted == payload["isEncrypted"]


# Test for backward compatibility
def test_message_state_from_dict_backwards_compatibility():
    payload = {
        "id": "123",
        "state": "Pending",
        "recipients": [
            {"phoneNumber": "123", "state": "Pending"},
            {"phoneNumber": "456", "state": "Pending"},
        ],
    }

    message_state = MessageState.from_dict(payload)
    assert message_state.id == payload["id"]
    assert message_state.state.name == payload["state"]
    assert all(
        isinstance(recipient, RecipientState) for recipient in message_state.recipients
    )
    assert len(message_state.recipients) == len(payload["recipients"])
    assert message_state.is_hashed is False
    assert message_state.is_encrypted is False


# Test for handling missing fields
def test_message_state_from_dict_missing_fields():
    incomplete_payload = {
        "id": "123",
        # 'state' is missing
        "recipients": [
            {"phoneNumber": "123", "state": "Pending"}
        ],  # Assume one recipient is enough to test
        "isHashed": True,
        "isEncrypted": False,
    }

    with pytest.raises(KeyError):
        MessageState.from_dict(incomplete_payload)


# Test for handling incorrect types
def test_message_state_from_dict_incorrect_types():
    incorrect_payload = {
        "id": 123,  # Should be a string
        "state": 42,  # Should be a string that can be converted to a ProcessState
        "recipients": "Alice, Bob",  # Should be a list of dictionaries
        "isHashed": "yes",  # Should be a boolean
        "isEncrypted": "no",  # Should be a boolean
    }

    with pytest.raises(
        Exception
    ):  # Replace Exception with the specific exception you expect
        MessageState.from_dict(incorrect_payload)


def test_webhook_from_dict():
    """
    Tests that a Webhook instance can be successfully instantiated from a dictionary
    representation of a webhook.
    """
    payload = {
        "id": "webhook_123",
        "url": "https://example.com/webhook",
        "event": "sms:received",
    }

    webhook = Webhook.from_dict(payload)

    assert webhook.id == payload["id"]
    assert webhook.url == payload["url"]
    assert webhook.event == WebhookEvent(payload["event"])


def test_webhook_asdict():
    """
    Tests that a Webhook instance can be successfully converted to a dictionary
    representation and that the fields match the expected values.

    This test ensures that the asdict method of the Webhook class returns a dictionary
    with the correct keys and values.
    """
    webhook = Webhook(
        id="webhook_123",
        url="https://example.com/webhook",
        event=WebhookEvent.SMS_RECEIVED,
    )

    expected_dict = {
        "id": "webhook_123",
        "url": "https://example.com/webhook",
        "event": "sms:received",
    }

    assert webhook.asdict() == expected_dict

    webhook = Webhook(
        id=None,
        url="https://example.com/webhook",
        event=WebhookEvent.SMS_RECEIVED,
    )

    expected_dict = {
        "id": None,
        "url": "https://example.com/webhook",
        "event": "sms:received",
    }

    assert webhook.asdict() == expected_dict


@pytest.mark.parametrize(
    "message_content,phone_numbers,with_delivery_report,is_encrypted,id,ttl,sim_number,priority,expected",
    [
        (
            "Hello, world!",
            ["123", "456"],
            True,
            False,
            "msg_123",
            300,
            1,
            MessagePriority.BYPASS_THRESHOLD,
            {
                "message": "Hello, world!",
                "phoneNumbers": ["123", "456"],
                "withDeliveryReport": True,
                "isEncrypted": False,
                "id": "msg_123",
                "ttl": 300,
                "simNumber": 1,
                "priority": 100,
            },
        ),
        (
            "Hello, world!",
            ["123", "456"],
            True,
            False,
            None,
            None,
            None,
            None,
            {
                "message": "Hello, world!",
                "phoneNumbers": ["123", "456"],
                "withDeliveryReport": True,
                "isEncrypted": False,
            },
        ),
        (
            "Hello, world!",
            ["123", "456"],
            True,
            False,
            "msg_123",
            None,
            1,
            None,
            {
                "message": "Hello, world!",
                "phoneNumbers": ["123", "456"],
                "withDeliveryReport": True,
                "isEncrypted": False,
                "id": "msg_123",
                "simNumber": 1,
            },
        ),
        (
            "Hello, world!",
            ["123", "456"],
            True,
            False,
            "msg_123",
            None,
            None,
            MessagePriority.DEFAULT,
            {
                "message": "Hello, world!",
                "phoneNumbers": ["123", "456"],
                "withDeliveryReport": True,
                "isEncrypted": False,
                "id": "msg_123",
                "priority": 0,
            },
        ),
        (
            "Hi",
            ["555"],
            True,
            False,
            None,
            None,
            None,
            MessagePriority.MINIMUM,
            {
                "message": "Hi",
                "phoneNumbers": ["555"],
                "withDeliveryReport": True,
                "isEncrypted": False,
                "priority": -128,
            },
        ),
    ],
)
def test_message_asdict(
    message_content,
    phone_numbers,
    with_delivery_report,
    is_encrypted,
    id,
    ttl,
    sim_number,
    priority,
    expected,
):
    """
    Tests that a Message instance can be successfully converted to a dictionary
    representation with camelCase keys and that only non-None fields are included.
    Uses parametrized testing to cover multiple scenarios.
    """
    message = Message(
        message=message_content,
        phone_numbers=phone_numbers,
        with_delivery_report=with_delivery_report,
        is_encrypted=is_encrypted,
        id=id,
        ttl=ttl,
        sim_number=sim_number,
        priority=priority,
    )

    assert message.asdict() == expected
