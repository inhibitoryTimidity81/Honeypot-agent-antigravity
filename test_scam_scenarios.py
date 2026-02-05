"""
Test Scam Scenarios
Comprehensive test suite for the honeypot API
"""
import requests
import json
from datetime import datetime
import time

# Configuration
BASE_URL = "http://localhost:8000"  # Change to your deployed URL for production testing
API_KEY = "your_custom_api_key_here"  # Change to your actual API key

HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}


def test_health_check():
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✅ Health check passed")


def test_bank_fraud_scenario():
    """Test bank fraud scam scenario"""
    print("\n=== Testing Bank Fraud Scenario ===")
    
    session_id = f"test-bank-fraud-{int(time.time())}"
    
    # Message 1: Initial scam message
    request1 = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "URGENT: Your bank account will be blocked in 2 hours due to suspicious activity. Verify immediately by calling 9876543210",
            "timestamp": datetime.now().isoformat()
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    response1 = requests.post(f"{BASE_URL}/api/honeypot", json=request1, headers=HEADERS)
    print(f"\nMessage 1 Response ({response1.status_code}):")
    result1 = response1.json()
    print(json.dumps(result1, indent=2))
    
    assert result1["scamDetected"] == True
    assert result1["agentResponse"] is not None
    print(f"Agent Response: {result1['agentResponse']}")
    
    # Message 2: Follow-up
    time.sleep(1)
    request2 = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "Please share your account number and UPI ID to verify your identity",
            "timestamp": datetime.now().isoformat()
        },
        "conversationHistory": [
            request1["message"],
            {"sender": "user", "text": result1["agentResponse"], "timestamp": datetime.now().isoformat()}
        ],
        "metadata": request1["metadata"]
    }
    
    response2 = requests.post(f"{BASE_URL}/api/honeypot", json=request2, headers=HEADERS)
    result2 = response2.json()
    print(f"\nMessage 2 Response ({response2.status_code}):")
    print(f"Agent Response: {result2['agentResponse']}")
    print(f"Extracted Intelligence: {json.dumps(result2['extractedIntelligence'], indent=2)}")
    
    print("✅ Bank fraud scenario test passed")


def test_upi_fraud_scenario():
    """Test UPI fraud scam scenario"""
    print("\n=== Testing UPI Fraud Scenario ===")
    
    session_id = f"test-upi-fraud-{int(time.time())}"
    
    request = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "You have received a wrong payment of Rs. 5000. Please refund to scammer@paytm immediately to avoid legal action.",
            "timestamp": datetime.now().isoformat()
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "WhatsApp",
            "language": "English",
            "locale": "IN"
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/honeypot", json=request, headers=HEADERS)
    result = response.json()
    
    print(f"Response ({response.status_code}):")
    print(f"Scam Detected: {result['scamDetected']}")
    print(f"Agent Response: {result['agentResponse']}")
    print(f"UPI IDs Found: {result['extractedIntelligence']['upiIds']}")
    
    assert result["scamDetected"] == True
    assert "scammer@paytm" in result['extractedIntelligence']['upiIds']
    print("✅ UPI fraud scenario test passed")


def test_phishing_link_scenario():
    """Test phishing link scenario"""
    print("\n=== Testing Phishing Link Scenario ===")
    
    session_id = f"test-phishing-{int(time.time())}"
    
    request = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "Your KYC is incomplete. Update now: http://fake-bank-kyc.com/update?id=12345 or your account will be suspended.",
            "timestamp": datetime.now().isoformat()
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "Email",
            "language": "English",
            "locale": "IN"
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/honeypot", json=request, headers=HEADERS)
    result = response.json()
    
    print(f"Response ({response.status_code}):")
    print(f"Scam Detected: {result['scamDetected']}")
    print(f"Agent Response: {result['agentResponse']}")
    print(f"Phishing Links: {result['extractedIntelligence']['phishingLinks']}")
    
    assert result["scamDetected"] == True
    assert len(result['extractedIntelligence']['phishingLinks']) > 0
    print("✅ Phishing link scenario test passed")


def test_document_request_scenario():
    """Test scenario where scammer requests documents"""
    print("\n=== Testing Document Request Scenario ===")
    
    session_id = f"test-doc-request-{int(time.time())}"
    
    # Initial message
    request1 = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "This is your bank. We need to verify your account.",
            "timestamp": datetime.now().isoformat()
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    response1 = requests.post(f"{BASE_URL}/api/honeypot", json=request1, headers=HEADERS)
    result1 = response1.json()
    
    # Scammer asks for cancelled check
    time.sleep(1)
    request2 = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": "Please send a photo of your cancelled check for verification",
            "timestamp": datetime.now().isoformat()
        },
        "conversationHistory": [
            request1["message"],
            {"sender": "user", "text": result1["agentResponse"], "timestamp": datetime.now().isoformat()}
        ],
        "metadata": request1["metadata"]
    }
    
    response2 = requests.post(f"{BASE_URL}/api/honeypot", json=request2, headers=HEADERS)
    result2 = response2.json()
    
    print(f"Response to document request:")
    print(f"Agent Response: {result2['agentResponse']}")
    
    # Agent should stall and ask questions instead of providing document
    assert result2["agentResponse"] is not None
    print("✅ Document request scenario test passed")


def test_multi_turn_conversation():
    """Test extended multi-turn conversation"""
    print("\n=== Testing Multi-Turn Conversation ===")
    
    session_id = f"test-multi-turn-{int(time.time())}"
    conversation_history = []
    
    messages = [
        "Your account has been compromised. Call us immediately at 9999888877",
        "We need to verify your identity. What is your account number?",
        "Also provide your UPI ID registered with the bank",
        "Send payment of Rs 100 to verify@okaxis to unlock your account"
    ]
    
    for i, msg in enumerate(messages):
        request = {
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": msg,
                "timestamp": datetime.now().isoformat()
            },
            "conversationHistory": conversation_history.copy(),
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/honeypot", json=request, headers=HEADERS)
        result = response.json()
        
        print(f"\nTurn {i+1}:")
        print(f"Scammer: {msg}")
        print(f"Agent: {result['agentResponse']}")
        print(f"Total Messages: {result['engagementMetrics']['totalMessagesExchanged']}")
        
        # Update conversation history
        conversation_history.append(request["message"])
        if result["agentResponse"]:
            conversation_history.append({
                "sender": "user",
                "text": result["agentResponse"],
                "timestamp": datetime.now().isoformat()
            })
        
        time.sleep(1)
    
    print(f"\nFinal Intelligence Extracted:")
    print(json.dumps(result['extractedIntelligence'], indent=2))
    print(f"Agent Notes: {result['agentNotes']}")
    
    print("✅ Multi-turn conversation test passed")


def run_all_tests():
    """Run all test scenarios"""
    print("=" * 60)
    print("AGENTIC HONEYPOT API - TEST SUITE")
    print("=" * 60)
    
    try:
        test_health_check()
        test_bank_fraud_scenario()
        test_upi_fraud_scenario()
        test_phishing_link_scenario()
        test_document_request_scenario()
        test_multi_turn_conversation()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Cannot connect to {BASE_URL}")
        print("Make sure the server is running!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    print("Starting tests...")
    print(f"Target URL: {BASE_URL}")
    print(f"API Key: {API_KEY[:10]}...")
    
    run_all_tests()
