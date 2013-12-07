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

-- TODO: figure out how to get the local path
dofile("/usr/local/freeswitch/scripts/AO/paths.lua");
dofile("/usr/local/freeswitch/scripts/AO/common.lua");
dofile("/usr/local/freeswitch/scripts/AO/db.lua");

script_name = "survey.lua";
aosd = basedir .. "/scripts/AO/sounds/";
-- script-specific sounds
sursd = aosd .. "survey/";

digits = "";
arg = {};

sessid = os.time();
-- for call durations
callstarttime = nil;

-- The prompts_played queue. Make global to record listens
-- on hangup event
prevprompts = {};

-- survey phonenumber
-- get destination from different spots depending
-- on whether this is SIP or PRI
destination = session:getVariable("sip_to_user");
if (destination == nil) then
	destination = session:getVariable("destination_number");
else
	destination = destination:sub(-8);
end
freeswitch.consoleLog("info", script_name .. " : destination = " .. destination .. "\n");
-- get survey id
query = 		"SELECT survey.id, survey.complete_after, survey.callback, survey.outbound_number ";
query = query .. " FROM surveys_survey survey ";
query = query .. " WHERE number LIKE '%" .. destination .. "%' ";
-- This is legacy, moved to inbound field
query = query .. " AND (name LIKE '%" .. INBOUND_DESIGNATOR .. "%' ";
query = query .. " 		OR survey.inbound = 1) ";
-- get most recent version of the survey
query = query .. " ORDER BY survey.id DESC ";
freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
local res = row(query);
local surveyid = res[1];

logfilename = logfileroot .. "survey_in_" .. destination .. ".log";
logfile = io.open(logfilename, "a");
logfile:setvbuf("line");



complete_after_idx = tonumber(res[2]);
local callback_allowed = tonumber(res[3]);
local outbound_number = nil;
if (res[4] ~= nil and res[4] ~= '') then
	outbound_number = res[4];
end

-- caller's number
caller = session:getVariable("caller_id_number");
-- get the dialer now to check for whether this
-- is survey has a dialer with a country code associated with it;
-- if so, parse the inbound phone number accordingly
local prefixes = {};
local suffixes = {};
local maxparallels = {};
local channel_vars_tbl = {};
local dialer_types = {};
local country_code = nil;

-- get dialer and phone number length info
local dialstrings = get_table_rows("ao_dialer dialer, surveys_survey_dialers survey_dialers", "survey_dialers.survey_id="..surveyid.." AND dialer.id = survey_dialers.dialer_id", "dialer.dialstring_prefix, dialer.dialstring_suffix, dialer.max_parallel_in, dialer.country_code, dialer.min_number_len, dialer.channel_vars, dialer.type");
local dialstring = dialstrings();
local min_len = nil;
local phone_num = nil;
local pattern = nil;
while (dialstring ~= nil) do
	table.insert(prefixes, dialstring[1]);
	suffixes[dialstring[1]] = dialstring[2];
	table.insert(maxparallels, dialstring[3]);
	channel_vars_tbl[dialstring[1]] = dialstring[6];
	table.insert(dialer_types, dialstring[7]);

	if (phone_num == nil) then
		country_code = dialstring[4];
		min_len = tonumber(dialstring[5]);
		freeswitch.consoleLog("info", script_name .. ": country code = " .. tostring(country_code) .. " , minlen = " .. tostring(min_len) .."\n");
		if (country_code ~= nil and country_code ~= '' and min_len ~= nil) then
			pattern = '('..string.rep('%d', min_len)..'%d*)';			
			phone_num = string.match(caller, '1?'..country_code..pattern) or string.match(caller, pattern);
			--freeswitch.consoleLog("info", script_name .. ": country code = " .. country_code .. " , minlen = " .. tostring(min_len) .. " , pattern = " .. pattern .. " , phone_num = " .. phone_num .."\n");
		end
	end
	
	dialstring = dialstrings();
end

if (phone_num ~= nil) then
	caller = phone_num
