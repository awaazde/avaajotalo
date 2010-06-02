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
logfilename = "/home/neil/Log/AO/recordmsg.log";
logfile = io.open(logfilename, "a");
logfile:setvbuf("line");

script_name = "recordmessage.lua";
digits = "";
arg = {};

--DIALSTRING_PREFIX = "user/";
DIALSTRING_PREFIX = "sofia/gateway/gizmo/";
DIALSTRING_SUFFIX = "";

phonenum = argv[1];
sessid = os.time();


freeswitch.consoleLog("info", script_name .. " : calling = " .. phonenum .. "\n");

-----------
-- recordmessage
-----------

function recordmessage ()
   local partfilename = "recordmsg/" .. os.time() .. ".mp3";
   local filename = sd .. partfilename;
   local maxlength = 1000 * 60 * 8;

   repeat
      read_no_bargein(aosd .. "pleaserecord.wav", 1000);
      session:execute("playback", "tone_stream://%(500, 0, 620)");
      freeswitch.consoleLog("info", script_name .. " : Recording " .. filename .. "\n");
      logfile:write(sessid, "\t",
		    session:getVariable("caller_id_number"), "\t",
		    os.time(), "\t", "Record", "\t", filename, "\n");
      session:execute("record", filename .. " " .. maxlength .. " 80 2");
      --sleep(1000);
      
      
      while (d ~= "1" and d ~= "2" and d ~= "3") do
		 read(aosd .. "hererecorded.wav", 1000);
		 read(filename, 1000);
		 read(rmsgsd .. "notsatisfied.wav", 2000);
		 sleep(6000)
		 d = use();
      end
      
     if (d == "3") then
	 	os.remove(filename);
		read_no_bargein(aosd .. "messagecancelled.wav", 500);
		hangup();
      end
      
   until (d == "1");

   read_no_bargein(rmsgsd .. "okrecorded.wav", 500);
end

-----------
-- MAIN 
-----------
aosd = basedir .. "/scripts/AO/sounds/eng/";
rmsgsd = basedir .. "/scripts/AO/sounds/survey/en/";

-- make the call
session = freeswitch.Session(DIALSTRING_PREFIX .. phonenum .. DIALSTRING_SUFFIX)
session:setVariable("caller_id_number", phonenum)
session:setVariable("playback_terminators", "#");
session:setHangupHook("hangup");
--session:setInputCallback("my_cb", "arg");

if (session:ready() == true) then
	-- sleep for a bit
	session:sleep(13000);

	logfile:write(sessid, "\t", session:getVariable("caller_id_number"),
	"\t", os.time(), "\t", "Start call", "\n");
	
	recordmessage();
	
	hangup();
end
