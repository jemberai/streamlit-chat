import os
import json
import requests
import logging

class DataIntakeService():
    def __init__(self) -> None:
        self.access_token = ''

    def request_oauth2_token(self):
        auth_server_url = os.environ["DATA_INTAKE_URL"]+"/oauth2/token"
        client_id = os.environ["DATA_INTAKE_CLIENT_ID"]
        client_secret = os.environ["DATA_INTAKE_CLIENT_SECRET"]

        token_req_payload = {'grant_type': 'client_credentials'}

        token_response = requests.post(
            auth_server_url,
            data=token_req_payload, 
            verify=False, 
            allow_redirects=False,
            auth=(client_id, client_secret)
        )
                    
        if token_response.status_code !=200:
            logging.info("Failed to obtain token from the OAuth 2.0 server")
        else:
            logging.info("Successfuly obtained a new token")
            tokens = json.loads(token_response.text)

            self.access_token = tokens['access_token']

            os.environ["DATA_INTAKE_ACCESS_TOKEN"] = self.access_token

    def __query_topk(self, query, topK=5, similarityThreshold=0):
        payload = {
            'query': query,
            'topK': topK,
            'similarityThreshold': similarityThreshold,
        }
        api_server_url = os.environ["DATA_INTAKE_URL"]+"/v1/query"
        api_call_headers = {'Authorization': 'Bearer ' + os.environ["DATA_INTAKE_ACCESS_TOKEN"]}
        api_call_response = requests.post(
            api_server_url, 
            headers=api_call_headers, 
            json = payload
        )

        return api_call_response

    def request_query_topk(self, query, topK=5, similarityThreshold=0):
        resp = self.__query_topk(query, topK, similarityThreshold)
        
        if resp.status_code != 200:
            logging.info("Query TopK returned NON 200")
            self.request_oauth2_token()
            resp = self.__query_topk(query, topK, similarityThreshold)
            if resp.status_code != 200:
                raise Exception("Failed to authenticate with server")
        
        return resp.json()

    def __create_upload_cloudevent(self, trace_id, filename, mime, temp_file):
        client_id = os.environ["DATA_INTAKE_CLIENT_ID"]
        
        with open(temp_file, 'rb') as f:
            payload = f.read()

        api_server_url = os.environ["DATA_INTAKE_URL"]+"/v1/event"
        api_call_headers = {
            'Authorization': 'Bearer ' + os.environ["DATA_INTAKE_ACCESS_TOKEN"],
            'ce-specversion': '1.0',
            'ce-id': trace_id,
            'ce-type': 'ai.jember.streamlit-chat.upload',
            'ce-source': f'/chat/{client_id}/embedding',
            'ce-datacontenttype': mime,
        }
        api_call_response = requests.post(
            api_server_url, 
            headers=api_call_headers, 
            data = payload
        )

        return api_call_response

    def request_create_upload_cloudevent(self, trace_id, filename, mime, temp_file):
        resp = self.__create_upload_cloudevent(trace_id, filename, mime, temp_file)
        
        if resp.status_code == 401:
            logging.info("Create event returned 401")
            self.request_oauth2_token()
            resp = self.__create_upload_cloudevent(trace_id, filename, mime, temp_file)
            if resp.status_code != 201:
                logging.warn(f'Create event returned {resp.status_code}')
                raise Exception("Failed to create event on server")
        elif resp.status_code != 201:
            logging.warn(f'Create event returned {resp.status_code}')
            raise Exception("Failed to create event on server")
        
        return True