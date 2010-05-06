--[[ 

Copyright (c) 2009 Regents of the University of California, Stanford
  University, and others

   Licensed under the Apache License, Version 2.0 (the "License"); you
   may not use this file except in compliance with the License.  You
   may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied.  See the License for the specific language governing
   permissions and limitations under the License.

   --]]

-- INCLUDES
require "luasql.odbc";

-- TODO: figure out how to get the local path
dofile("/usr/local/freeswitch/scripts/AO/paths.lua");

-- overwrite standard logfile
logfilename = "/home/neil/Log/AO/alert.log";
logfile = io.open(logfilename, "a");
logfile:setvbuf("line");

script_name = "missed_call.lua";
DIALSTRING_PREFIX = "{ignore_early_media=true}user/"
wait_interval = 5000;

userid = argv[1];

freeswitch.consoleLog("info", script_name .. " : user id = " .. userid .. "\n");

-- Get phone number to call out
query = "SELECT number FROM AO_user where id = ".. userid;
cur = con:execute(query);
row = {};
result = cur:fetch(row);
cur:close();
phone_num = tostring(row[1]);

-- FUNCTIONS

-----------
-- hangup 
-----------

function hangup() 
   logfile:write(sessid, "\t",
		 session:getVariable("caller_id_number"), "\t",
		 os.time(), "\t", "End call", "\n");
 
   -- cleanup
   con:close();
   env:close();
   logfile:flush();
   logfile:close();
   
   -- hangup
   session:hangup();
end

-----------
-- MAIN 
-----------

-- make the call
session = freeswitch.Session(DIALSTRING_PREFIX .. phone_num)
session:setHangupHook("hangup");
logfile:write(sessid, "\t", phone_name,
	"\t", os.time(), "\t", "Missed Call", "\n");

-- This needs to be tuned
session:sleep(wait_interval);

hangup();
