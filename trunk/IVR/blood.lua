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
require "luasql.odbc";
require "socket.http";

-- TODO: figure out how to get the local path
dofile("/usr/local/freeswitch/scripts/AO/paths.lua");
dofile("/usr/local/freeswitch/scripts/AO/common.lua");

script_name = "blood.lua";

-- script-specific sounds
bsd = basedir .. "/scripts/AO/sounds/blood/";

digits = "";
arg = {};

sessid = os.time();

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
local IBD_URL = 'http://indianblooddonors.com/fetch_donor.php?';
local IBD_PIN = 'std=';
local IBD_BGROUP = 'bgid=';

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
	freeswitch.consoleLog("info", script_name .. " : playing prompt " .. promptfile .. "\n");
	read(bsd .. promptfile, delay);
	d = use();
	repeat_cnt = check_abort(repeat_cnt, DEF_NUM_REPEATS)
end
   	 
---------------------------
------ set language -------
---------------------------
-- default
local lang = LANG_ENG;

if (d == LANG_ENG) then
	lang = LANG_ENG .. "/";
elseif (d == LANG_HIN) then
	lang = LANG_HIN .. "/";
end
	
---------------------------
------ get std code -------
---------------------------
promptfile = "std.wav";
repeat_cnt = 0;
d = "";
while (string.len(tostring(d)) < MIN_STD_LEN) do
	read(bsd .. lang .. promptfile, delay, MAX_STD_LEN);
	d = use();
	repeat_cnt = check_abort(repeat_cnt, DEF_NUM_REPEATS)
end
local std = d;
d = "";

-- get blood group
promptfile = "bloodgroup.wav";
repeat_cnt = 0;
d = "0";
while (tonumber(d) < MIN_BGROUP_ID or tonumber(d) > MAX_BGROUP_ID) do
	read(bsd .. lang .. promptfile, delay);
	d = use();
	repeat_cnt = check_abort(repeat_cnt, DEF_NUM_REPEATS)
end
local bgroupid = d;
d = "";
-- send request
response = socket.http.request(IBD_URL .. IBD_BGROUP .. bgroupid .. '&' .. IBD_STD .. std);
number = tostring(number);
-- playback number
repeat_cnt = 0;
-- loop up to default repeat times (make it an actual number just as a failsafe)
repeat
	promptfile = "numberis.wav";
	read_no_bargein(bsd .. lang .. promptfile, 1000);
	local i = 1;
	local digit = "";
	while (i <= 10) do
		digit = number:sub(i,i);
		read_no_bargein(bsd .. 'digits/' .. tostring(digit) .. '.wav', 1000);
	end
	repeat_cnt = repeat_cnt + 1;
until (repeat_cnt > DEF_NUM_REPEATS);

hangup();