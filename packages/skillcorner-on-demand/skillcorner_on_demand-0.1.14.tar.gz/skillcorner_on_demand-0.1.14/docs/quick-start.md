# Getting Started

## Installation
```shell
uv pip install skillcorner-on-demand
```

## Credentials
You need to add in your environment your `username` and `password` with that you can access to the service, if you don't like this method follow the alternative

```shell
export SKILLCORNER_ON_DEMAND_USERNAME=email@mycompagny.com
export SKILLCORNER_ON_DEMAND_PASSWORD=mysuperpassword
```

## How to use it
You just need to instanciate the client like this

```py
import os

from skillcorner_on_demand.client import SkillcornerOnDemandClient

USERNAME = os.getenv('SKILLCORNER_ON_DEMAND_USERNAME')
PASSWORD = os.getenv('SKILLCORNER_ON_DEMAND_PASSWORD')

client = SkillcornerOnDemandClient(USERNAME, PASSWORD)

client.get_all_requests()
```

With the reponse
```json
"count": 6,
    "next": null,
    "previous": null,
    "results": {
        "matches": [
            {
                "id": 14,
                "status": "input_data",
                "tactical_data": [],
                "match": {
                    "id": 1429092,
                    "unique_name": "Match Name",
                    "date_time": "2024-02-10T13:00:00Z",
                    "status": "not_started"
                },
                "is_matchsheet_csv_valid": true,
                "is_period_limits_csv_valid": true,
                "is_homeside_team_csv_valid": true,
                "is_video_uploaded": false
            },
            ...
        ]
    }
```

## Send a CSV file

```python
client = SkillcornerOnDemandClient(USERNAME, PASSWORD)

with open('path/to/csvfile.csv', 'rb') as f:
    file_payload = {
        'file': ('match_sheet.csv', f, 'text/csv'),
    }
    response = client.post_match_sheet(
        match_id=1429092,
        files=file_payload,
    )

```

response

```shell
Information successfully added and uploaded to the request
```
