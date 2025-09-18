from attrs import define
import os
import time
from typing import Optional, List
import requests
from .models import SearchResponse, SearchResult, SyncCompletionStatus, SyncStatusResponse


@define
class COB:

    apikey:str|None = os.getenv("COB_APIKEY")
    apiurl:str = "http://127.0.0.1:8000"
    DEFAULT_TOP_N:int = 8

    def search(self, question:str, top_n:Optional[int] = None) -> SearchResponse:
        t = time.time()

        headers = {"Authorization": f"bearer {self.apikey}"}
        
        # Use default value if top_n is not provided
        if top_n is None:
            top_n = self.DEFAULT_TOP_N
        
        # top_n is always sent as a required parameter
        params = {"top_n": top_n}
        
        response = requests.get(self.apiurl + '/search/' + question, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for bad status codes
        
        results = response.json()
        
        search_results = [
            SearchResult(
                filename=r["filename"],
                snippet=r["snippet"],
                sharepoint_link=r["sharepoint_link"],
            )
            for r in results.get("results", [])
        ]
        
        search_response = SearchResponse(query=question, results=search_results, time_taken=time.time()-t)
        print(search_response)
        return search_response

    
    def sync(self) -> SyncCompletionStatus:
        """
        Triggers a full synchronization with SharePoint and returns a summary.
        """
        headers = {"Authorization": f"bearer {self.apikey}"}
        response = requests.get(self.apiurl + '/sync/', headers=headers)
        response.raise_for_status()  # Will raise an HTTPError for bad responses (4xx or 5xx)
        
        # The response JSON is parsed and validated against the Pydantic model
        sync_status = SyncCompletionStatus(**response.json())
        print(sync_status)
        return sync_status

    def status(self) -> SyncStatusResponse:
        """
        Retrieves the current synchronization status from the API.
        """
        headers = {"Authorization": f"bearer {self.apikey}"}
        response = requests.get(self.apiurl + '/sync/status', headers=headers)
        response.raise_for_status() # Will raise an HTTPError for bad responses
        
        # The response JSON is parsed and validated against the Pydantic model
        status_response = SyncStatusResponse(**response.json())
        print(status_response)
        return status_response