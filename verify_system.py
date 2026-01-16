import requests
import sys

BASE_URL = "http://127.0.0.1:5000"

def test_routes():
    print("Testing Routes...")
    
    # 1. Test Homepage
    try:
        response = requests.get(BASE_URL + "/")
        if response.status_code == 200:
            print("[OK] Homepage is reachable")
        else:
            print(f"[FAIL] Homepage failed with {response.status_code}")
    except Exception as e:
        print(f"[FAIL] Connection failed: {e}")
        return

    # 2. Test ML Analysis with dummy data (bypassing auth for simplicity check or mocking)
    # The current API requires session user_id. We can't easily mock session in a simple script 
    # without a login flow, but we can verify the ML engine imports directly.
    pass

def verify_modules():
    print("\nVerifying Modules Locally...")
    try:
        from ml_engine import analyzer
        print("[OK] ML Engine imported")
        
        test_msg = "I need to study calculus"
        pred = analyzer.predict(test_msg)
        print(f"   Prediction for '{test_msg}': {pred} (Expected: Study)")
        
        if pred == 'Study':
            print("[OK] ML Prediction Accuracy Check Passed")
        else:
            print("[FAIL] ML Prediction Accuracy Check Failed")
            
        from study_buddy import study_buddy
        print("[OK] Study Buddy imported")
        
        explanation = study_buddy.get_explanation("Python", "Basic")
        if "cookbook" in explanation['content']:
             print("[OK] Study Buddy Content Check Passed")
        else:
             print("[FAIL] Study Buddy Content Check Failed")

    except ImportError as e:
        print(f"[FAIL] Import Error: {e}")
    except Exception as e:
        print(f"[FAIL] Error during verification: {e}")


if __name__ == "__main__":
    test_routes()
    verify_modules()
