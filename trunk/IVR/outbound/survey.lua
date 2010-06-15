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
CALLID_VAR = '{ao_survey=true}';

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
      session:getVariable("caller_id_number"), "\t", os.time(), "\t",
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
   local query = " SELECT opt.number, opt.action, opt.action_param1, opt.action_param2 ";
   query = query .. " FROM surveys_option opt, surveys_prompt prompt ";
   query = query .. " WHERE prompt.id = " .. promptid;
   freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
   return rows(query);
end

-----------
-- get_option
-----------

function get_option (promptid, number)
   local query = " SELECT opt.action, opt.action_param1, opt.action_param2 ";
   query = query .. " FROM surveys_option opt, surveys_prompt prompt ";
   query = query .. " WHERE prompt.id = " .. promptid;
   query = query .. " AND opt.prompt_id = prompt.id ";
   query = query .. " AND opt.number = '" .. number .. "' ";
   freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
   return row(query);
end

-----------
-- set_survey_complete
-----------

function set_survey_complete (callid)
   local query = " UPDATE surveys_call ";
   query = query .. " SET complete = 1 ";
   query = query .. " WHERE id = " .. callid;
   con:execute(query);
   freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
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
   local replay_cnt = 0;
   
   while (current_prompt ~= nil) do
   	  promptid = current_prompt[1];
   	  promptfile = current_prompt[2];
   	  bargein = current_prompt[3];
   	  freeswitch.consoleLog("info", script_name .. " : playing prompt " .. promptfile .. "\n");
   	  
	  if (complete_after_idx ~= nil and current_prompt_idx > complete_after_idx) then
   	  	set_survey_complete(callid);
   	  end
   	  
   	  if (bargein == 1) then
   	  	read(sursd .. promptfile, 2000);
      	  else
      		read_no_bargein(sursd .. promptfile, 2000);
   	  end
   	  d = use();
   	  
   	  -- get option
   	  option = get_option(promptid, d);
   	  if (option == nil) then
   	  	-- default: repeat which is safer than NEXT since bad input
		-- will make the prompt be skipped. Downside is that prompts have to have
		-- an explicit option for no input, though this is probably better practice.
   	  	action = OPTION_REPLAY;
   	  else
   	  	action = option[1];
   	  end
      
      freeswitch.consoleLog("info", script_name .. " : option selected - " .. tostring(action) .. "\n");
      if (action == OPTION_REPLAY) then
		replay_cnt = replay_cnt + 1;
		-- in case this call is going nowhere
		if (replay_cnt > 5) then
			hangup();
		end
      else
		replay_cnt = 0;
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
      elseif (action == OPTION_PREV) then
		 if (current_prompt_idx > 1) then
		    current_prompt_idx = current_prompt_idx - 1;
		    current_prompt = prevprompts[current_prompt_idx];
		 end
      elseif (action == OPTION_GOTO) then
	  	local goto_idx = tonumber(option[2]);
   		freeswitch.consoleLog("info", script_name .. " : goto idx is " .. tostring(goto_idx) .. "\n");
		-- check to see if we are at the last msg in the list
	 	if (goto_idx > #prevprompts) then
		    for i=current_prompt_idx+1, goto_idx do
			    current_prompt = prompts();
			    if (current_prompt ~= nil) then
			       table.insert(prevprompts, current_prompt);
			    end
			end
			current_prompt_idx = goto_idx;
		else
		    -- get msg from the prev list
		    current_prompt_idx = goto_idx;
		    current_prompt = prevprompts[current_prompt_idx];
	    end
	  end
    
   end -- end while
   
   -- if survey doesn't specify a finished prompt,
   -- that means the survey is finished after all prompts
   -- have been heard
   if (complete_after_idx == nil) then
   		set_survey_complete(callid);
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
	session:sleep(10000);
	logfile:write(sessid, "\t", session:getVariable("caller_id_number"),
	"\t", os.time(), "\t", "Start call", "\n");
	
	while (1) do
		-- play prompts
	   	play_prompts(prompts);
	end
end



