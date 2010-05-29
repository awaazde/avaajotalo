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

digits = "";
arg = {};

-- These should be consistent with the constants in the database
OPTION_NEXT = 1;
OPTION_PREV = 2;
OPTION_REPLAY = 3;
OPTION_GOTO = 4;

sessid = os.time();
-- The prompts_played queue. Make global to record listens
-- on hangup event
prevprompts = {};

-- receive the call object
callid = argv[1];

-- get subject id, phone number, and survey id
query = 		"SELECT subject.id, subject.number, survey.id, survey.dialstring_prefix, survey.dialstring_suffix ";
query = query .. " FROM surveys_survey survey, surveys_subject subject, surveys_call c ";
query = query .. " WHERE c.id = " .. callid;
freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
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

-----------
-- get_prompts
-----------

function get_prompts(surveyid)
	local query = 	"SELECT id, file, bargein ";
	query = query .. " FROM surveys_prompt ";
	query = query .. " WHERE survey_id = " .. surveyid;
	query = query .. " ORDER BY surveys_prompt.order ASC ";
	freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
	return rows(query);
end

-----------
-- get_options
-----------

function get_options (promptid)
   local query = " SELECT option.number, option.action, option.action_param1, option.action_param2 ";
   query = query .. " FROM surveys_option option, surveys_prompt prompt ";
   query = query .. " WHERE prompt.id = " .. promptid;
   freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
   return rows(query);
end

-----------
-- get_option
-----------

function get_option (promptid, number)
   local query = " SELECT option.action, option.action_param1, option.action_param2 ";
   query = query .. " FROM surveys_option option, surveys_prompt prompt ";
   query = query .. " WHERE prompt.id = " .. promptid;
   query = query .. " AND option.number = '" .. number .. "' ";
   freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
   return row(query);
end

-----------
-- play_prompts
-----------

function play_prompts (prompts)
   -- get the first prompt
   local current_prompt = prompts();
   prevprompts = {};
   table.insert(prevprompts, current_prompt);
   local current_prompt_idx = 1;
   local d = "";
   
   while (current_prompt ~= nil) do
   	  promptid = current_prompt[1];
   	  promptfile = current_prompt[2];
   	  bargein = current_prompt[3];
   	  
   	  if (bargein == "1") then
   	  	read(sursd .. promptfile);
      	d = use();
      else
      	session:streamFile(sursd .. promptfile);
   	  	d = "";
      	sleep(1000);
   	  end
   	  
   	  -- get option
   	  option = get_option(promptid, d);
   	  if (option == nil) then
   	  	-- default: go to next
   	  	action = OPTION_NEXT
   	  else
   	  	action = option[1];
   	  end
      
      if (action == OPTION_NEXT) then
	    current_prompt_idx = current_prompt_idx + 1;
		-- check to see if we are at the last msg in the list
	 	if (current_prompt_idx > #prevprompts) then
		    -- get next msg from the cursor
		    current_prompt = prompts();
		    if (current_prompt ~= nil) then
		       table.insert(prevprompts, current_prompt);
		    end
		else
		    -- get msg from the prev list
		    current_prompt = prevprompts[current_prompt_idx];
	    end
      elseif (d == OPTION_PREV) then
		 if (current_prompt_idx > 1) then
		    current_prompt_idx = current_prompt_idx - 1;
		    current_prompt = prevprompts[current_prompt_idx];
		 end
      elseif (d == OPTION_REPLAY) then
		-- do nothing
      elseif (d == OPTION_GOTO) then
	  	current_prompt_idx = option[2];
		-- check to see if we are at the last msg in the list
	 	if (current_prompt_idx > #prevprompts) then
		    -- get next msg from the cursor
		    current_prompt = prompts();
		    if (current_prompt ~= nil) then
		       table.insert(prevprompts, current_prompt);
		    end
		else
		    -- get msg from the prev list
		    current_prompt = prevprompts[current_prompt_idx];
	    end
	  end
    
   end -- end while
   update_listens(prevprompts, userid);
end


-----------
-- MAIN 
-----------

prompts = get_prompts(surveyid);

-- make the call
session = freeswitch.Session(DIALSTRING_PREFIX .. phonenum .. DIALSTRING_SUFFIX)
session:setVariable("caller_id_number", phonenum)
session:setVariable("playback_terminators", "#");
session:setHangupHook("hangup");
-- handle bargeins manually
--session:setInputCallback("my_cb", "arg");

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