else
	-- default
	caller = caller:sub(-10);
	country_code = '';
end

-- added for forwarding (checking sufficient balance, creating forward request, etc.)
userid = get_table_field('ao_user', 'id', 'number='..caller);

-- create a call in order to track any inputs made to this survey
-- first get subject id
query = "SELECT subject.id FROM surveys_subject subject WHERE subject.number = " .. caller;
freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
local cur = con:execute(query);
local subj = row(query);

local subjectid = nil;
if (subj == nil) then
	query = "INSERT INTO surveys_subject (number) VALUES ('" ..caller.."')";
	con:execute(query);
	freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n");
	local cur = con:execute("SELECT LAST_INSERT_ID()");
	subjectid = tostring(cur:fetch());
	cur:close();
else
	subjectid = subj[1];
end

-- create the call
query = "INSERT INTO surveys_call (subject_id, survey_id, date, priority ) VALUES (" ..subjectid..","..surveyid..",now(),1) ";
con:execute(query);
freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n");
local cur = con:execute("SELECT LAST_INSERT_ID()");
callid = tostring(cur:fetch());
cur:close();

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
function survey_main()
	prompts = get_prompts(surveyid);
	
	if (callback_allowed == 1) then
		freeswitch.consoleLog("info", script_name .. " : in main \n");
		-- Allow for missed calls to be made
		session:execute("ring_ready");
		local api = freeswitch.API();
		
		local channel_vars = nil;
		 -- find a dialer that is available
	    local DIALSTRING_PREFIX = get_available_line(api, prefixes, maxparallels, dialer_types)..country_code;
	    local DIALSTRING_SUFFIX = suffixes[DIALSTRING_PREFIX] or '';
	    channel_vars = channel_vars_tbl[DIALSTRING_PREFIX];
	    channel_vars = replace_channel_vars_wildcards(channel_vars);
	
		local uuid = session:getVariable('uuid');
		local mc_cnt = 0;
	    while (api:executeString('eval uuid:' .. uuid .. ' ${Channel-Call-State}') == 'RINGING') do
		 	session:sleep(3000);
		 	mc_cnt = check_abort(mc_cnt, 11)
	  	end
		freeswitch.consoleLog("info", script_name .. " : woke up \n");
			
		-- Missed call; 
		-- call the user back
		session:hangup();
		local vars = '{';
		vars = vars .. 'ignore_early_media=true';
		vars = vars .. ',caller_id_number='..caller;
		vars = vars .. ',origination_caller_id_number='.. (outbound_number or destination);
		vars = vars .. ',origination_caller_id_name='.. (outbound_number or destination);
		if (channel_vars ~= nil) then
			vars = vars ..','.. channel_vars ..',';
		end
		vars = vars .. '}'
		
		freeswitch.consoleLog("info", script_name .. " : vars = " .. vars .. "\n");
		session = freeswitch.Session(vars .. DIALSTRING_PREFIX .. caller .. DIALSTRING_SUFFIX)
		
		-- wait a while before testing
		-- do it in increments so we don't wait unnecessarily long
		local ready_cnt = 0;
		while (ready_cnt < 10 and session:ready() ~= true) do
			-- session:sleep doesn't work!
			os.execute("sleep 2");
			ready_cnt = ready_cnt + 1;
		end
	else
		-- answer the call
		session:answer();
	end
	
	if (session:ready() == true) then
		session:setVariable("playback_terminators", "#");
		session:setHangupHook("hangup");
		
		-- sleep for a bit
		--session:sleep(1000);
		
		callstarttime = os.time();
		logfile:write(sessid, "\t", caller, "\t", destination,
		"\t", callstarttime, "\t", "Start call", "\n");
		
		-- play prompts
		play_prompts(prompts);
		
		hangup();
	end
end

status, err = pcall(survey_main)
if status == false and termination_reason ~= NORMAL_HANGUP then
	freeswitch.consoleLog("err", tostring(debug.traceback(err)) .. "\n");
end

