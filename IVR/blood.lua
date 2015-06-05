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
********* Special application for Indianblooddonors.com
*************************************************************
--]]

-- INCLUDES
require "socket.http";
json = require("json");

-- TODO: figure out how to get the local path
dofile("/usr/local/freeswitch/scripts/AO/paths.lua");
dofile("/usr/local/freeswitch/scripts/AO/common.lua");

script_name = "blood.lua";

digits = "";
arg = {};
opencursors = {};

sessid = os.time();

local platelets = session:getVariable("platelet");
freeswitch.consoleLog("info", script_name .. " : platelet " .. tostring(platelets) .. "\n");
if (platelets == nil) then
	platelets = false;
end

-- survey phonenumber
destination = session:getVariable("destination_number");

-- caller's number
caller = session:getVariable("caller_id_number");
caller = caller:sub(-10);

logfilename = logfileroot .. "blood_" .. destination .. ".log";
logfile = io.open(logfilename, "a");
logfile:setvbuf("line");

local DIALSTRING_PREFIX = "freetdm/grp1/a/0";
local DIALSTRING_SUFFIX = "";
local LANG_ENG = 'eng';
local LANG_HIN = 'hin';
local MIN_STD_LEN = 3;
local MAX_STD_LEN = 5;
local DEF_NUM_REPEATS = 3;
local MIN_BGROUP_ID = 1;
local MAX_BGROUP_ID = 8;
local IBD_STD = 'std=';
local IBD_BGROUP = 'bgid=';
local IBD_CALLER = 'caller=';
local IBD_BGROUP_OPTS = {"a+%2Bve", "a+-ve", "b+%2Bve", "b+-ve", "ab+%2Bve", "ab+-ve", "o+%2Bve", "o+-ve"};

local IBD_URL = '';
if (platelets) then
	-- script-specific sounds
	bsd = sd .. "forum/platelets/";
	IBD_URL = 'http://plateletdonors.org/api/ivrs/ws-ivrs-std-code-search.php?';
	IBD_BGROUP = 'bloodgroup=';
	IBD_STD = 'stdcode=';
else
	-- script-specific sounds
	bsd = sd .. "forum/blood/";
	IBD_URL = 'http://indianblooddonors.com/fetch_donor.php?';
end

-- hard-coded for now
local callback_allowed = 0;

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
	pause_for_session_ready();
else
	-- answer the call
	session:answer();
end

session:setVariable("playback_terminators", "#");
session:setHangupHook("hangup");

-- sleep for a bit
session:sleep(1000);

logfile:write(sessid, "\t", caller, "\t", destination,
"\t", os.time(), "\t", "Start call", "\n");

delay = 4000;
---------------------------
---- welcome/choose lang --
---------------------------
local promptfile = "welcome.wav";

local repeat_cnt = 0
local d = "";
while (d ~= "1" and d ~= "2") do
	freeswitch.consoleLog("info", script_name .. " : playing prompt " .. bsd .. promptfile .. "\n");
	read(bsd .. promptfile, delay);
	d = input();
	repeat_cnt = check_abort(repeat_cnt, DEF_NUM_REPEATS)
end
   	 
---------------------------
------ set language -------
---------------------------
-- default
local lang = LANG_HIN;

if (d == "1") then
	lang = LANG_HIN .. "/";
elseif (d == "2") then
	lang = LANG_ENG .. "/";
end
freeswitch.consoleLog("info", script_name .. " : language is " .. lang .. "\n");
---------------------------
------ get std code -------
---------------------------
promptfile = "std.wav";
repeat_cnt = 0;
d = "";
while (string.len(tostring(d)) < MIN_STD_LEN) do
	freeswitch.consoleLog("info", script_name .. " : playing prompt " .. bsd .. lang .. promptfile .. "\n");
	read(bsd .. lang .. promptfile, delay, MAX_STD_LEN);
	d = input();
	repeat_cnt = check_abort(repeat_cnt, DEF_NUM_REPEATS)
end
local std = d;
d = "";

-- get blood group
promptfile = "bloodgroup.wav";
repeat_cnt = 0;
d = "0";
while (d == "" or tonumber(d) < MIN_BGROUP_ID or tonumber(d) > MAX_BGROUP_ID) do
	freeswitch.consoleLog("info", script_name .. " : playing prompt " .. bsd .. lang .. promptfile .. "\n");
	read(bsd .. lang .. promptfile, delay);
	d = input();
	repeat_cnt = check_abort(repeat_cnt, DEF_NUM_REPEATS)
end
local bgroupid = d;
if (platelets) then
	bgroupid = IBD_BGROUP_OPTS[tonumber(d)];
	if (bgroupid == nil) then
		bgroupid = '';
	end
end
d = "";
-- send request
freeswitch.consoleLog("info", script_name .. " : request {std=" .. std .. ",bgid=" .. bgroupid .. ",number=" .. caller .."}\n");
local response = socket.http.request {url=IBD_URL .. IBD_BGROUP .. bgroupid .. '&' .. IBD_STD .. std .. '&' .. IBD_CALLER .. caller, method="POST"};
freeswitch.consoleLog("info", script_name .. " : response is " .. tostring(response) .. "\n");

if (platelets) then
	json_table = json.decode(response);	
	if (json_table.DonorFound == false) then
		response = nil;
	else
		number = json_table.DonorMobile;
	end
else
	number = trim(tostring(response));
end

if (response == nil or trim(tostring(response)) == "0") then
	promptfile = "nomatch.wav";
	freeswitch.consoleLog("info", script_name .. " : playing prompt " .. bsd .. lang .. promptfile .. "\n");
	read(bsd .. lang .. promptfile, 0);
else
	-- playback number
	repeat_cnt = 0;
	-- loop up to default repeat times (make it an actual number just as a failsafe)
	repeat
		promptfile = "numberis.wav";
		freeswitch.consoleLog("info", script_name .. " : playing prompt " .. bsd .. lang .. promptfile .. "\n");
		read_no_bargein(bsd .. lang .. promptfile, 1000);
		local i = 1;
		local digit = "";
		while (i <= 10) do
			digit = number:sub(i,i);
			freeswitch.consoleLog("info", script_name .. " : playing prompt " .. bsd .. lang .. 'digits/' .. tostring(digit) .. '.wav' .. "\n");
			read_no_bargein(bsd .. lang .. 'digits/' .. tostring(digit) .. '.wav', 1000);
			i = i + 1;
		end
		repeat_cnt = repeat_cnt + 1;
		promptfile = "repeat.wav";
		read(bsd .. lang .. promptfile, 0);
	until (repeat_cnt > DEF_NUM_REPEATS);
end
hangup(CAUSE_APP_HANGUP);
