from tor import Tor, TorControl

torSession1 = Tor("127.0.0.1", 9050)
torSession1.initialize()
torSession1.connect("ident.me", 80)
request = torSession1.get_request()
print(request)

torController = TorControl("127.0.0.1", 9150)
torController.authenticate("")
torController.new_identity()

# Must create new Tor session after requesting new identity
torSession2 = Tor("127.0.0.1", 9050)
torSession2.initialize()
torSession2.connect("ident.me", 80)
request2 = torSession2.get_request()
print(request2)

# Manual / Custom command
# command = torController.command("SIGNAL NEWNYM")
# Get the output of the command in 2 parts; .status (integer)
# status_code = command.status
# info (string)
# status_info = command.info
# status_code (integer)
# print(str(status_code) + " " + status_info)
