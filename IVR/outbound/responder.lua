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

-- TODO: figure out how to get the local path
dofile("/usr/local/freeswitch/scripts/AO/paths.lua");
dofile("/usr/local/freeswitch/scripts/AO/common.lua");
dofile("/usr/local/freeswitch/scripts/AO/db.lua");

script_name = "responder.lua";
digits = "";
arg = {};

sessid = os.time();
userid = argv[1];
-- for the message_played queue. Make global to record listens
-- on hangup event
prevmsgs = {};
adminforums = {};

freeswitch.consoleLog("info", script_name .. " : user id = " .. userid .. "\n");

-- Get phone number to call out
local num = row("SELECT number FROM ao_user where id = ".. userid);

caller = tostring(num[1]);

-- FUNCTIONS
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
      
      if (obj['digit'] == GLOBAL_MENU_MAINMENU) then
		 digits = GLOBAL_MENU_MAINMENU;
		 return "break";
      end

      -- This is tricky.  Note we are checking if the playback is
      -- *already* paused, not whether the user pressed Pause.
      if (digits == GLOBAL_MENU_PAUSE) then
		 digits = "";
		 session:execute("playback", "tone_stream://%(500, 0, 620)");
		 return "pause";
      end
      
      if (obj['digit'] == GLOBAL_MENU_NEXT or obj['digit'] == "#") then
		 digits = GLOBAL_MENU_NEXT;
		 return "break";
      end
      
      if (obj['digit'] == GLOBAL_MENU_RESPOND) then	
		 digits = GLOBAL_MENU_RESPOND;
		 return "break";
      end
      
       if (obj['digit'] == GLOBAL_MENU_INSTRUCTIONS) then
		 read(aosd .. "okinstructions.wav", 500);
		 read(anssd .. "instructions_full.wav", 500);
		 digits = input();
		 return "break";
      end
      
      
      if (obj['digit'] == GLOBAL_MENU_SKIP_BACK) then
		 digits = GLOBAL_MENU_SKIP_BACK;
		 freeswitch.consoleLog("info", script_name .. ".callback() : digits = " .. digits .. "\n");
		 return "break";
      end

      if (obj['digit'] == GLOBAL_MENU_PAUSE) then
	    read(aosd .. "paused.wav", 500);
	    digits = input();
	    if (digits == "") then
	       digits = GLOBAL_MENU_PAUSE;
	       return "pause";
	    else
	       digits = "";
	       session:execute("playback", "tone_stream://%(500, 0, 620)");
	    end
      end

      if (obj['digit'] == GLOBAL_MENU_REPLAY) then
		 digits = GLOBAL_MENU_REPLAY;
		 return "break";
      end

      if (obj['digit'] == GLOBAL_MENU_ASK_LATER) then
	 	digits = GLOBAL_MENU_ASK_LATER;
	 	return "break";
      end
              
      if (obj['digit'] == GLOBAL_MENU_PASS) then
	 	digits = GLOBAL_MENU_PASS;
	 	return "break";
      end
      
      if (obj['digit'] == GLOBAL_MENU_REFER) then
	 	digits = GLOBAL_MENU_REFER;
	 	return "break";
      end
      
   else
      freeswitch.console_log("info", obj:serialize("xml"));
   end
end

-----------
-- MAIN 
-----------

-- check for messages first so that we don't
-- make unnecessary calls

