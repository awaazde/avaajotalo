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
logfilename = "/home/neil/Log/AO/notification_voice.log";
logfile = io.open(logfilename, "a");
logfile:setvbuf("line");

script_name = "notification_voice.lua";
aosd = basedir .. "/scripts/AO/sounds/";
-- script-specific sounds XXXX TO DO - where are the tag files
tagsd = aosd .. "tags/";
notsd = aosd .. "notification/";
CALLID_VAR = '{ao_notification=true}';

digits = "";
arg = {};

sessid = os.time();
-- The prompts_played queue. Make global to record listens
-- on hangup event
prevprompts = {};

-- receive the call object
notification_message_id = argv[1];

-- get subject id, phone number, and survey id
query = 		"SELECT  number, voice_message_tag ";
query = query .. " FROM notification_notificationmessage";
query = query .. " WHERE id = " .. notification_message_id;
freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
res = row(query);
phonenum = res[1];
tag = res[2];

-- get the tag file
query = 		"SELECT  tag_file ";
query = query .. " FROM AO_tag";
query = query .. " WHERE tag = '" .. tag .. "'";
freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
res = row(query);
tag_file = res[1];


DIALSTRING_PREFIX = "";
DIALSTRING_SUFFIX = "";

--------------------------------------------------------------------------------
-- set_voice_notification
--------------------------------------------------------------------------------
function set_voice_notification (notid)
   local query = " UPDATE notification_notificationmessage ";
   -- XXXX TODO replace 111111 by the current time
   -- query = query .. " SET sent_on = 11111111 ";
   query = query .. " SET sent_on = created_on";
   query = query .. " WHERE id = " .. notid;
   con:execute(query);
   freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
end

--------------------------------------------------------------------------------
-- MAIN 
--------------------------------------------------------------------------------

-- make the call
session = freeswitch.Session(CALLID_VAR .. DIALSTRING_PREFIX .. phonenum .. DIALSTRING_SUFFIX)
session:setVariable("caller_id_number", phonenum)
session:setVariable("playback_terminators", "#");
session:setHangupHook("hangup");

if (session:ready() == true) then
	-- sleep for a bit
	session:sleep(10000);
	logfile:write(sessid, "\t", session:getVariable("caller_id_number"), "\t", session:getVariable("destination_number"),
	"\t", os.time(), "\t", "Start call", "\n");
	
	-- XXXX TO DO use the file that has: you have new messages in your inbox about
	read(notsd .. "youhavemessages.wav", 500);
	-- XXXX TODO use the file that has for instance: millet.wav (one for each tag)
	read(tagsd .. tag ..".wav", 500);

	-- DONE, update the DB
	
end



