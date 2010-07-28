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
dofile("/usr/local/freeswitch/scripts/AO/common.lua");

-- overwrite standard logfile
logfilename = "/home/neil/Log/AO/survey.log";
logfile = io.open(logfilename, "a");
logfile:setvbuf("line");

script_name = "survey.lua";
aosd = basedir .. "/scripts/AO/sounds/";
-- script-specific sounds
sursd = aosd .. "survey/";
CALLID_VAR = '{ao_survey=true,ignore_early_media=true}';

digits = "";
arg = {};

sessid = os.time();
-- The prompts_played queue. Make global to record listens
-- on hangup event
prevprompts = {};

-- receive the call object
callid = argv[1];

-- get subject id, phone number, and survey id
query = 		"SELECT subject.id, subject.number, survey.id, survey.dialstring_prefix, survey.dialstring_suffix, survey.complete_after ";
query = query .. " FROM surveys_survey survey, surveys_subject subject, surveys_call c ";
query = query .. " WHERE c.id = " .. callid;
query = query .. " AND c.survey_id = survey.id AND c.subject_id = subject.id ";
freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
res = row(query);
subjectid = res[1];
phonenum = res[2];
surveyid = res[3];

DIALSTRING_PREFIX = "";
DIALSTRING_SUFFIX = "";
if (res[4] ~= nil) then
	DIALSTRING_PREFIX = res[4];
end
if (res[5] ~= nil) then
	DIALSTRING_SUFFIX = res[5];
end

complete_after_idx = res[6];

freeswitch.consoleLog("info", script_name .. " : subject id = " .. subjectid .. " , num = " .. phonenum .. " , survey = " .. surveyid .. ", complete_after = " .. complete_after_idx .. "\n");

-----------
-- my_cb
-----------

function my_cb(s, type, obj, arg)
   freeswitch.console_log("info", "\ncallback: [" .. obj['digit'] .. "]\n")
   
   if (type == "dtmf") then
      
      logfile:write(sessid, "\t",
      session:getVariable("caller_id_number"), "\t", session:getVariable("destination_number"), "\t", os.time(), "\t",
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

-- make the call
session = freeswitch.Session(CALLID_VAR .. DIALSTRING_PREFIX .. phonenum .. DIALSTRING_SUFFIX)
session:setVariable("caller_id_number", phonenum)
session:setVariable("playback_terminators", "#");
session:setHangupHook("hangup");
--session:setInputCallback("my_cb", "arg");

if (session:ready() == true) then
	-- sleep for a bit
	session:sleep(1000);
	logfile:write(sessid, "\t", session:getVariable("caller_id_number"), "\t", session:getVariable("destination_number"),
	"\t", os.time(), "\t", "Start call", "\n");
	
	while (1) do
		-- play prompts
	   	play_prompts(prompts);
	end
end



