from attrs import define
import os
import time
import sys
import threading
import requests
from .models import SearchResponse, SearchResult, SyncStartResponse, SyncStatusResponse, FailedDocumentInfo


@define
class COB:

    apikey: str | None = os.getenv("COB_APIKEY")
    apiurl: str = "https://api.cob.vondr.ai"

    def search(self, question: str, top_n: int = 8) -> SearchResponse:
        """Search for documents based on a query."""
        t = time.time()

        headers = {"Authorization": f"bearer {self.apikey}"}
        
        # top_n is always sent as a required parameter
        params = {"top_n": top_n}
        
        response = requests.get(self.apiurl + '/search/' + question, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        
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

    def _show_status_animation(self, stop_event: threading.Event, message: str = "Checking"):
        """Show a rotating animation while an operation is in progress."""
        animation_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        i = 0
        
        while not stop_event.is_set():
            sys.stdout.write(f'\r{animation_chars[i % len(animation_chars)]} {message}...')
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        
        # Clear the animation line
        sys.stdout.write('\r' + ' ' * (len(message) + 10) + '\r')
        sys.stdout.flush()

    def start_sync(self, wait_for_completion: bool = False, check_interval: int = 5) -> SyncStartResponse:
        """
        Start a background sync operation.
        
        Args:
            wait_for_completion: If True, waits for sync to complete by polling status
            check_interval: Seconds between status checks when waiting
            
        Returns:
            SyncStartResponse with success status and message
        """
        print("🔄 Starting sync with SharePoint...")
        
        try:
            headers = {"Authorization": f"bearer {self.apikey}"}
            response = requests.post(self.apiurl + '/sync/', headers=headers)
            
            if response.status_code == 409:
                print("⚠️  A sync is already running!")
                return SyncStartResponse(success=False, message="A sync operation is already in progress")
            
            response.raise_for_status()
            
            start_response = SyncStartResponse(**response.json())
            print(start_response)
            
            if start_response.success and wait_for_completion:
                print("\n📊 Waiting for sync to complete...")
                print("(Press Ctrl+C to stop waiting and check status manually later)\n")
                
                # Start animation
                stop_event = threading.Event()
                animation_thread = threading.Thread(
                    target=self._show_status_animation, 
                    args=(stop_event, "Syncing")
                )
                animation_thread.daemon = True
                animation_thread.start()
                
                try:
                    while True:
                        time.sleep(check_interval)
                        
                        # Check status
                        status = self._get_status_quietly()
                        
                        if not status.is_sync_running:
                            # Stop animation
                            stop_event.set()
                            animation_thread.join(timeout=1.0)
                            
                            print("✅ Sync completed!")
                            print(status)
                            break
                        
                        # Update animation message with runtime
                        if status.sync_runtime_seconds:
                            minutes, seconds = divmod(int(status.sync_runtime_seconds), 60)
                            if minutes > 0:
                                time_str = f"Syncing ({minutes}m {seconds}s)"
                            else:
                                time_str = f"Syncing ({seconds}s)"
                            
                            # Update message
                            stop_event.set()
                            animation_thread.join(timeout=0.5)
                            stop_event = threading.Event()
                            animation_thread = threading.Thread(
                                target=self._show_status_animation,
                                args=(stop_event, time_str)
                            )
                            animation_thread.daemon = True
                            animation_thread.start()
                            
                except KeyboardInterrupt:
                    stop_event.set()
                    animation_thread.join(timeout=1.0)
                    print("\n\n⏸️  Stopped waiting. Sync continues in background.")
                    print("Use .status() to check sync progress later.\n")
                    
            return start_response
            
        except Exception as e:
            print(f"❌ Failed to start sync: {str(e)}")
            raise

    def _get_status_quietly(self) -> SyncStatusResponse:
        """Get status without printing (for internal use)."""
        headers = {"Authorization": f"bearer {self.apikey}"}
        response = requests.get(self.apiurl + '/sync/status', headers=headers)
        response.raise_for_status()
        
        response_json = response.json()
        
        # Handle both list and dict for failed_documents
        failed_docs = response_json.get("failed_documents", [])
        if failed_docs and isinstance(failed_docs[0], dict):
            # Convert dict to FailedDocumentInfo if needed
            failed_documents = [
                FailedDocumentInfo(
                    filename=doc.get("filename", ""),
                    folder=doc.get("folder", ""),
                    error_message=doc.get("error_message", "")
                ) if isinstance(doc, dict) else doc
                for doc in failed_docs
            ]
            response_json["failed_documents"] = failed_documents
        
        return SyncStatusResponse(**response_json)

    def status(self) -> SyncStatusResponse:
        """
        Get the current sync status.
        
        Returns general sync system status including:
        - Whether a sync is currently running
        - Overall statistics
        - Failed documents
        """
        print("📊 Fetching sync status...")
        
        # Start animation for status check
        stop_event = threading.Event()
        animation_thread = threading.Thread(
            target=self._show_status_animation,
            args=(stop_event, "Loading status")
        )
        animation_thread.daemon = True
        animation_thread.start()
        
        try:
            status_response = self._get_status_quietly()
            
            # Stop animation
            stop_event.set()
            animation_thread.join(timeout=1.0)
            
            print(status_response)
            return status_response
            
        except Exception as e:
            stop_event.set()
            animation_thread.join(timeout=1.0)
            print(f"❌ Failed to get status: {str(e)}")
            raise

    # Convenience method for backward compatibility
    def sync(self, wait: bool = True) -> SyncStartResponse:
        """
        Start a sync operation (backward compatibility wrapper).
        
        Args:
            wait: If True, waits for sync to complete (default: True for compatibility)
            
        Returns:
            SyncStartResponse
        """
        return self.start_sync(wait_for_completion=wait)