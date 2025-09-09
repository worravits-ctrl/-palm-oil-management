import requests
import sys

# ทดสอบการเข้าสู่ระบบและส่งออก CSV
session = requests.Session()

# Login first
login_data = {
    'username': 'admin',
    'password': 'admin123',
    'submit': 'เข้าสู่ระบบ'
}

try:
    # Login
    login_response = session.post('http://127.0.0.1:8000/login', data=login_data)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        # Test income export
        export_response = session.get('http://127.0.0.1:8000/income/export')
        print(f"Income export status: {export_response.status_code}")
        
        if export_response.status_code == 200:
            print(f"Content-Type: {export_response.headers.get('Content-Type')}")
            print(f"Content-Length: {export_response.headers.get('Content-Length')}")
            print("CSV Export successful!")
            
            # Save to file to test
            with open('test_export.csv', 'wb') as f:
                f.write(export_response.content)
            print("CSV saved as test_export.csv")
        else:
            print(f"Export failed: {export_response.text}")
    else:
        print("Login failed")
        
except Exception as e:
    print(f"Error: {e}")
