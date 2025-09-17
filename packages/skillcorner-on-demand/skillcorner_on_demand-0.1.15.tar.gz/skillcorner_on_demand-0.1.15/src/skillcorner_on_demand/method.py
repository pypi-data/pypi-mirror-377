from fitrequest.method_generator import RequestMethod

METHOD_DOCSTRING = (
    'Retrieve response from {endpoint} GET request. '
    'To learn more about it go to: https://tactical.skillcorner.com/api/docs/#{docs_url_anchor}.'
)


METHODS_BINDING = [
    {
        'name': 'get_all_requests',
        'endpoint': '/api/requests/',
        'docs_url_anchor': 'requests',
    },
    {
        'name': 'get_request',
        'endpoint': '/api/request/{}',
        'docs_url_anchor': 'request',
        'resource_name': 'match_id',
    },
    {
        'name': 'get_match_sheet',
        'endpoint': '/api/request/{}/match-sheet/',
        'docs_url_anchor': 'match_sheet',
        'resource_name': 'match_id',
    },
    {
        'name': 'post_match_sheet',
        'endpoint': '/api/request/{}/match-sheet/',
        'docs_url_anchor': 'match_sheet',
        'resource_name': 'match_id',
        'request_method': RequestMethod.post,
    },
    {
        'name': 'update_match_sheet',
        'endpoint': '/api/request/{}/match-sheet/',
        'docs_url_anchor': 'match_sheet',
        'resource_name': 'match_id',
        'request_method': RequestMethod.put,
    },
    {
        'name': 'get_period_limits',
        'endpoint': '/api/request/{}/period-limits/',
        'docs_url_anchor': 'period_limits',
        'resource_name': 'match_id',
    },
    {
        'name': 'post_period_limits',
        'endpoint': '/api/request/{}/period-limits/',
        'docs_url_anchor': 'period_limits',
        'resource_name': 'match_id',
        'request_method': RequestMethod.post,
    },
    {
        'name': 'update_period_limits',
        'endpoint': '/api/request/{}/period-limits/',
        'docs_url_anchor': 'period_limits',
        'resource_name': 'match_id',
        'request_method': RequestMethod.put,
    },
    {
        'name': 'get_home_team_side',
        'endpoint': '/api/request/{}/home-team-side/',
        'docs_url_anchor': 'home_team_side',
        'resource_name': 'match_id',
    },
    {
        'name': 'post_home_team_side',
        'endpoint': '/api/request/{}/home-team-side/',
        'docs_url_anchor': 'home_team_side',
        'resource_name': 'match_id',
        'request_method': RequestMethod.post,
    },
    {
        'name': 'update_home_team_side',
        'endpoint': '/api/request/{}/home-team-side/',
        'docs_url_anchor': 'home_team_side',
        'resource_name': 'match_id',
        'request_method': RequestMethod.put,
    },
    {
        'name': 'data_collection',
        'endpoint': '/api/match/{}/data_collection/',
        'docs_url_anchor': 'data_collection',
        'resource_name': 'match_id',
    },
    {
        'name': 'get_tracking_data',
        'endpoint': '/api/match/{}/tracking?data_version=3&on_demand=true',
        'docs_url_anchor': 'tracking',
        'resource_name': 'match_id',
    },
    {
        'name': 'match_data',
        'endpoint': '/api/match/{}/',
        'docs_url_anchor': 'match_data',
        'resource_name': 'match_id',
    },
    {
        'name': 'post_launch_match',
        'endpoint': '/api/request/{}/start-processing/',
        'docs_url_anchor': 'launch_match',
        'resource_name': 'match_id',
        'request_method': RequestMethod.post,
    },
    {
        'name': 'get_physical',
        'endpoint': '/api/match/{}/physical/',
        'docs_url_anchor': 'match_physical',
        'resource_name': 'match_id',
        'request_method': RequestMethod.get,
    },
    {
        'name': 'post_match_list',
        'endpoint': '/api/requests/match-list/',
        'docs_url_anchor': 'match_list',
        'request_method': RequestMethod.post,
    },
    {
        'name': 'get_match_dynamic_events',
        'endpoint': '/api/match/{}/dynamic_events/',
        'docs_url_anchor': 'dynamic_events',
        'resource_name': 'match_id',
        'request_method': RequestMethod.get,
    },
]
