import requests
from datetime import datetime
from eigeningenuity.core import get_default_server, EigenServer
from eigeningenuity.util import force_list, get_eigenserver, parseEvents, _do_chunked_eigen_post_request, _do_eigen_post_request, validate_eventlog_query

from typing import Union

class EventLog (object):
    """An elasticsearch instance which talks the Eigen elastic endpoint.
    """
    def __init__(self, baseurl: str, auth: bool):
        """This is a constructor. It takes in a URL like http://infra:8080/ei-applet/search/"""
        self.baseurl = baseurl
        self.eigenserver = get_eigenserver(baseurl)
        self.auth = auth

    def _testConnection(self):
        """Preflight Request to verify connection to ingenuity"""
        try:
            status = requests.get(self.baseurl, verify=False).status_code
        except (ConnectionError):
            raise ConnectionError ("Failed to connect to ingenuity instance at " + self.eigenserver + ". Please check the url is correct and the instance is up.")

    def _doJsonWriteRequest(self, relative_url: str,data: dict,label: str):
        url = self.baseurl + relative_url
        return _do_chunked_eigen_post_request(url,data,label,self.auth)

    def _doJsonReadRequest(self, relative_url: str, data: dict):
        url = self.baseurl + relative_url
        response = _do_eigen_post_request(url,data,self.auth)
        
        if response["success"] is not True:
            raise ValueError("Query failed: " + str(response["errors"]))

        return response["response"]

    def getEvents(self, query: dict, size: int = 1000, page: int = 0) -> list:
        """
        Execute a raw query against the ingenuity eventlog

        Args:
            query: A dictionary containing the query structure with the following format:
                - start (required): Start time (e.g., "yesterday", SO datetime string, python datetime object)
                - end (required): End time (e.g., "now", SO datetime string, python datetime object)
                - severities (optional): List of severity levels (e.g., ["INFO", "WARNING"])
                - types (optional): List of event types (e.g., ["DataTagThresholdCheck"]). Exact matches only. API fails to parse certain characters like '-'
                - sources (optional): List of source identifiers. Allows partial matches
                - messages (optional): List of message types. Allows partial matches
                - assetNames (optional): List of asset names
                - contentFilter (optional): Additional filter string. Uses Elasticsearch Query String syntax e.g. (fieldName1 = value1 AND fieldName2 = value2) AND (fieldName3 = b OR fieldName4 = d)
            size: Maximum number of results to return (default: 1000)
            page: Page number for pagination (default: 0)

        Returns:
            The response from ingenuity, typically a list of dictionaries
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate the query structure and required fields
        validate_eventlog_query(query)
        
        relative_url = "/list/eventlog"
        body = {
            "request": query,
            "size": size,
            "page": page
        }
        
        response = self._doJsonReadRequest(relative_url, body)

        return response

    def getEventsBySource(self, source: Union[str, list], exact_match: bool = False, start: Union[str, datetime] = "yesterday", end: Union[str, datetime] = "now", filter:Union[str, None] = None, size: int = 1000, page: int = 0) -> list:
        """
        Retrieve events from the ingenuity eventlog filtered by source

        Args:
            source: The source identifier to filter events by (string)
            exact_match: If True, only return events with an exact match on source. If False, allows partial matches (default: False)
            start: Start time (e.g., "yesterday", SO datetime string, python datetime object)
            end: End time (e.g., "now", SO datetime string, python datetime object)
            filter: Additional filter string. Uses Elasticsearch Query String syntax e.g. (fieldName1 = value1 AND fieldName2 = value2) AND (fieldName3 = b OR fieldName4 = d) (default: None)
            size: Maximum number of results to return (default: 1000)
            page: Page number for pagination (default: 0)

        Returns:
            The response from ingenuity, typically a list of dictionaries
            
        Raises:
            ValueError: If the source is not provided
        """
        if not source or not isinstance(source, (str, list)):
            raise ValueError("Source must be a non-empty string or list")

        source = force_list(source)

        validate_eventlog_query({
            "start": start,
            "end": end,
            "sources": source
        })

        relative_url = "/list/eventlog"
        body = {
            "request": {
                "start": start,
                "end": end,
                "sources": source
            },
            "size": size,
            "page": page
        }
        
        # Only include contentFilter if it's not None
        if filter is not None:
            body["request"]["contentFilter"] = filter
        
        response = self._doJsonReadRequest(relative_url, body)
        
        if exact_match:
            # Filter results to only include exact matches on source
            filtered_events = [event for event in response["items"] if event.get("source") in source]
            return filtered_events

        return response

    def getEventsByType(self, event_type: Union[str, list], start: Union[str, datetime] = "yesterday", end: Union[str, datetime] = "now", filter:Union[str, None] = None, size: int = 1000, page: int = 0) -> list:
        """
        Retrieve events from the ingenuity eventlog filtered by event type

        Args:
            event_type: The event type to filter events by (string)
            start: Start time (e.g., "yesterday", ISO datetime string, python datetime object)
            end: End time (e.g., "now", ISO datetime string, python datetime object)
            filter: Additional filter string. Uses Elasticsearch Query String syntax e.g. (fieldName1 = value1 AND fieldName2 = value2) AND (fieldName3 = b OR fieldName4 = d) (default: None)
            size: Maximum number of results to return (default: 1000)
            page: Page number for pagination (default: 0)

        Returns:
            The response from ingenuity, typically a list of dictionaries

        Raises:
            ValueError: If the event type is not provided
        """
        if not event_type or not isinstance(event_type, (str, list)):
            raise ValueError("Event type must be a non-empty string or list")
        
        event_type = force_list(event_type)

        validate_eventlog_query({
            "start": start,
            "end": end,
            "types": event_type
        })

        relative_url = "/list/eventlog"
        body = {
            "request": {
                "start": start,
                "end": end,
                "types": event_type
            },
            "size": size,
            "page": page
        }

        # Only include contentFilter if it's not None
        if filter is not None:
            body["request"]["contentFilter"] = filter

        response = self._doJsonReadRequest(relative_url, body)

        return response

    def pushToEventlog(self, events: Union[dict, list]) -> bool:
        """
        Push one or more events to the ingenuity eventlog, accepts any event structure

        Args:
            events: A single event as dict, many events as a list of dicts, or the string filepath of a file containing events

        Returns:
            A boolean representing the successful push of all events. False if at least one event failed to be created
        """
        events = parseEvents(events)
        relative_url = "/save-multiple"
        label = "events"
        
        failures = self._doJsonWriteRequest(relative_url, events, label)

        if failures:
            print("Some Events failed to push")
            return failures
        else:
            return True

def get_eventlog(eigenserver: EigenServer = None) -> EventLog:
    """
    Connect to Assetmodel of eigenserver. If eigenserver is not provided this will default to the EIGENSERVER environmental variable

    Args:
        eigenserver: An instance of EigenServer() to query

    Returns:
        An object defining a connection to the AssetModel
    """
    if eigenserver is None:
        eigenserver = get_default_server()
    elif isinstance(eigenserver, str):
        eigenserver = EigenServer(eigenserver)

    return EventLog(eigenserver.getEigenServerUrl() + "events" + "/", eigenserver.auth)

