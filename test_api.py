# /// script
# dependencies = ["linkdapi"]
# ///
from linkdapi import LinkdAPI
api_key = "li-AqG4H7aQFqrL9OGvesAP1qBWweEyIZ2RxUwQgT73XWlf-XJrXn_19UfArQSZ2OHMjPTJ_A4jIpNYNhhWmtyTbTctTtO82Q"
client = LinkdAPI(api_key)
print(client.get_profile_overview("satyanadella"))
