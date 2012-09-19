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
opencursors = {};

-- survey phonenumber
destination = session:getVariable("destination_number");
-- caller's number
caller = session:getVariable("caller_id_number");
caller = caller:sub(-10);

-- get survey id
query = 		"SELECT survey.id, survey.dialstring_prefix, survey.dialstring_suffix, survey.complete_after, survey.callback ";
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

local DIALSTRING_PREFIX = "";
local DIALSTRING_SUFFIX = "";
if (res[2] ~= nil) then
	DIALSTRING_PREFIX = res[2];
end
if (res[3] ~= nil) then
	DIALSTRING_SUFFIX = res[3];
end

complete_after_idx = tonumber(res[4]);
local callback_allowed = tonumber(res[5]);

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

prompts = get_prompts(surveyid);

if (callback_allowed == 1) then
	-- Allow for missed calls to be made
	session:execute("ring_ready");
	api = freeswitch.API();
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
	vars = vars .. ',origination_caller_id_number='..destination;
	vars = vars .. '}'
	session = freeswitch.Session(vars .. DIALSTRING_PREFIX .. caller .. DIALSTRING_SUFFIX)
	
	-- wait a while before testing
	session:sleep(2000);
	if (session:ready() == false) then
		hangup();
	end
else
	-- answer the call
	session:answer();
end

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



