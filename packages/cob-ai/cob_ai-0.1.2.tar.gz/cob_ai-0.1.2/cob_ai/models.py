from __future__ import annotations

import time
import requests
from dataclasses import dataclass
from typing import List, Optional
import textwrap


@dataclass
class SyncCompletionStatus:
    processed_count: int
    deleted_count: int
    failed_count: int
    failed_documents: list[dict]

    def __str__(self) -> str:
        # Header with sync completion info
        header = "🔄 Sync Completion Status"
        header_separator = "═" * len(header)
        
        # Summary stats
        summary = (
            f"📊 Processed: {self.processed_count} documents\n"
            f"🗑️  Deleted: {self.deleted_count} documents\n"
            f"❌ Failed: {self.failed_count} documents"
        )
        
        # Failed documents details if any
        failed_details = ""
        if self.failed_documents:
            failed_details = "\n\n📋 Failed Documents:\n" + "─" * 20
            for i, doc in enumerate(self.failed_documents, 1):
                failed_details += f"\n{i}. {doc.get('filename', 'Unknown file')}: {doc.get('error', 'Unknown error')}"
        
        return (
            f"\n{header}\n"
            f"{header_separator}\n"
            f"{summary}"
            f"{failed_details}\n"
        )
@dataclass
class FailedDocumentInfo:
    filename: str
    folder: str
    error_message: str

@dataclass
class SyncStatusResponse:
    synced_folders: list[str]
    successfully_synced_count: int
    failed_documents_count: int
    failed_documents: list[FailedDocumentInfo]

    def __str__(self) -> str:
        # Header with sync status info
        header = "📈 Sync Status Overview"
        header_separator = "═" * len(header)
        
        # Summary stats
        summary = (
            f"✅ Successfully synced: {self.successfully_synced_count} documents\n"
            f"❌ Failed documents: {self.failed_documents_count} documents\n"
            f"📁 Synced folders: {len(self.synced_folders)} folders"
        )
        
        # Folders list
        folders_section = ""
        if self.synced_folders:
            folders_section = "\n\n📂 Synced Folders:\n" + "─" * 17
            for i, folder in enumerate(self.synced_folders, 1):
                folders_section += f"\n{i}. {folder}"
        
        # Failed documents details if any
        failed_details = ""
        if self.failed_documents:
            failed_details = "\n\n📋 Failed Documents:\n" + "─" * 20
            for i, doc in enumerate(self.failed_documents, 1):
                failed_details += f"\n{i}. {doc.filename} ({doc.folder}): {doc.error_message}"
        
        return (
            f"\n{header}\n"
            f"{header_separator}\n"
            f"{summary}"
            f"{folders_section}"
            f"{failed_details}\n"
        )


@dataclass
class SearchResult:
    filename: str
    snippet: str
    sharepoint_link: str

    def __str__(self) -> str:
        # Format filename with file icon and styling
        filename_display = f"📄 {self.filename}"
        
        # Wrap snippet text for better readability (max 80 chars per line)
        wrapped_snippet = textwrap.fill(
            self.snippet, 
            width=80, 
            initial_indent="   ", 
            subsequent_indent="   "
        )
        
        # Create a clean link display
        link_display = f"🔗 {self.sharepoint_link}"
        
        return (
            f"\n{filename_display}\n"
            f"{'─' * len(filename_display)}\n"
            f"{wrapped_snippet}\n\n"
            f"{link_display}\n"
            f"{'═' * 80}\n"
        )

@dataclass
class SearchResponse:
    query: str
    results: List[SearchResult]
    time_taken:float

    def __str__(self) -> str:
        # Header with search query
        header = f"🔍 Search Results for: \"{self.query}\""
        header_separator = "═" * len(header)
        
        # Results count
        count_info = f"Found {len(self.results)} result{'s' if len(self.results) != 1 else ''}"
        
        # Join all results with numbering
        results_text = ""
        for i, result in enumerate(self.results, 1):
            # Add numbering to each result
            numbered_result = str(result).replace("📄", f"{i}. 📄", 1)
            results_text += numbered_result
        
        # Remove trailing separator if there are results
        if results_text:
            results_text = results_text.rstrip("═" * 80 + "\n")
        
        return (
            f"\n{header}\n"
            f"{header_separator}\n"
            f"{count_info}\n"
            f"{results_text}\n"
        )
