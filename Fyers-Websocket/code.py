# Import the required module from the fyers_apiv3 package
from fyers_apiv3 import fyersModel

client_id = "QGP6MO6UJQ-100"
secret_key = "2X22I3160A"
redirect_uri = "https://trade.fyers.in/api-login/redirect-uri/index.html"
response_type = "code"  
state = "sample_state"
grant_type = "authorization_code"  

# The authorization code received from Fyers after the user grants access
auth_code = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBfaWQiOiJRR1A2TU82VUpRIiwidXVpZCI6IjlhNWMyMzk3MzRjOTRiZTM5ZDIyYWQ0MTZiMDRmYzU1IiwiaXBBZGRyIjoiIiwibm9uY2UiOiIiLCJzY29wZSI6IiIsImRpc3BsYXlfbmFtZSI6IlhSMjAxODUiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiJkZWNhY2RhZDNmNzdjMGNkYTE0OThlNzY1MzdiMTMyYjcxNGMyZTg0NmQzNDFmMmZiYzkzZmY1YSIsImlzRGRwaUVuYWJsZWQiOiJOIiwiaXNNdGZFbmFibGVkIjoiTiIsImF1ZCI6IltcImQ6MVwiLFwiZDoyXCIsXCJ4OjBcIixcIng6MVwiLFwieDoyXCJdIiwiZXhwIjoxNzQ0NzQ4NjY1LCJpYXQiOjE3NDQ3MTg2NjUsImlzcyI6ImFwaS5sb2dpbi5meWVycy5pbiIsIm5iZiI6MTc0NDcxODY2NSwic3ViIjoiYXV0aF9jb2RlIn0.4Lz9g--SVigZWtdEZosqQfFOmyXSQhK21rzwhhWHoFw"

# Create a session object to handle the Fyers API authentication and token generation
session = fyersModel.SessionModel(
    client_id=client_id,
    secret_key=secret_key, 
    redirect_uri=redirect_uri, 
    response_type=response_type, 
    grant_type=grant_type
)

# Set the authorization code in the session object
session.set_token(auth_code)

# Generate the access token using the authorization code
response = session.generate_token()

# Print the response, which should contain the access token and other details
print(response)


