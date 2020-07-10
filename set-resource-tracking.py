import os
import sys
import requests
import json
import urllib
from datetime import datetime

# Initialize CSV
api_token = os.environ.get('ACCOUNT_TOKEN')


class Samanage:
    def __init__(self, api_token):
        self.base_url = 'https://api.samanage.com/'
        self.default_headers = {
            'X-Samanage-Authorization': f"Bearer {api_token}",
            'Content-Type': 'application/json',
            'Accept': 'Accept: application/vnd.samanage.v2.1+json'
        }
        self.default_params = {'updated[]': 1}
        self.initialize()
        self.resource_dict = {
            'Administrative': 'Training and Administrative',
            'Forms Related': 'Training and Administrative',
            'General Issues': 'Training and Administrative',
            'Invoices/Contracts': 'Training and Administrative',
            'Project, IT Goverance': 'Training and Administrative',
            'Project, Non-IT Governance': 'Training and Administrative',
            'Rounding': 'Training and Administrative',
            'Training, (Self) ': 'Training and Administrative',
            'Training, Others in I.S.S': 'Training and Administrative',
            'Documentation, Publishing, Versioning and Security': 'Training and Administrative',
            'Issue, Phones and Voice Hardware': 'Ticket/Break fix ',
            'Issue, Clinical Application': 'Ticket/Break fix ',
            'Issue, Copier/Printer Hardware': 'Ticket/Break fix ',
            'Issue, Hardware and Peripheral': 'Ticket/Break fix ',
            'Issue, Financial Application': 'Ticket/Break fix ',
            'Issue, Network Cabling': 'Ticket/Break fix ',
            'Issue, Non-Clinical Application': 'Ticket/Break fix ',
            'Issue, PACS/CPACS': 'Ticket/Break fix ',
            'Issue, Restore Data (Backup)': 'Ticket/Break fix ',
            'Issue, Supply Chain Applications': 'Ticket/Break fix ',
            'Issue, User Profile and Login': 'Ticket/Break fix ',
            'Issue, Virus/Phishing/Spam': 'Ticket/Break fix ',
            'Issue, Website': 'Ticket/Break fix ',
            'Issue, Provider Access': 'Ticket/Break fix ',
            'Issue, User Access': 'Ticket/Break fix ',
            'Modify, Employee/Contractor Access': 'Ticket/Break fix ',
            'Modify, Provider & Access': 'Ticket/Break fix ',
            'New, Employee/Contractor': 'Ticket/Break fix ',
            'New, Provider': 'Ticket/Break fix ',
            'Reinstate, Employee/Contractor Access': 'Ticket/Break fix ',
            'Reinstate, Provider Access': 'Ticket/Break fix ',
            'Suspend, Employee/Contractor Access': 'Ticket/Break fix ',
            'Suspend, Provider Access': 'Ticket/Break fix ',
            'Terminate, Employee/Contractor Access': 'Ticket/Break fix ',
            'Terminate, Provider Access': 'Ticket/Break fix ',
            'Unscheduled Downtime and Recovery': 'Ticket/Break fix ',
            'Training, Phone and Voice Hardware': 'Issue',
            'Training, Copier/Printer Hardware': 'Issue',
            'Training, Hardware and Peripheral': 'Issue',
            'Training, Financial Application': 'Issue',
            'Training, Non-Clinical Application': 'Issue',
            'Training, Non-Clinical Application': 'Issue',
            'Training, PACS/CPACS': 'Issue',
            'Training, Supply Chain Applications': 'Issue',
            'Optimization, Clinical Application': 'Issue',
            'Optimization, Financial Application': 'Issue',
            'Optimization, Non-Clinical Application': 'Issue',
            'Optimization, PACS/CPACS': 'Issue',
            'Optimization, Supply Chain Application': 'Issue',
            'Optimization, User Profile and Login': 'Issue',
            'ISS After Action Reviews and Reports': 'Innovation and Process Improvement',
            'ISS SBARs': 'Innovation and Process Improvement',
            'ISS Continuous Improvement Initiatives': 'Innovation and Process Improvement',
            'Non-ISS Contiuous Improvement/Quality': 'Innovation and Process Improvement',
            'Other Post Mortem Reviews': 'Innovation and Process Improvement',
            'Lessons Learned': 'Innovation and Process Improvement',
            'Documentation, Authoring': 'Innovation and Process Improvement',
            'Documentation, Review': 'Innovation and Process Improvement',
            'Pilots and Trials': 'Innovation and Process Improvement',
            'Purchase, Clinical Application (New)': 'Task',
            'Purchase, Hardware and Peripheral (New)': 'Task',
            'Purchase, Financial Application (New)': 'Task',
            'Purchase, Mobile Device (New)': 'Task',
            'Purchase, Network Cabling (New)': 'Task',
            'Purchase, Non-Clinical Application (New)': 'Task',
            'Purchase, Supply Chain Application (New)': 'Task',
            'Upgrade, Clinical Application (New)': 'Task',
            'Upgrade, Hardware and Peripheral (Existing)': 'Task',
            'Upgrade, Financial Application (Existing)': 'Task',
            'Upgrade, Mobile Device (Existing)': 'Task',
            'Upgrade, Network Cabling (Existing)': 'Task',
            'Upgrade, Non-Clinical Application (Existing)': 'Task',
            'Upgrade, Supply Chain Applications (Existing)': 'Task',
            'Move, Desktop Hardware': 'Task',
            'Move, Network Cabling Location': 'Task',
            'Move, Printer/Copier': 'Task',
            'Maintenance, Clinical Application': 'Task',
            'Maintenance, Finiancial Application': 'Task',
            'Maintenance, Infrastructure': 'Task',
            'Maintenance, Interface': 'Task',
            'Maintenance, Non-Clinical Application': 'Task',
            'Maintenance, Storage & Backup': 'Task',
            'Maintenance, Supply Chain Application': 'Task'
        }

    # Validate API credentials
    def initialize(self):
        initialize_path = 'api.json?per_page=100'
        api_call = requests.get(
            self.base_url + initialize_path, headers=self.default_headers)
        if api_call.status_code > 201:
            print("Invalid Credentials")
            print(
                "Please enter 'python set-resource-tracking.py api-token")
            quit()
        else:
            print("Authentication successful")

    def get_incidents(self, page=1, incidents=[]):
        path = 'incidents.json?'
        self.default_params['page'] = page
        url = self.base_url + path + \
            urllib.parse.urlencode(self.default_params, encoding='utf-8')
        print(url)
        api_request = requests.get(url, headers=self.default_headers)
        incidents += api_request.json()
        if int(api_request.headers['X-Total-Pages']) == page:
            return incidents
        else:
            return self.get_incidents(page=page+1, incidents=incidents)

    def update_incidents(self):
        incidents = self.get_incidents()
        for incident in incidents:
            resource = None
            subcategory = None
            category = None
            # Check for issues or no match
            try:
                category = incident['category']['name']
                subcategory = incident['subcategory']['name']
                resource = self.resource_dict[subcategory]
            except (TypeError, KeyError):
                print(
                    f"No Match -- Subcategory: '{subcategory}' Resolved Resource: '{resource}'"
                )
                next
            if category == 'Import':
                print(f"Category was '{category}' skipping")
                next
            if resource == None:
                print(
                    f"No Match -- Subcategory: '{subcategory}' Resolved Resource: '{resource}'"
                )
                next
            # If nothing fails update
            else:
                print(
                    f"Updating Incident #{incident['number']} to '{resource}' https://app.samanage.com/incidents/{incident['id']}")
                payload = {'incident':
                           {'custom_fields_values': {
                               'custom_fields_value': [{'name': 'Resource Tracking (Executive)', 'value': resource}]
                           }}}
                api_request = requests.put(
                    self.base_url + f"incidents/{incident['id']}.json", json=payload, headers=self.default_headers)


api_controller = Samanage(api_token)
api_controller.update_incidents()
