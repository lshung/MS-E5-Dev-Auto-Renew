import sys
import random
import string
from helpers import *


class ManageUsers():
    def __init__(self, access_token=""):
        self.access_token = access_token
    
    # Get current user count
    def get_user_count(self):
        response = call_api_get("https://graph.microsoft.com/v1.0/users", self.access_token)
        return len(response.json()["value"])
    
    # Get a random user (userPrincipalName)
    def get_random_user(self):
        response = call_api_get("https://graph.microsoft.com/v1.0/users", self.access_token)
        return random.choice([item.get("userPrincipalName") for item in response.json()["value"]])
    
    # Add a user with auto generated user's info
    def add_user(self, recursive_count=0):
        user = __class__.generate_random_name()
        domain = self.get_random_domain()
        data = {
            "accountEnabled": True,
            "displayName": user["displayName"],
            "givenName": user["givenName"],
            "surname": user["surname"],
            "mailNickname": user["mailNickname"],
            "mobilePhone": __class__.generate_random_phone_number(),
            "mail": user["userPrincipalName"] + "@" + domain,
            "userPrincipalName": user["userPrincipalName"] + "@" + domain,
            "preferredLanguage": "en",
            "passwordProfile": {
                "forceChangePasswordNextSignIn": True,
                "password": __class__.generate_password()
            }
        }
        response = call_api_post("https://graph.microsoft.com/v1.0/users", data, self.access_token)
        if response.status_code == 201:
            print(f"Success: Add user {data["userPrincipalName"]}")
        else:
            print(f"Error: Add user {data["userPrincipalName"]} {response.status_code} {response.text}")
            if recursive_count < 5:
                self.add_user(recursive_count + 1) # Recursively call this function until its success
    
    # Delete a user by id or userPrincipalName
    def delete_user_by_id(self, id):
        response = call_api_delete(f"https://graph.microsoft.com/v1.0/users/{id}", self.access_token)
        if response.status_code == 204:
            print(f"Sucess: Delete user {id}")
        else:
            print(f"Error: Delete user {id} {response.status_code} {response.text}")
    
    # Delete a user randomly
    def delete_a_random_user(self, recursive_count=0):
        user_id = self.get_random_user()
        if not self.check_user_role(user_id):
            self.delete_user_by_id(user_id)
        else:
            print(f"Error: Delete user {user_id} Cannot delete the Global Admin")
            if recursive_count < 5:
                self.delete_a_random_user(recursive_count + 1) # Recursively call this function until its success
    
    # Check if user is an Admin
    def check_user_role(self, id):
        response = call_api_get(f"https://graph.microsoft.com/v1.0/users/{id}/memberOf", self.access_token)
        is_admin = any(
            item.get("@odata.type") == "#microsoft.graph.directoryRole" and
            item.get("roleTemplateId") == "62e90394-69f5-4237-9190-012177145e10"
            for item in response.json()["value"]
        )
        return is_admin

    @staticmethod
    def generate_password(length=12):
        characters = string.ascii_letters + string.digits + string.punctuation
        password = "".join(random.choice(characters) for _ in range(length))
        return password

    @staticmethod
    def generate_random_name():
        first_names = ("James", "Robert", "John", "Michael", "David", "William", "Richard", "Joseph", "Thomas", "Christopher", "Charles", "Daniel", "Matthew", "Anthony", "Mark", "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Sandra", "Margaret")
        last_names = ("Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzales", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson")
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        return {
            "displayName": f"{first_name} {last_name}",
            "givenName": f"{first_name}",
            "surname": f"{last_name}",
            "mailNickname": f"{first_name}{last_name[:1]}",
            "userPrincipalName": f"{first_name}{last_name[:1]}".lower()
        }

    @staticmethod
    def generate_random_phone_number():
        first = "0" + random.choice(("3", "5", "8", "9"))
        second = str(random.randint(0, 999)).zfill(3)
        last = str(random.randint(0, 9999)).zfill(4)
        return f"{first}{second}{last}"

    def get_random_domain(self):
        response = call_api_get("https://graph.microsoft.com/v1.0/domains", self.access_token)
        return random.choice([item.get("id") for item in response.json()["value"]])

    # Main run
    def run(self):
        current_user_count = self.get_user_count()
        plan_to_add = random.randint(1, 10)
        plan_to_delete = random.randint(1, 10)
        user_count_midpoint = 10
        target_user_count = current_user_count + plan_to_add - plan_to_delete
        if target_user_count >= 0.5 * user_count_midpoint and target_user_count <= 1.5 * user_count_midpoint:
            print("Pre-process user count: {} users".format(current_user_count))
            print("Plan to add: {} users".format(plan_to_add))
            print("Plan to delete: {} users".format(plan_to_delete))
            print("Target user count: {} users".format(target_user_count))
            for _ in range(plan_to_add):
                self.add_user()
            for _ in range(plan_to_delete):
                self.delete_a_random_user()
            print(f"Post-process user count: {self.get_user_count()} users")
        else:
            self.run() # Recursively call this function until it meets the condition


if __name__ == "__main__":
    # For production
    users = ManageUsers(access_token=sys.argv[1])
    users.run()

    # For testing on local machine
    # from ms_tokens import MSTokens
    # mst = MSTokens(
    #     mode="dev",
    #     client_id="", # Manually enter
    #     client_secret="", # Manually enter
    #     tokens_file_name="tokens.txt" # The refresh token is in this file
    # )
    # users = ManageUsers(access_token=mst.get_access_token())
    # users.run()
