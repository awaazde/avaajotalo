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
-- script-specific sounds
sursd = aosd .. "survey/";

digits = "";
arg = {};

sessid = os.time();
-- for the message_played queue. Make global to record listens
-- on hangup event
prevmsgs = {};

-- receive the call object
callid = argv[1];

-- get subject id, phone number, and survey id
query = 		"SELECT subject.id, subject.number, survey.id, survey.dialstring_prefix, survey.dialstring_suffix ";
query = query .. " FROM surveys_survey survey, surveys_subject subject, surveys_call call ";
query = query .. " WHERE call.id = " .. callid;

res = row(query)
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

freeswitch.consoleLog("info", script_name .. " : subject id = " .. subjectid .. " , num = " .. phonenum .. " , survey = " .. surveyid .. "\n");

function play_prompts(prompts)

end


-----------
-- MAIN 
-----------
-- get prompts
query = 		"SELECT file ";
query = query .. " FROM surveys_prompt ";
query = query .. " WHERE survey_id = " .. surveyid;
query = query .. " ORDER BY order ASC ";

prompts = rows(query);

-- make the call
session = freeswitch.Session(DIALSTRING_PREFIX .. phonenum .. DIALSTRING_SUFFIX)
session:setVariable("caller_id_number", phonenum)
session:setVariable("playback_terminators", "#");
session:setHangupHook("hangup");
session:setInputCallback("my_cb", "arg");

if (session:ready() == true) then

	logfile:write(sessid, "\t", session:getVariable("caller_id_number"),
	"\t", os.time(), "\t", "Start call", "\n");
	
	-- sleep for a sec
	sleep(1000);
	
	while (1) do
	   -- play prompts
	   play_prompts(prompts);
	end
	
	hangup();
end



