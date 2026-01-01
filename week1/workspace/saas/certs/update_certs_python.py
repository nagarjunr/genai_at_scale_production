"""
Find certificate (SSL) in python and copy certs from Bosch and append in this certificate from python
Goal: fix issue with SSL CERTIFICATES using proxy

# Local Bosch proxy
http_proxy=http://rb-proxy-de.bosch.com:8080
https_proxy=http://rb-proxy-de.bosch.com:8080

# OpenShift Server Bosch
HTTP_PROXY=http://rb-proxy-emea.internal.bosch.cloud:8080
HTTPS_PROXY=http://rb-proxy-emea.internal.bosch.cloud:8080
NO_PROXY=127.0.0.1,localhost,.cluster.local,.svc,.internal.bosch.cloud,.inside.bosch.cloud,.bgn,.de.bosch.com,.bosch.com,.bicadm.com,.bosch-iot-cloud.com,172.30.0.0/16,10.128.0.0/14,192.168.0.0/16,10.140.0.0/17,10.140.128.0/17,10.143.0.0/17,10.140.250.30,10.140.241.30,10.140.233.30,10.143.57.30
http_proxy=http://rb-proxy-emea.internal.bosch.cloud:8080
https_proxy=http://rb-proxy-emea.internal.bosch.cloud:8080
no_proxy=127.0.0.1,localhost,.cluster.local,.svc,.internal.bosch.cloud,.inside.bosch.cloud,.bgn,.de.bosch.com,.bosch.com,.bicadm.com,.bosch-iot-cloud.com,172.30.0.0/16,10.128.0.0/14,192.168.0.0/16,10.140.0.0/17,10.140.128.0/17,10.143.0.0/17,10.140.250.30,10.140.241.30,10.140.233.30,10.143.57.30

# Rancher Server Bosch
http_proxy=http://rb-proxy-sl.bosch.com:8080
https_proxy=http://rb-proxy-sl.bosch.com:8080
no_proxy=127.0.0.1,localhost,.cluster.local,.svc,.internal.bosch.cloud,.bgn,.de.bosch.com,.bosch.com,.bicadm.com,.bosch-iot-cloud.com,172.30.0.0/16,10.128.0.0/14,192.168.0.0/16,10.140.0.0/17,10.140.128.0/17,10.143.0.0/17,10.140.250.30,10.140.241.30,10.140.233.30,10.143.57.30
"""

import certifi
import os

def append_certs(source, destination):
    # Open the source file in read mode
    with open(source, 'r') as source_file:
        # Read the contents of the source file
        source_text = source_file.read()

    # Open the destination file in append mode
    with open(destination, 'a') as destination_file:
        # Append the contents of the source file to the destination file
        destination_file.write(source_text)

