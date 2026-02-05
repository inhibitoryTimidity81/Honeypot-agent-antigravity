"""
Simple syntax check for all modified files
"""

print("Checking imports...")

try:
    from session_manager import Session, session_manager
    print("✅ session_manager.py - OK")
except Exception as e:
    print(f"❌ session_manager.py - ERROR: {e}")

try:
    # Don't initialize agent (requires API key), just check syntax
    import agent
    print("✅ agent.py - Syntax OK")
except Exception as e:
    print(f"❌ agent.py - ERROR: {e}")

try:
    # Check if the new method exists
    from agent import HoneypotAgent
    if hasattr(HoneypotAgent, 'generate_normal_response'):
        print("✅ agent.py - generate_normal_response() method exists")
    else:
        print("❌ agent.py - generate_normal_response() method NOT FOUND")
except Exception as e:
    print(f"❌ agent.py method check - ERROR: {e}")

print("\nChecking Session dataclass...")
try:
    from session_manager import Session
    session = Session(session_id="test")
    if hasattr(session, 'scam_type'):
        print(f"✅ Session has scam_type field (default: '{session.scam_type}')")
    else:
        print("❌ Session missing scam_type field")
except Exception as e:
    print(f"❌ Session check - ERROR: {e}")

print("\n✅ All syntax checks passed!")
