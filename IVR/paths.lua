basedir = "/usr/local/freeswitch";
bsd = basedir .. "/sounds/en/us/callie/";
aosd = basedir .. "/scripts/AO/sounds/guj/";
sd = "/home/dsc/Development/audio/";
logfilename = "/home/dsc/Documents/Log/AO/ao.log";
--sd = basedir .. "/storage/otalo/";
--logfilename = sd .. "ao.log";

-- GLOBALS
env = assert (luasql.mysql());
con = assert (env:connect("otalo","otalo","otalo","localhost"));

-- ADMINS
cur = con:execute("SELECT number from AO_user WHERE admin = 'y'" );
local admins = {};
local num = cur:fetch();
while (num ~= nil) do
  table.insert(admins, num);
  num = cur:fetch();
end
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

-- UTILITY FUNCTIONS
function table.val_to_str ( v )
  if "string" == type( v ) then
    v = string.gsub( v, "\n", "\\n" )
    if string.match( string.gsub(v,"[^'\"]",""), '^"+$' ) then
      return "'" .. v .. "'"
    end
    return '"' .. string.gsub(v,'"', '\\"' ) .. '"'
  else
    return "table" == type( v ) and table.tostring( v ) or
      tostring( v )
  end
end

function table.key_to_str ( k )
  if "string" == type( k ) and string.match( k, "^[_%a][_%a%d]*$" ) then
    return k
  else
    return "[" .. table.val_to_str( k ) .. "]"
  end
end

function table.tostring( tbl )
  local result, done = {}, {}
  for k, v in ipairs( tbl ) do
    table.insert( result, table.val_to_str( v ) )
    done[ k ] = true
  end
  for k, v in pairs( tbl ) do
    if not done[ k ] then
      table.insert( result,
        table.key_to_str( k ) .. "=" .. table.val_to_str( v ) )
    end
  end
  return "{" .. table.concat( result, "," ) .. "}"
end

