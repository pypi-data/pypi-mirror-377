import json
import requests

#from osdu_perf.core.sample import Auth

from sample import Auth
def adduser(host, token, users, email, role, partition):
    url = "https://{}/api/entitlements/v2/groups/{}/members".format(host, users)

    payload = json.dumps({
      "email":  email,
      "role": role
    })
    headers = {
      'data-partition-id': partition,
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + token
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print("AddUser result", response.text, "addUserStatusCode=", response.status_code , "For User", users)


def getgroups(token, users, partition, host):
    url = "https://{}/api/entitlements/v2/groups".format(host)

    #url = "https://ankur44.oep.ppe.azure-int.net/api/entitlements/v2/groups"


    #janraj 04eff046-d35f-452e-a297-65b5bda1d274
    #slb app b04bba7b-4c67-404f-9fbc-34b4276d299e
    payload = {}
    headers = {
      #'data-partition-id': 'digital2020-31535118-e607-11ee',
      'data-partition-id': partition,
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + token
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print("Got the user groups", response.text, "addUserStatusCode=", response.status_code , "For User", users)

def getuserGroup(host, token, users, email, role, partition):
    url = "https://{}/api/entitlements/v2/members/{}/groups?type=none".format(host, email)

    #url = "https://ankur44.oep.ppe.azure-int.net/api/entitlements/v2/groups"


    #janraj 04eff046-d35f-452e-a297-65b5bda1d274
    #slb app b04bba7b-4c67-404f-9fbc-34b4276d299e
    payload = {}
    headers = {
      #'data-partition-id': 'digital2020-31535118-e607-11ee',
      'data-partition-id': partition,
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + token
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print("Got the user groups", response.text, "addUserStatusCode=", response.status_code , "For User", users)



if __name__ == "__main__":
  email = "04eff046-d35f-452e-a297-65b5bda1d274"
  #email = "93d605368c784ec599525030af7fc895"
  #from auth import AzureTokenManager
  #token_manager = AzureTokenManager(client_id="2f59abbc-7b40-4d0e-91b2-22ca3084bc84", use_managed_identity=False)
  #token = token_manager.get_access_token("https://management.azure.com/.default") 
  #email = "51d2f791-795b-4c8d-9657-cd23b1f9f2a7"
  authT = Auth.get_instance(client_id="2f59abbc-7b40-4d0e-91b2-22ca3084bc84")
  token = authT.get_bearer_token()
  print(f"Access Token: {token}")
  #token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IkpZaEFjVFBNWl9MWDZEQmxPV1E3SG4wTmVYRSIsImtpZCI6IkpZaEFjVFBNWl9MWDZEQmxPV1E3SG4wTmVYRSJ9.eyJhdWQiOiIyZjU5YWJiYy03YjQwLTRkMGUtOTFiMi0yMmNhMzA4NGJjODQiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC83MmY5ODhiZi04NmYxLTQxYWYtOTFhYi0yZDdjZDAxMWRiNDcvIiwiaWF0IjoxNzU2NzE1MDc1LCJuYmYiOjE3NTY3MTUwNzUsImV4cCI6MTc1NjcxOTg2NSwiYWNyIjoiMSIsImFpbyI6IkFjUUFPLzhaQUFBQVIyNmZwcEdacHVFcmZ3eFhKTExjeE8xNk1GeFpna0p2UTF0bnZPUUQxNlh1cHVOeTc5ODRzY3B6YWlYanNqMm93ZFB6bmhOemhKVTZEYlk0TnF3L2hTYTVnOTJCWHBpR1NHakVXWENSUnRtaHRoMHhSK1NLVS82NnR5RXpYa3pmVVRFS3JaNlRkbVpUTlBJVmM2ODI2ZGw4MzkzT0gybTc3NFdUbkhqZ2JnSFJGN2pwS0ZHcm9PSlUwWkF5V1FIcTZNT3M5TE5KcnVwZzBUS0ZvM1Vxc2ltNWkwbzc0R3JaTFYwZTJxR3M1dkNvNFN1TG5TK1ZjczRNZUR5bmIrdWwiLCJhbXIiOlsicnNhIiwibWZhIl0sImFwcGlkIjoiMDRiMDc3OTUtOGRkYi00NjFhLWJiZWUtMDJmOWUxYmY3YjQ2IiwiYXBwaWRhY3IiOiIwIiwiZGV2aWNlaWQiOiJlNmUyOTg4My1iNGE2LTRjMzYtODcwYi04YzU2ODRkYjRkOWUiLCJmYW1pbHlfbmFtZSI6IkNKIiwiZ2l2ZW5fbmFtZSI6IkphbnJhaiIsImlwYWRkciI6IjEwMy4xNjAuMjMzLjE3MyIsIm5hbWUiOiJKYW5yYWogQ0oiLCJvaWQiOiIwNGVmZjA0Ni1kMzVmLTQ1MmUtYTI5Ny02NWI1YmRhMWQyNzQiLCJvbnByZW1fc2lkIjoiUy0xLTUtMjEtMjEyNzUyMTE4NC0xNjA0MDEyOTIwLTE4ODc5Mjc1MjctNTczNzgwNzYiLCJwd2RfdXJsIjoiaHR0cHM6Ly9wb3J0YWwubWljcm9zb2Z0b25saW5lLmNvbS9DaGFuZ2VQYXNzd29yZC5hc3B4IiwicmgiOiIxLkFSb0F2NGo1Y3ZHR3IwR1JxeTE4MEJIYlI3eXJXUzlBZXc1TmtiSWl5akNFdklRYUFPZ2FBQS4iLCJzY3AiOiJ0ZXN0Iiwic2lkIjoiNDgwOGMxNWUtOWUwYy00YTI3LTg5NGEtYTg4MjA0ZjRmN2JjIiwic3ViIjoidlI1SWNVNXNjX2tTY0luM1JIOUFQYXFvZmpmVlJuaU5EMl84cHdwUXd6NCIsInRpZCI6IjcyZjk4OGJmLTg2ZjEtNDFhZi05MWFiLTJkN2NkMDExZGI0NyIsInVuaXF1ZV9uYW1lIjoiamFucmFqY2pAbWljcm9zb2Z0LmNvbSIsInVwbiI6ImphbnJhamNqQG1pY3Jvc29mdC5jb20iLCJ1dGkiOiJzNEVwaGpacUFFQ0lDZUhZdFFodUFBIiwidmVyIjoiMS4wIiwieG1zX2Z0ZCI6ImpYN01heEZfdi1SMnRNYjFZTC1xWTRWcDhuQWhKeGg1MEJpclpkX25peG9CWVhOcFlYTnZkWFJvWldGemRDMWtjMjF6In0.e80nt6eQ7kN4ihMD6aXyeNV_xXpdnNY1sUTzA3bkSqLH-_FiYUJepuF5uQ068WNQn3d5_MT7OTOuMJ3__T1W3jicftp62rZhhUT_-zA0JryfyLszlDeshB_fGKb26hW74Q0r7rhhQG8VrTdm0G5XaUZvqrTpE9Eqd85TOQAJ7PlXF2Xux1kiSZri46lB5iulVJhd0CW4z9e8JRBLuFNVRtOTrYZEwIQKUlWCRLRyxNMRSXkqZQMf3-_47b-X--HO2uMuknNNTsl-gD_chHNo903-JEMsp1k-A6xHIU8r4MAU_oxcuFje6_lM50fyWI0LB-4r0LlnCmjYobqcGHKrGg"
  #print(f"Access Token: {token}")
  #host = "slbadmedev.energy.azure.com"

  partition = "dev"
  role = "OWNER"
  host = "perfinst.energy.azure.com"
  users = "users@{}.dataservices.energy".format(partition)
  email = "04eff046-d35f-452e-a297-65b5bda1d274"
  
  getuserGroup(host, token, users, email, role, partition)
  '''
  adduser(host, token, users, email, role, partition)

  email = "04eff046-d35f-452e-a297-65b5bda1d274"
  users = "users@{}.dataservices.energy".format(partition)
  adduser(host, token, users, email, role, partition)

  email = "04eff046-d35f-452e-a297-65b5bda1d274"
  users = "users@{}.dataservices.energy".format(partition)
  adduser(host, token, users, email, role, partition)
  '''
  '''
  users = "users.datalake.ops@{}.dataservices.energy".format(partition)
  adduser(host, token, users, email, role, partition)
  users = "service.legal.editor@{}.dataservices.energy".format(partition)
  adduser(host, token, users, email, role, partition)
  users = "data.default.owners@{}.dataservices.energy".format(partition)
  adduser(host, token, users, email, role, partition)
  getgroups(token, users, partition, host)
  '''