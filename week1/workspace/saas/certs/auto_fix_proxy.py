import requests
import os
import platform

# List of HTTP proxy URLs to test
proxy_list = {
    "local_proxy_de": {"http_proxy": "http://rb-proxy-de.bosch.com:8080", "https_proxy": "http://rb-proxy-de.bosch.com:8080", "no_proxy": "127.0.0.*,localhost,rb-omscloudasl4.server.bosch.com"},
    "local_proxy_br": {"http_proxy": "http://rb-proxy-br.bosch.com:8080", "https_proxy": "http://rb-proxy-br.bosch.com:8080", "no_proxy": "127.0.0.*,localhost,rb-omscloudasl4.server.bosch.com"},
    "openshift_proxy": {"http_proxy": "http://rb-proxy-emea.internal.bosch.cloud:8080", "https_proxy": "http://rb-proxy-emea.internal.bosch.cloud:8080", "no_proxy": "127.0.0.1,localhost,.cluster.local,.svc,.internal.bosch.cloud,.inside.bosch.cloud,.bgn,.de.bosch.com,.bosch.com,.bicadm.com,.bosch-iot-cloud.com,172.30.0.0/16,10.128.0.0/14,192.168.0.0/16,10.140.0.0/17,10.140.128.0/17,10.143.0.0/17,10.140.250.30,10.140.241.30,10.140.233.30,10.143.57.30"},
    "rancher_proxy": {"http_proxy": "http://rb-proxy-sl.bosch.com:8080", "https_proxy": "http://rb-proxy-sl.bosch.com:8080", "no_proxy": "127.0.0.1,localhost,.cluster.local,.svc,.internal.bosch.cloud,.bgn,.de.bosch.com,.bosch.com,.bicadm.com,.bosch-iot-cloud.com,172.30.0.0/16,10.128.0.0/14,192.168.0.0/16,10.140.0.0/17,10.140.128.0/17,10.143.0.0/17,10.140.250.30,10.140.241.30,10.140.233.30,10.143.57.30"},
    "ipz002_proxy": {"http_proxy": "http://rb-proxy-emea.internal.bosch.cloud:8080", "https_proxy": "http://rb-proxy-emea.internal.bosch.cloud:8080", "no_proxy": "127.0.0.1,localhost,.cluster.local,.svc,.internal.bosch.cloud,.inside.bosch.cloud,.bgn,.de.bosch.com,.bosch.com,.bicadm.com,.bosch-iot-cloud.com,172.30.0.0/16,10.128.0.0/14,192.168.0.0/16,10.140.0.0/17,10.140.128.0/17,10.143.0.0/17,10.140.250.30,10.140.241.30,10.140.233.30,10.143.57.30"},
}

def override_user_profile_proxy(http_proxy, https_proxy, no_proxy):
    # Get the current platform
    current_platform = platform.system()

    if current_platform == "Windows":
        # Handle Windows differently or skip if not applicable
        # print("Don't apply in public http_proxy, because running on Windows. Only apply proxy in terminal or current code")
        return

    # Get the user's home directory
    user_home = os.path.expanduser("~")

    # Define the path to the user's profile file (e.g., ~/.profile)
    profile_file_path = os.path.join(user_home, ".profile")

    # Create a temporary file to store the updated environment variables
    temp_file_path = os.path.join(user_home, "environment_temp")
    with open(temp_file_path, "w") as temp_file:
        with open(profile_file_path, "r") as profile_file:
            for line in profile_file:
                # Remove existing http_proxy, https_proxy, and no_proxy lines
                if line.startswith("export http_proxy=") or line.startswith("export https_proxy=") or line.startswith("export no_proxy=") or line.startswith("export HTTP_PROXY=") or line.startswith("export HTTPS_PROXY=") or line.startswith("export NO_PROXY="):
                    continue
                temp_file.write(line)

            # Add the new environment variable definitions
            temp_file.write("\n")
            temp_file.write(f'export http_proxy="{http_proxy}"\n')
            temp_file.write(f'export https_proxy="{https_proxy}"\n')
            temp_file.write(f'export no_proxy="{no_proxy}"\n')

    # Replace the original profile file with the updated one
    os.rename(temp_file_path, profile_file_path)

    # Print a message indicating that the profile file has been updated
    # print("Environment variables updated in user profile.")
    
# python -c 'import requests; print(requests.get("https://google.com/", proxies={"http": "http://10.143.16.65:8080", "https": "http://10.143.16.65:8080"}, timeout=5))'
# python -c 'import requests; print(requests.get("https://google.com/", proxies={"http": "http://10.143.0.177:8080/", "https": "http://10.143.0.177:8080/"}, timeout=5))'
# python -c 'import requests; print(requests.get("https://google.com/", proxies={"http": "http://rb-proxy-sl.bosch.com:8080/", "https": "http://rb-proxy-sl.bosch.com:8080/"}, timeout=5))'
# python -c 'import requests; print(requests.get("https://google.com/", proxies={"http": "http://rb-proxy-de.bosch.com:8080", "https": "http://rb-proxy-de.bosch.com:8080"}, timeout=5))'
# python -c 'import requests; print(requests.get("https://www.example.com/", proxies={"http": "http://rb-proxy-sl.bosch.com:8080/", "https": "http://rb-proxy-sl.bosch.com:8080/"}, timeout=5))'
# echo "http_proxy=$http_proxy, https_proxy=$https_proxy, no_proxy=$no_proxy"
# python -c 'import requests; print(requests.get("https://api.aleph-alpha.com/", headers={"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyMjQ1NiwidG9rZW5faWQiOjQ0OTV9.fSDcOLLC-6eKPfzzTI_6R2DW75yuA0LJ0OfAyd_38e8", "User-Agent": "Aleph-Alpha-Python-Client-1.16.0"}, timeout=5))'

# Function to test a proxy and return True if it's working
def test_proxy(http_proxy, https_proxy, no_proxy):
    try:
        response = requests.get("https://google.com/", proxies={"http": http_proxy, "https": https_proxy, "no_proxy": no_proxy}, timeout=5)
        # response = requests.get("https://www.example.com", proxies={"http": http_proxy, "https": https_proxy}, timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def init():
    # Iterate through the proxy list and find the first working proxy
    selected_proxy = None
    for proxy_url in proxy_list.values():
        if test_proxy(proxy_url.get("http_proxy"), proxy_url.get("https_proxy"), proxy_url.get("no_proxy")):
            selected_proxy = proxy_url
            break

    if selected_proxy:
        # Set the selected proxy as an environment variable
        os.environ["http_proxy"] = selected_proxy["http_proxy"]
        os.environ["https_proxy"] = selected_proxy["https_proxy"]
        os.environ["no_proxy"] = selected_proxy["no_proxy"]
        os.environ["HTTP_PROXY"] = selected_proxy["http_proxy"]
        os.environ["HTTPS_PROXY"] = selected_proxy["https_proxy"]
        os.environ["NO_PROXY"] = selected_proxy["no_proxy"]
        print(selected_proxy["http_proxy"])
        print(selected_proxy["https_proxy"])
        print(selected_proxy["no_proxy"])

        try:
            override_user_profile_proxy(selected_proxy["http_proxy"], selected_proxy["https_proxy"], selected_proxy["no_proxy"])
        except Exception:
            _
            # print("Proxy was not applied to the public variables, only to the current code and the current terminal session.\Get administrative rights and apply the mentioned variables.")
    else:
        print("")
        print("")
        print("")
    #     print("No working proxy found.")

if __name__ == "__main__":
    init()
