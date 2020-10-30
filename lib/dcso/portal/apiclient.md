`APIClient` is the main class for interacting with DCSO Portal.

Basic example (`api_endpoint` is something known to the reader):

    from dcso.portal import APIClient
    
    apic = APIClient(api_endpoint)
    apic.auth.authenticate(username='alice', password='tea.pots')

When authentication was successful, the API token will stored in the
APIClient instance, unless the `authenticate` method was called with
parameter `set_api_token` set to False.

In most cases, using credentials is not an option, and a Machine (API)
Token is preferred. In your application, you can after instantiating
the client, you set the token property:

    from dcso.portal import APIClient
    
    apic = APIClient(api_endpoint)
    apic.token = "YOURTOKENHERE"

The above is done automatically for you when you set the environment
variable `DCSO_PORTAL_TOKEN`.