def append_certs_from_text(destination):

    source_text = """-----BEGIN CERTIFICATE-----
MIIE+jCCA+KgAwIBAgIEQwG2sjANBgkqhkiG9w0BAQUFADBQMRMwEQYKCZImiZPy
LGQBGRYDY29tMRUwEwYKCZImiZPyLGQBGRYFQm9zY2gxDDAKBgNVBAMTA1BLSTEU
MBIGA1UEAxMLQm9zY2gtQ0EtREUwHhcNMDUwODE2MDkxOTQyWhcNMjUwODE2MDk0
OTQyWjBQMRMwEQYKCZImiZPyLGQBGRYDY29tMRUwEwYKCZImiZPyLGQBGRYFQm9z
Y2gxDDAKBgNVBAMTA1BLSTEUMBIGA1UEAxMLQm9zY2gtQ0EtREUwggEiMA0GCSqG
SIb3DQEBAQUAA4IBDwAwggEKAoIBAQDADDavsLqpxKnP+mABiNavAOpR8EK4o7E1
NxRj//V6gVHdLw9EnRY+CeX6KAf6CjW3X+VRzQMZOMxcj4Hn9T2/hvApgjr4asLH
duTYlNlSPBLH1c0rDBJRj4SllBtkHx4g7eelVWzWT4k2vIgxNtwAR0x+dghgObQB
MGnPYGsERYQ62JU4c3Z3yNVOOCtSh+3J9m+8zMSvPKKpiqK4D5QfhMjJDvOAgJRz
kQLnJHTATLhF5Jp0phWUHJGeChwoncbhYX13AnEpqccGrid+ZdKYIFDs/I8t505V
TzvQ8O0yMkYc1RLIfXMsDeullW+00lmlFylcqXXMStOMhyYii4XXAgMBAAGjggHa
MIIB1jARBglghkgBhvhCAQEEBAMCAAcwggEYBgNVHR8EggEPMIIBCzBnoGWgY6Rh
MF8xEzARBgoJkiaJk/IsZAEZFgNjb20xFTATBgoJkiaJk/IsZAEZFgVCb3NjaDEM
MAoGA1UEAxMDUEtJMRQwEgYDVQQDEwtCb3NjaC1DQS1ERTENMAsGA1UEAxMEQ1JM
MTCBn6CBnKCBmYZVbGRhcDovL2Jvc2NoLmNvbS9jbj1Cb3NjaC1DQS1ERSxjbj1Q
S0ksZGM9Qm9zY2gsZGM9Y29tP2NlcnRpZmljYXRlUmV2b2NhdGlvbkxpc3Q/YmFz
ZYZAaHR0cDovL3RydXN0Y2VudGVyLmJvc2NoLmNvbS9DUkwvYm9zY2gtY2EtZGVf
cGtpX2NvbV9jcmxmaWxlLmNybDArBgNVHRAEJDAigA8yMDA1MDgxNjA5MTk0MlqB
DzIwMjUwODE2MDk0OTQyWjALBgNVHQ8EBAMCAQYwHwYDVR0jBBgwFoAUHqU/IqII
IRvFWCjRHy3w8/j5FSkwHQYDVR0OBBYEFB6lPyKiCCEbxVgo0R8t8PP4+RUpMAwG
A1UdEwQFMAMBAf8wHQYJKoZIhvZ9B0EABBAwDhsIVjcuMTo0LjADAgSQMA0GCSqG
SIb3DQEBBQUAA4IBAQBkQ/eOR9L4eenoIddXw7SjnJDnfsgZIaJNsnJ8afxgJjvo
t/U6AjnmPo7Waa5gyEIS9EEEmAubTwU30NyhHCr8iHjFDWhbSa9Waajb81i6Wgkl
pjM6T1D+RuEO1Ty6sWgPsfx3bZLITQyoXr33nRokVmKshjwtEU05BKRXgvk7ma9H
GCV1lOtwdjHKcK17mE2FHGbFNm/o6P9CkN4P3jdmpWKSb7915Cz9wdNPOl0IBcSl
wH7j3D8YEfbkrDkk2UYPccZUzMkPi6+WhlUmwkc0ea+Fa+pjGBsZ7AEfRCcVZaz3
fjluyBWjuWRa5bY3P86UdjQplcobWrovoIwehkyR
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIEtzCCA5+gAwIBAgIEQwHQujANBgkqhkiG9w0BAQsFADBQMRMwEQYKCZImiZPy
LGQBGRYDY29tMRUwEwYKCZImiZPyLGQBGRYFQm9zY2gxDDAKBgNVBAMTA1BLSTEU
MBIGA1UEAxMLQm9zY2gtQ0EtREUwHhcNMTUwNTEyMDk0ODEwWhcNMjUwNTEyMTAx
ODEwWjBRMRMwEQYKCZImiZPyLGQBGRYDY29tMRUwEwYKCZImiZPyLGQBGRYFQm9z
Y2gxDDAKBgNVBAMTA1BLSTEVMBMGA1UEAxMMQm9zY2gtQ0ExLURFMIIBIjANBgkq
hkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAoCSMNJfVszQGGIlreOUP8OJb6yE/zj38
G3JAqUvuj4t92nUZmtblwd2WDqSzhfyB3fOWlgL4l5Z3VyVR/YEEeUkrI4dHZxo4
ydKw2xsNhD3zg7zh2dZLx7HYmLD6P7A1O0KAvc6G4ZPEwhaVZ86G2XMy/Pd2qq0y
lpierOhhv+35TPOODxbT8p0IzrTszqJzaOmCHPWyvmP03mpgX8RNBZCc2g90DOiG
zRuTZbTbBXJrJWNJUNUrpw8CcGdXNoW/7U1XmazncyWZCSBKDtKRGzXHAqyDkxI6
wMMv52f1uL1RTVpg1cVN59QRwdROyOmTtERX41CjvY73sl9Qo4q3XwIDAQABo4IB
ljCCAZIwggEYBgNVHR8EggEPMIIBCzBnoGWgY6RhMF8xEzARBgoJkiaJk/IsZAEZ
FgNjb20xFTATBgoJkiaJk/IsZAEZFgVCb3NjaDEMMAoGA1UEAxMDUEtJMRQwEgYD
VQQDEwtCb3NjaC1DQS1ERTENMAsGA1UEAxMEQ1JMMTCBn6CBnKCBmYZVbGRhcDov
L2Jvc2NoLmNvbS9jbj1Cb3NjaC1DQS1ERSxjbj1QS0ksZGM9Qm9zY2gsZGM9Y29t
P2NlcnRpZmljYXRlUmV2b2NhdGlvbkxpc3Q/YmFzZYZAaHR0cDovL3RydXN0Y2Vu
dGVyLmJvc2NoLmNvbS9DUkwvYm9zY2gtY2EtZGVfcGtpX2NvbV9jcmxmaWxlLmNy
bDALBgNVHQ8EBAMCAQYwHwYDVR0jBBgwFoAUHqU/IqIIIRvFWCjRHy3w8/j5FSkw
HQYDVR0OBBYEFN4E4syJCP11jNikMDHYEG3lofSbMAwGA1UdEwQFMAMBAf8wGQYJ
KoZIhvZ9B0EABAwwChsEVjguMQMCAIEwDQYJKoZIhvcNAQELBQADggEBAEhM5mk5
bcNMPvYrtYOrlmHl4d/N6DgULfENn2ePhuz45sXH7Miex2KxiXJyPmuWwyMOtL6E
0oEI9Wwv8nIiB6VNvt8deSXmbaJ+yqfC/RhHtOTnT2igd1VdMuZlXgCPJ5dSYpde
H5CQr0OIeFTqwt2Q96PiAGiV6aoPRJWvN3sX5mocC+BxC1xExVz6uQAOsLanK0P3
RemoOXYjlF2c1J9WmjsWw/nMdrI0EgGIcGGZU+GAxQKOPE0a4wZMLvgCqoBOsAoj
fMQANsGiiE6VoeZ+e6sYcdTbUgCBdhjPi+eCpqlhaJOjZ1E+6qFpkM2ni1eEFjOq
6cBhN9cvOjqptek=
-----END CERTIFICATE-----
"""
    # Open the destination file in append mode
    with open(destination, 'a') as destination_file:
        # Append the contents of the source file to the destination file
        destination_file.write(source_text)

def init(source_certs = "."):
    """
    source_certs = folder where are certificates from ssl
    """
    print("Certificate from python: {}".format(certifi.where()))
    destination_cert_python = certifi.where() # find where is certifi from python

    # option 1
    append_certs_from_text(destination_cert_python)
    print("Certificates appended successfully.")

    # option 2
    # Iterate through the files and filter those that end with ".crt" and "pem.cer"
    # crt_file_paths = [os.path.join(source_certs, file_name) for file_name in os.listdir(source_certs) if (file_name.endswith('.crt') or file_name.endswith('pem.cer'))]

    # for source_cert in crt_file_paths:
    #     append_certs(source_cert, destination_cert_python)

    # if len(crt_file_paths) <= 0:
    #     print("Error - Missing certificates.")
    # else:
    #     print("Certificates appended successfully.")

if __name__ == "__main__":
    init()