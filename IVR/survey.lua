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

--[[ 
*************************************************************
********* NOTE: This is an inbound version 
********* 		of outbound/survey.lua
*************************************************************
--]]

-- INCLUDES
require "luasql.odbc";

-- TODO: figure out how to get the local path
dofile("/usr/local/freeswitch/scripts/AO/paths.lua");
dofile("/usr/local/freeswitch/scripts/AO/common.lua");

logfilename = logfileroot .. "survey_in.log";
logfile = io.open(logfilename, "a");
logfile:setvbuf("line");

script_name = "survey.lua";
aosd = basedir .. "/scripts/AO/sounds/";
-- script-specific sounds
sursd = aosd .. "survey/";

digits = "";
arg = {};

sessid = os.time();
-- The prompts_played queue. Make global to record listens
-- on hangup event
prevprompts = {};
opencursors = {};

-- survey phonenumber
destination = session:getVariable("destination_number");
-- caller's number
caller = session:getVariable("caller_id_number");
-- there is no outbound call
callid = nil;

-- get survey id
query = 		"SELECT survey.id, survey.complete_after ";
query = query .. " FROM surveys_survey survey ";
query = query .. " WHERE number LIKE '%" .. destination .. "%' ";
query = query .. " AND name LIKE '%" .. INBOUND_DESIGNATOR .. "%'";
freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
res = row(query);
surveyid = res[1];
complete_after_idx = res[2];

freeswitch.consoleLog("info", script_name .. " , num = " .. caller .. " , survey = " .. surveyid .. "\n");

-----------
-- my_cb
-----------

function my_cb(s, type, obj, arg)
   freeswitch.console_log("info", "\ncallback: [" .. obj['digit'] .. "]\n")
   
   if (type == "dtmf") then
      
      logfile:write(sessid, "\t",
      caller, "\t", destination, "\t", os.time(), "\t",
      "dtmf", "\t", arg[1], "\t", obj['digit'], "\n");
      
      freeswitch.console_log("info", "\ndigit: [" .. obj['digit']
			     .. "]\nduration: [" .. obj['duration'] .. "]\n");
      
      
      digits = obj['digit'];
      if (bargein) then
      	return "break";
      else
      	return "continue";
      end
      
   else
      freeswitch.console_log("info", obj:serialize("xml"));
   end
end

-----------
-- MAIN 
-----------

prompts = get_prompts(surveyid);

-- answer the call
session:answer();

if (session:ready() == true) then
	-- sleep for a bit
	session:sleep(1000);
	
	logfile:write(sessid, "\t", caller, "\t", destination,
	"\t", os.time(), "\t", "Start call", "\n");
	
	-- play prompts
	play_prompts(prompts);
	
	logfile:write(sessid, "\t", caller, "\t", destination,
	"\t", os.time(), "\t", "End call", "\n");
end



