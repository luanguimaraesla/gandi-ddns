import requests

class GandiHandler:
    def __init__(self, api, api_key):
        self.api = api
        self.api_key = api_key
        self.zones_info = self.get_zones_information()

    def get_zones_information(self):
        request_headers = {"X-Api-Key": self.api_key}
        http_response = requests.get(self.api + "zones", headers=request_headers)
        return http_response.json()

    def _get_zone_info(self, attribute, domain):
        for zone in self.zones_info:
            if zone['name'].find(domain) >= 0: #if domain matches
                return zone[attribute]
        else:
            return None

    def get_zone_uuid(self, domain):
        return self._get_zone_info('uuid', domain)

    def get_zone_href(self, domain):
        return self._get_zone_info('zone_href', domain)

    def get_zone_records(self, domain):
        request_headers = {"X-Api-Key": self.api_key}
        zone_href = self.get_zone_href(domain)
        http_response = requests.get(zone_href + '/records', headers=request_headers)
        zone_records = http_response.json()
        return zone_records

    def _get_record_info(self, attribute, record_name, record_type, domain):
        request_headers = {"X-Api-Key": self.api_key}
        zone_records = self.get_zone_records(domain)
        for record in zone_records:
            if record['rrset_name'] == record_name and record['rrset_type'] == record_type:
                return record[attribute]
        else:
            return None

    def get_record_href(self, record_name, record_type, domain):
        return self._get_record_info('rrset_href', record_name, record_type, domain)

    def is_ip_up_to_date(self, new_ip, record_href):
        request_headers = {
            "X-Api-Key": self.api_key
        }

        http_response = requests.get(record_href, headers=request_headers)
        record_info = http_response.json()
        return record_info['rrset_values'][0] == new_ip
        

    def change_zone_a_record(self, new_ip, record_name, ttl, domain):
        request_headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key
        }

        request_data = {
            "rrset_ttl": ttl,
            "rrset_values": [
                new_ip
            ]
        }

        record_href = self.get_record_href(record_name, "A", domain) 
        if not self.is_ip_up_to_date(new_ip, record_href):
            print("Recording new IP(" + new_ip + ") for " + record_name + ".")
            print("URL: " + record_href)

            http_response = requests.put(record_href,
                headers=request_headers, data=str(request_data).replace("'",'"'))

            print("Request response status: " + str(http_response.status_code))
            print("Request text: " + http_response.text)
        else:
            print("External IP is up to date")
