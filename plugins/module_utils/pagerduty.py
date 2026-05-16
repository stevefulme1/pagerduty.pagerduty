from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
from ansible.module_utils.urls import open_url
from ansible.module_utils.basic import env_fallback

PAGERDUTY_COMMON_ARGS = dict(
    api_token=dict(
        type='str',
        required=True,
        no_log=True,
        fallback=(env_fallback, ['PAGERDUTY_API_TOKEN', 'PD_API_TOKEN']),
    ),
    api_url=dict(
        type='str',
        default='https://api.pagerduty.com',
    ),
)


class PagerDutyError(Exception):
    def __init__(self, message, status_code=None, response=None):
        super(PagerDutyError, self).__init__(message)
        self.status_code = status_code
        self.response = response


class PagerDutyClient(object):
    def __init__(self, module):
        self.module = module
        self.api_token = module.params['api_token']
        self.base_url = module.params.get('api_url', 'https://api.pagerduty.com').rstrip('/')

    def _headers(self):
        return {
            'Authorization': 'Token token={0}'.format(self.api_token),
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.pagerduty+json;version=2',
        }

    def request(self, method, path, data=None, params=None):
        url = '{0}{1}'.format(self.base_url, path)
        if params:
            query = '&'.join('{0}={1}'.format(k, v) for k, v in params.items() if v is not None)
            if query:
                url = '{0}?{1}'.format(url, query)

        body = json.dumps(data) if data else None
        try:
            response = open_url(
                url,
                method=method,
                headers=self._headers(),
                data=body,
                timeout=30,
            )
            status = response.getcode()
            if status == 204:
                return None
            return json.loads(response.read())
        except Exception as e:
            error_msg = str(e)
            status_code = getattr(e, 'code', None)
            body = None
            if hasattr(e, 'read'):
                try:
                    body = json.loads(e.read())
                    if 'error' in body:
                        error_msg = body['error'].get('message', error_msg)
                        errors = body['error'].get('errors', [])
                        if errors:
                            error_msg = '{0}: {1}'.format(error_msg, '; '.join(errors))
                except Exception:
                    pass
            raise PagerDutyError(error_msg, status_code=status_code, response=body)

    def get(self, path, params=None):
        return self.request('GET', path, params=params)

    def post(self, path, data):
        return self.request('POST', path, data=data)

    def put(self, path, data):
        return self.request('PUT', path, data=data)

    def delete(self, path):
        return self.request('DELETE', path)

    def list_all(self, path, resource_key, params=None):
        results = []
        if params is None:
            params = {}
        params['limit'] = 100
        params['offset'] = 0
        while True:
            response = self.get(path, params=params)
            items = response.get(resource_key, [])
            results.extend(items)
            if not response.get('more', False):
                break
            params['offset'] += len(items)
        return results

    def find_by_name(self, path, resource_key, name, query_param='query'):
        params = {query_param: name}
        items = self.list_all(path, resource_key, params=params)
        for item in items:
            if item.get('name') == name:
                return item
        return None

    def find_by_id(self, path, resource_key=None):
        try:
            result = self.get(path)
            if resource_key and resource_key in result:
                return result[resource_key]
            return result
        except PagerDutyError as e:
            if e.status_code == 404:
                return None
            raise


class PagerDutyModule(object):
    def __init__(self, module):
        self.module = module
        self.client = PagerDutyClient(module)
        self.check_mode = module.check_mode
        self.result = dict(changed=False)

    def _sanitize(self, obj, keys_to_remove=None):
        if keys_to_remove is None:
            keys_to_remove = {'created_at', 'updated_at', 'html_url', 'self', 'type'}
        if isinstance(obj, dict):
            return {k: self._sanitize(v, keys_to_remove) for k, v in obj.items() if k not in keys_to_remove}
        return obj

    def _diff(self, current, desired, compare_keys):
        changes = {}
        for key in compare_keys:
            if key in desired:
                current_val = current.get(key)
                desired_val = desired[key]
                if current_val != desired_val:
                    changes[key] = desired_val
        return changes

    def ensure_present(self, resource_key, find_path, find_key, create_path, create_data,
                       update_path_tmpl, update_data_fn=None, compare_keys=None, id_field='id'):
        existing = None
        resource_id = self.module.params.get(id_field)
        name = self.module.params.get('name')

        if resource_id:
            existing = self.client.find_by_id('{0}/{1}'.format(find_path, resource_id), resource_key)
        elif name:
            existing = self.client.find_by_name(find_path, find_key, name)

        if existing:
            if compare_keys and update_data_fn:
                desired = update_data_fn()
                changes = self._diff(existing, desired, compare_keys)
                if changes:
                    if not self.check_mode:
                        update_path = update_path_tmpl.format(id=existing['id'])
                        result = self.client.put(update_path, {resource_key: changes})
                        self.result[resource_key] = result.get(resource_key, result)
                    else:
                        self.result[resource_key] = existing
                    self.result['changed'] = True
                else:
                    self.result[resource_key] = existing
            else:
                self.result[resource_key] = existing
        else:
            if not self.check_mode:
                result = self.client.post(create_path, {resource_key: create_data})
                self.result[resource_key] = result.get(resource_key, result)
            self.result['changed'] = True

        return self.result

    def ensure_absent(self, resource_key, find_path, find_key, delete_path_tmpl, id_field='id'):
        existing = None
        resource_id = self.module.params.get(id_field)
        name = self.module.params.get('name')

        if resource_id:
            existing = self.client.find_by_id('{0}/{1}'.format(find_path, resource_id), resource_key)
        elif name:
            existing = self.client.find_by_name(find_path, find_key, name)

        if existing:
            if not self.check_mode:
                delete_path = delete_path_tmpl.format(id=existing['id'])
                self.client.delete(delete_path)
            self.result['changed'] = True

        return self.result

    def exit(self):
        self.module.exit_json(**self.result)

    def fail(self, msg):
        self.module.fail_json(msg=msg, **self.result)


class PagerDutyEventsClient(object):
    def __init__(self, module):
        self.module = module
        self.events_url = module.params.get('events_url', 'https://events.pagerduty.com/v2/enqueue')
        self.change_url = module.params.get('change_url', 'https://events.pagerduty.com/v2/change/enqueue')

    def send_event(self, routing_key, event_action, dedup_key=None, payload=None, links=None, images=None):
        data = {
            'routing_key': routing_key,
            'event_action': event_action,
        }
        if dedup_key:
            data['dedup_key'] = dedup_key
        if payload:
            data['payload'] = payload
        if links:
            data['links'] = links
        if images:
            data['images'] = images

        try:
            response = open_url(
                self.events_url,
                method='POST',
                headers={'Content-Type': 'application/json'},
                data=json.dumps(data),
                timeout=30,
            )
            return json.loads(response.read())
        except Exception as e:
            raise PagerDutyError('Events API error: {0}'.format(str(e)))

    def send_change(self, routing_key, summary, timestamp=None, source=None, custom_details=None, links=None):
        payload = {'summary': summary}
        if timestamp:
            payload['timestamp'] = timestamp
        if source:
            payload['source'] = source
        if custom_details:
            payload['custom_details'] = custom_details

        data = {
            'routing_key': routing_key,
            'payload': payload,
        }
        if links:
            data['links'] = links

        try:
            response = open_url(
                self.change_url,
                method='POST',
                headers={'Content-Type': 'application/json'},
                data=json.dumps(data),
                timeout=30,
            )
            return json.loads(response.read())
        except Exception as e:
            raise PagerDutyError('Change Events API error: {0}'.format(str(e)))
