"""
Simple HTTP-based Orkera client.
"""

import logging
import requests
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from .models import Task

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
        task_name: str,
        callback_url: str,
        task_args: Optional[List[Any]] = None,
        task_kwargs: Optional[Dict[str, Any]] = None,
        schedule_time: Optional[Union[datetime, str]] = None
    ) -> str:
        """
        Schedule a task for execution.
        
        Args:
            task_name: Name of the task to execute
            callback_url: URL to notify when task is triggered
            task_args: Positional arguments for the task
            task_kwargs: Keyword arguments for the task
            schedule_time: When to execute the task (datetime or ISO string)
        
        Returns:
            Task ID string
        
        Raises:
            requests.RequestException: If the request fails
            ValueError: If the response is invalid
        """
        url = f"{ORKERA_API_URL}/api/tasks/"
        payload = {
            'task_name': task_name,
            'task_args': task_args or [],
            'task_kwargs': task_kwargs or {},
            'callback_url': callback_url
        }
        if schedule_time:
            if isinstance(schedule_time, datetime):
                payload['schedule_time'] = schedule_time.isoformat()
            else:
                payload['schedule_time'] = schedule_time
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
    
    def list_tasks(self) -> List[Task]:
        """
        List all tasks for the authenticated user.
        
        Returns:
            List of Task objects
        """
        url = f"{ORKERA_API_URL}/api/tasks/"
        tasks = []
        params = {}
        while url:
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                if isinstance(data, dict) and 'results' in data:
                    tasks.extend([Task(**item) for item in data['results']])
                    url = data.get('next')
                    params = {}
                elif isinstance(data, list):
                    tasks.extend([Task(**item) for item in data])
                    url = None
                else:
                    tasks.extend([Task(**item) for item in data.get('tasks', [])])
                    url = None
            except requests.RequestException as e:
                logger.error(f"Failed to list tasks: {e}")
                raise
        return tasks
    
    def list_scheduled_tasks(self) -> List[Task]:
        """
        List all scheduled tasks for the authenticated user.
        
        Returns:
            List of Task objects with status 'scheduled'
        """
        url = f"{ORKERA_API_URL}/api/tasks/scheduled/"
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list):
                return [Task(**item) for item in data]
            else:
                return [Task(**item) for item in data.get('tasks', [])]
        except requests.RequestException as e:
            logger.error(f"Failed to list scheduled tasks: {e}")
            raise
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get details of a specific task.
        
        Args:
            task_id: ID of the task to retrieve
        
        Returns:
            Task object or None if not found
        """
        url = f"{ORKERA_API_URL}/api/tasks/{task_id}/"
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            return Task(**data)
        except requests.RequestException as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            raise
    
    def close(self):
        """Close the session."""
        self.session.close() 