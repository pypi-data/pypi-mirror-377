"""
Simple HTTP-based Orkera client.
"""

import logging
import requests
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from .models import Params

logger = logging.getLogger(__name__)

# Global API endpoint
ORKERA_API_URL = "https://api.orkera.com"


class OrkeraClient:
    """
    Simple HTTP client for the Orkera server.
    
    Provides basic task scheduling functionality via REST API.
    """
    
    def __init__(self, api_key: str, timeout: int = 30):
        """
        Initialize the Orkera client.
        
        Args:
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Api-Key {api_key}',
            'Content-Type': 'application/json'
        })
    
    def schedule_task(
        self,
        task_name: Optional[str] = None,
        task_args: Optional[List[Any]] = None,
        task_kwargs: Optional[Dict[str, Any]] = None,
        schedule_time: Optional[Union[datetime, str]] = None,
        callback_url: Optional[str] = None,
        params: Optional[Params] = None
    ) -> str:
        """
        Schedule a task for execution.
        
        Args:
            task_name: Name of the task to execute
            task_args: Positional arguments for the task
            task_kwargs: Keyword arguments for the task
            schedule_time: When to execute the task (datetime or ISO string)
            callback_url: URL to notify when task is triggered
            params: Params object containing all parameters (alternative to individual args)
            
        Returns:
            Task ID string
            
        Raises:
            requests.RequestException: If the request fails
            ValueError: If the response is invalid
        """
        url = f"{ORKERA_API_URL}/api/tasks/"
        
        # Use Params object if provided, otherwise use individual parameters
        if params:
            if not isinstance(params, Params):
                raise ValueError("params must be a Params object")
            
            payload = {
                'task_name': params.task_name,
                'task_args': params.task_args or [],
                'task_kwargs': params.task_kwargs or {}
            }
            
            if params.schedule_time:
                payload['schedule_time'] = params.schedule_time.isoformat()
            if params.callback_url:
                payload['callback_url'] = params.callback_url
        else:
            if not task_name:
                raise ValueError("task_name is required when not using params object")
            
            payload = {
                'task_name': task_name,
                'task_args': task_args or [],
                'task_kwargs': task_kwargs or {}
            }
            
            if schedule_time:
                if isinstance(schedule_time, datetime):
                    payload['schedule_time'] = schedule_time.isoformat()
                else:
                    payload['schedule_time'] = schedule_time
                    
            if callback_url:
                payload['callback_url'] = callback_url
        
        try:
            response = self.session.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            task_id = data.get('task_id')
            
            if not task_id:
                raise ValueError("No task_id in server response")
            
            logger.info(f"Task scheduled successfully: {task_id}")
            return task_id
            
        except requests.RequestException as e:
            logger.error(f"Failed to schedule task: {e}")
            raise
        except (KeyError, ValueError) as e:
            logger.error(f"Invalid response from server: {e}")
            raise
    
    def list_tasks(self) -> List[Dict[str, Any]]:
        """
        List all tasks for the authenticated user.
        
        Returns:
            List of task dictionaries
        """
        url = f"{ORKERA_API_URL}/api/tasks/"
        tasks = []
        params = {}
        while url:
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                # If paginated, expect 'results' and 'next' keys
                if isinstance(data, dict) and 'results' in data:
                    tasks.extend(data['results'])
                    url = data.get('next')
                    params = {}  # 'next' is a full URL
                elif isinstance(data, list):
                    tasks.extend(data)
                    url = None
                else:
                    # fallback for unexpected structure
                    tasks.extend(data.get('tasks', []))
                    url = None
            except requests.RequestException as e:
                logger.error(f"Failed to list tasks: {e}")
                raise
        return tasks
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get details of a specific task.
        
        Args:
            task_id: ID of the task to retrieve
            
        Returns:
            Task details dictionary or None if not found
        """
        url = f"{ORKERA_API_URL}/api/tasks/{task_id}/"
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            raise
    
    def close(self):
        """Close the session."""
        self.session.close() 