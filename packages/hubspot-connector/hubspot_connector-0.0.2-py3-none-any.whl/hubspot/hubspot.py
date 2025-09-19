import requests,logging,csv,os
from typing import Optional,List,Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HubSpotConnector:
    """
    A connector class to interact with the HubSpot API using OAuth 2.0 credentials.

    This class provides methods to access HubSpot CRM objects such as contacts, 
    manage authentication tokens, and make API requests.

    Attributes:
        client_id (str): HubSpot client ID used for OAuth authentication.
        client_secret (str): HubSpot client secret used for OAuth authentication.
        access_token (str): Access token for making API calls.
        refresh_token (str): Refresh token used to renew the access token.
        base_url (str): Base URL for HubSpot API endpoints.
        contact_url (str): API path for managing contacts.

    Example:
        connector = HubSpotConnector(
            client_id="your_client_id",
            client_secret="your_client_secret",
            access_token="your_access_token",
            refresh_token="your_refresh_token"
        )
    """
    def __init__(self, client_id: str, client_secret: str, access_token: str, refresh_token: str):
        """
        Initialize HubSpot connector with OAuth credentials.
        
        Args:
            client_id (str): HubSpot client ID
            client_secret (str): HubSpot client secret
            access_token (str): Access token for API calls
            refresh_token (str): Refresh token to renew access
        """
        try:
            self.client_id = client_id
            self.client_secret = client_secret
            self.access_token = access_token
            self.refresh_token = refresh_token
            self.base_url = "https://api.hubapi.com"
            self.contact_url = "/crm/v3/objects/contacts"         
            logger.info("HubSpotConnector initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize HubSpotConnector: {str(e)}")
            raise
    
    def get_all_leads(self) -> List:
        """
        Fetch all leads from the HubSpot account and log their details.

        Returns:
            List of leads as dictionaries.
        """
        try:
            leads = []
            url = f"{self.base_url}{self.contact_url}"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            while url:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

                results = data.get("results", [])
                leads.extend(results)

                # Log each lead
                # for lead in results:
                #     logger.info(f"Lead ID: {lead.get('id')}, Properties: {lead.get('properties')}")

                # Check for next page
                paging = data.get("paging", {})
                next_page = paging.get("next", {})
                url = next_page.get("link") if next_page else None

            logger.info(f"Total leads fetched: {len(leads)}")
            return leads

        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
        except Exception as e:
            logger.error(f"Error fetching leads: {e}")
            return []
        
    def create_lead(self, firstname: str, lastname: str, email: str, phone: str = None, additional_properties: dict = None) -> Dict:
        """
        Create a new lead (contact) in HubSpot CRM.

        Args:
            firstname (str): Lead's first name (mandatory)
            lastname (str): Lead's last name (mandatory)
            email (str): Lead's email address (mandatory)
            phone (str, optional): Lead's phone number
            additional_properties (dict, optional): Any extra contact properties

        Returns:
            dict: The created contact object from HubSpot
        """
        try:
            url = f"{self.base_url}{self.contact_url}"
            properties = {
                "firstname": firstname,
                "lastname": lastname,
                "email": email
            }

            if phone:
                properties["phone"] = phone

            if additional_properties:
                properties.update(additional_properties)

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            response = requests.post(url, headers=headers, json={"properties": properties})
            response.raise_for_status()
            lead = response.json()
            logger.info(f"Lead created successfully: ID={lead.get('id')}, Email={email}")
            return lead

        except requests.exceptions.HTTPError as http_err:
            if http_err.response is not None and http_err.response.status_code == 409:
                logger.error(f"Duplicate lead is not allowed: {http_err}")
            else:
                logger.error(f"HTTP error occurred while creating lead: {http_err}")
        except Exception as e:
            logger.error(f"Error creating lead: {e}")

    def update_lead(self, email: str, updated_fields: dict) -> Dict:
        """
        Update a lead (contact) in HubSpot by email.
        
        Args:
            email (str): Email of the lead to update.
            updated_fields (dict): Fields and values to update.
        
        Returns:
            dict: Updated lead details if successful, else {}.

        Updatable fields in HubSpot contacts include (not exhaustive):
            - firstname (string)
            - lastname (string)
            - email (string, must be unique if changed)
            - phone (string)
            - company (string)
            - jobtitle (string)
            - city (string)
            - state (string)
            - zip (string)
            - country (string)
            - lead_status (dropdown, e.g. NEW, OPEN, IN_PROGRESS, OPEN_DEAL, UNQUALIFIED, ATTEMPTED_TO_CONTACT, CONNECTED, BAD_TIMING)
            - lifecycle_stage (dropdown, e.g. subscriber, lead, opportunity, customer, evangelist, other)
        """
        try:
            # Step 1: Search contact by email
            search_url = f"{self.base_url}{self.contact_url}/search"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "filterGroups": [{
                    "filters": [{
                        "propertyName": "email",
                        "operator": "EQ",
                        "value": email
                    }]
                }]
            }
            response = requests.post(search_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            if not results:
                logger.warning(f"No lead found with email: {email}")
                return {}

            contact_id = results[0]["id"]

            # Step 2: Validate dropdown fields before update
            valid_lead_statuses = [
                "NEW", "OPEN", "IN_PROGRESS", "OPEN_DEAL",
                "UNQUALIFIED", "ATTEMPTED_TO_CONTACT", "CONNECTED", "BAD_TIMING"
            ]
            valid_lifecycle_stages = [
                "subscriber", "lead", "marketingqualifiedlead", "salesqualifiedlead",
                "opportunity", "customer", "evangelist", "other"
            ]

            safe_fields = {}
            for field, value in updated_fields.items():
                if field == "lead_status" and value not in valid_lead_statuses:
                    logger.warning(f"Invalid lead_status '{value}' for {email}. Skipping this field.")
                    continue
                if field == "lifecycle_stage" and value not in valid_lifecycle_stages:
                    logger.warning(f"Invalid lifecycle_stage '{value}' for {email}. Skipping this field.")
                    continue
                safe_fields[field] = value

            if not safe_fields:
                logger.warning(f"No valid fields to update for {email}.")
                return {}

            # Step 3: Update contact
            update_url = f"{self.base_url}{self.contact_url}/{contact_id}"
            update_payload = {"properties": safe_fields}

            update_response = requests.patch(update_url, headers=headers, json=update_payload)
            update_response.raise_for_status()
            updated_data = update_response.json()

            logger.info(f"Lead {email} updated successfully with fields: {safe_fields}")
            return updated_data

        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred while updating lead: {http_err}")
            return {}
        except Exception as e:
            logger.error(f"Error updating lead: {e}")
            return {}

    def get_lead_by_email(self, email: str):
        """
        Fetch a lead/contact from HubSpot using email.

        Args:
            email (str): The email of the lead to fetch.

        Returns:
            dict: Lead details if found, else None.
        """
        try:
            url = f"{self.base_url}{self.contact_url}/search"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "filterGroups": [
                    {
                        "filters": [
                            {"propertyName": "email", "operator": "EQ", "value": email}
                        ]
                    }
                ],
                "properties": [
                    "firstname", "lastname", "email", "phone", "company",
                    "lead_status", "lifecycle_stage", "jobtitle", "city",
                    "state", "zip", "country", "createdate", "hs_object_id"
                ]
            }

            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            if not results:
                logger.info(f"No lead found with email: {email}")
                return None

            # Return the first matching lead
            lead = results[0]
            logger.info(f"Lead found: ID={lead.get('id')}, Email={email}")
            return lead

        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred while fetching lead: {http_err}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed while fetching lead: {e}")
            return None

    def export_leads_to_csv(self, file_name: str = None, path: str = None)-> None:
        """
        Export all HubSpot leads to a CSV file.

        Args:
            file_name (str, optional): Name of the CSV file. Defaults to "Hubspot_lead.csv".
            path (str, optional): Directory path where the file will be saved.
                                  Defaults to current working directory.
        """
        try:
            # Step 1: Get all leads
            leads = self.get_all_leads()
            if not leads:
                print("No leads found.")
                return None

            # Step 2: Collect all unique keys (fields) across leads
            all_fields = set()
            for lead in leads:
                all_fields.update(lead.get("properties", {}).keys())

            # Always include ID field explicitly
            all_fields.update(["id"])
            all_fields = sorted(all_fields)  # keep consistent order

            # Step 3: Set default filename if not provided
            if not file_name:
                file_name = "Hubspot_lead.csv"

            # Step 4: Handle directory path
            if not path:
                path = os.getcwd()  # current working directory

            os.makedirs(path, exist_ok=True)  # create folder if it doesn't exist

            full_path = os.path.join(path, file_name)

            # Step 5: Write CSV
            with open(full_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=all_fields)
                writer.writeheader()

                for lead in leads:
                    properties = lead.get("properties", {})
                    row = {field: properties.get(field, None) for field in all_fields}
                    row["id"] = lead.get("id", None)
                    writer.writerow(row)

            print(f"✅ Leads exported successfully to {full_path}")
            return full_path

        except Exception as e:
            print(f"Error exporting leads: {e}")
            return None
