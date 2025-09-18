# Orkera SDK

Simple Python SDK for the Orkera's task scheduler.

## 🚀 Quick Start

To use the SDK, you need an API key. You can get one by signing up at [https://orkera.com](https://orkera.com).

```python
from orkera import OrkeraClient
from datetime import datetime, timedelta

# Initialize client (API URL is automatically set to https://api.orkera.com)
client = OrkeraClient(
    api_key="your_api_key"
)

# Schedule a task
task_id = client.schedule_task(
    task_name="calculate_sum",
    task_kwargs={"a": 10, "b": 20},
    schedule_time=datetime.now() + timedelta(seconds=10),
    callback_url="https://your-callback-url.com/"
)

print(f"Task scheduled: {task_id}")

# List only scheduled tasks
scheduled_tasks = client.list_scheduled_tasks()
print(f"Scheduled tasks: {len(scheduled_tasks)}")

# Get specific task
task = client.get_task(task_id)
print(f"Task status: {task.status}")
```

## 📋 **API Methods**

- `schedule_task(task_name, callback_url, task_args=None, task_kwargs=None, schedule_time=None)` - Schedule a task
- `list_tasks()` - List all tasks for the user
- `list_scheduled_tasks()` - List only scheduled tasks
- `get_task(task_id)` - Get details of a specific task

## 🔄 **What's New in v0.4.0**

- **Breaking Change**: `callback_url` is now required when scheduling tasks
- **New Method**: Added `list_scheduled_tasks()` to list only scheduled tasks
- **Security**: Enhanced server-side validation for callback URLs to prevent SSRF attacks
- **Bug Fix**: Fixed import issues in the SDK
