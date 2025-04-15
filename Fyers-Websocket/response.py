from fyers_apiv3 import fyersModel

client_id = ""
access_token = ""
fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")

data = {
    "symbols":"NSE:SBIN-EQ,NSE:IDEA-EQ"
}

response = fyers.quotes(data=data)
print(response)