import requests
import pytest

# Define the base URL of the running application
# This might need to be configured externally in a real CI environment
BASE_URL = "http://localhost:8000" 

def test_homepage_loads_and_contains_key_elements():
    """
    Tests if the homepage loads correctly (status 200) and contains key static text elements.
    """
    try:
        response = requests.get(BASE_URL + "/")
    except requests.exceptions.ConnectionError as e:
        pytest.fail(f"Connection to {BASE_URL} failed. Ensure the application is running. Error: {e}")
        return

    # Check 1: Status code
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    response_text = response.text

    # Check 2: Key content assertions
    key_elements_and_placeholders = [
        "Sujal's Guestbook",          # Site Title
        'placeholder="Your Name"',    # Name input placeholder
        'placeholder="Leave a message..."', # Message textarea placeholder
        "Recent Messages",            # Heading for the messages section
        # Consider adding checks for ARIA labels added in previous tasks if they are static
        'aria_label="Your Name"',
        'aria_label="Your Message"',
        'aria_label="Send your message"',
        'aria_label="Toggle website theme between light and dark modes"',
        'aria_label="Refresh messages"'
    ]

    for element_text in key_elements_and_placeholders:
        assert element_text in response_text, f"Expected to find '{element_text}' in homepage HTML."

    # Check 3: Ensure the "Load More Messages" button is present if messages exist,
    # or "No messages yet" if none (this is harder without knowing db state).
    # For a basic test, we'll just ensure some message-related container is there.
    # This test assumes the initial page load might have messages or the "no messages" state.
    assert ('id="message-list-items"' in response_text), "Expected to find the message list container."

if __name__ == "__main__":
    # This allows running the test directly with `python tests/test_frontend.py`
    # For more comprehensive test discovery and execution, use `pytest`.
    pytest.main([__file__])
