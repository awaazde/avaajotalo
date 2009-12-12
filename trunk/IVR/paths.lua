basedir = "/usr/local/freeswitch";
bsd = basedir .. "/sounds/en/us/callie/";
logfilename = "/home/dsc/Documents/Log/AO/ao.log";
aosd = basedir .. "/scripts/AO/sounds/guj/";
sd = "/home/dsc/Development/audio/";
--logfilename = "/Library/WebServer/Documents/AO/ao.log";
--aosd = basedir .. "/scripts/AO/sounds/eng/";
--sd = basedir .. "/storage/otalo/";

-- GLOBALS
env = assert (luasql.mysql());
con = assert (env:connect("otalo","otalo","otalo","localhost"));

-- ADMINS
cur = con:execute("SELECT number from AO_user WHERE admin = 'y'" );
local admins = cur:fetch({});
cur:close();

function adminmode()
	local caller = session:getVariable("caller_id_number");
	if (admins ~= nil) then
		for k,v in ipairs(admins) do
			if (v == caller) then
				return true;
			end
		end
	end
	return false;
end