-- cursor:numrows doesn't seem to work for all luasql drivers, so
-- better to just leave it out and take the hit of an extra query
function responder_main()
	check_n_msgs = get_responder_messages(userid);
	msg = check_n_msgs();
	if (msg ~= nil) then
		local lineid = "";
		-- set the language
		query = 		"SELECT line.language, line.number, line.outbound_number, line.id ";
		query = query .. " FROM ao_line line, ao_line_forums line_forum, ao_forum forum, ao_message_forum message_forum ";
		query = query .. " WHERE line.id = line_forum.line_id ";
		query = query .. " AND  line_forum.forum_id = forum.id ";
		query = query .. " AND  message_forum.forum_id = forum.id ";
		query = query .. " AND  message_forum.message_id = " .. msg[1];
		row = row(query);
		
		-- since we joined on message_forum, we are assured
		-- that there was only one line returned by the above.
		-- What we are not doing is adjusting this per message in
		-- this responder's queue, which we will have to do if
		-- a responder belongs to multiple lines (then billing the call is an issue)
		if (row == nil) then
		   -- default
		   aosd = sd .. "forum/eng/";
		else
		   aosd = sd .. "forum/" .. row[1] .. "/";
		   lineid = row[4];
		end	
		
		logfilename = logfileroot .. "responder_" .. lineid .. ".log";
		logfile = io.open(logfilename, "a");
		logfile:setvbuf("line");
	
		-- get admin permissions
		adminrows = rows("SELECT forum_id FROM ao_admin where user_id =  " .. userid);
		adminforum = adminrows();
		while (adminforum ~= nil) do
			-- use the table as a set to make lookup faster
			adminforums[adminforum[1]] = true;
			freeswitch.consoleLog("info", script_name .. " : adminforum = " .. adminforum[1] .. "\n");
			adminforum = adminrows();
		end
		
		-- get from dialer
		local dialstrings = get_table_rows("ao_dialer dialer, ao_line_dialers line_dialers", "line_dialers.line_id="..lineid.." AND dialer.id = line_dialers.dialer_id", "dialer.dialstring_prefix, dialer.dialstring_suffix, dialer.max_parallel_in, dialer.channel_vars, dialer.type");
		local prefixes = {};
		local suffixes = {};
		local maxparallels = {};
		local channel_vars_tbl = {};
		local dialer_types = {};
		local dialstring = dialstrings();
		while (dialstring ~= nil) do
			table.insert(prefixes, dialstring[1]);
			suffixes[dialstring[1]] = dialstring[2];
			table.insert(maxparallels, dialstring[3]);
			channel_vars_tbl[dialstring[1]] = dialstring[4];
			table.insert(dialer_types, dialstring[5]);
			dialstring = dialstrings();
	    end	    
	    -- find a dialer that is available
	    -- assumes the line has dialers with unique prefixes associated.
	    local api = freeswitch.API();
	    DIALSTRING_PREFIX = get_available_line(api, prefixes, maxparallels, dialer_types);
	    DIALSTRING_SUFFIX = suffixes[DIALSTRING_PREFIX] or '';
	    local channel_vars = channel_vars_tbl[DIALSTRING_PREFIX];
	    channel_vars = replace_channel_vars_wildcards(channel_vars);
		
		destination = row[3] or row[2];
		CALLID_VAR = '{ao_responder=true,ignore_early_media=true,origination_caller_id_number='..destination..',origination_caller_id_name='..destination;
		if (channel_vars ~= nil) then
			CALLID_VAR = CALLID_VAR .. ','.. channel_vars .. '}';
		else
			CALLID_VAR = CALLID_VAR .. '}';
		end
		freeswitch.consoleLog("info", script_name .. " : vars = " .. CALLID_VAR .. "\n");
		
		-- script-specific sounds
		anssd = aosd .. "answer/";
	
		-- make the call
		session = freeswitch.Session(CALLID_VAR .. DIALSTRING_PREFIX .. caller .. DIALSTRING_SUFFIX)
		session:setVariable("caller_id_number", caller);
		session:setVariable("playback_terminators", "#");
		session:setHangupHook("hangup");
		session:setInputCallback("my_cb", "arg");
	
		-- wait a while before testing
		pause_for_session_ready();
	
		if (session:ready() == true) then
			logfile:write(sessid, "\t", caller, "\t", destination,
			"\t", os.time(), "\t", "Start call", "\n");
			
			local mainmenu_cnt = 0;
			while (1) do
			   read(anssd .. "welcome.wav", 500);
			   -- ignore any barge-in and move on
			   input();
			   
			   msgs = get_responder_messages(userid);
	
			   -- play messages
			   play_responder_messages(userid, msgs, adminforums);
			   
			   mainmenu_cnt = check_abort(mainmenu_cnt, 5);
			   -- go back to the main menu
			   read(aosd .. "mainmenu.wav", 1000);
			end
				
			hangup(CAUSE_APP_HANGUP);
		end
	end -- close num_rows check
end

status, err = pcall(responder_main)
if status == false and termination_reason ~= NORMAL_HANGUP then
	freeswitch.consoleLog("err", tostring(debug.traceback(err)) .. "\n");
end


