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
   
-----------
-- hangup 
-----------
function hangup(cause)
   local callendtime = os.time();
   logfile:write(sessid, "\t",
		 caller, "\t", destination, "\t",
		 callendtime, "\t", "End call", "\n");
   
   -- if no argument is passed explicitly by the application
   -- then assume the hangup is being invoked by hanguphook,
   -- which passes userdata
   if (type(cause) ~= "string") then   		
		cause = CAUSE_CALLER_HANGUP;
   end
   
   for i,curs in ipairs(opencursors) do
		curs:close();
   end
   
   if (callid ~= nil and callstarttime ~= nil) then
   		local callduration = callendtime - callstarttime;
   		local name_vals = {duration=callduration, hangup_cause="'"..cause.."'"};
		update_table("surveys_call", name_vals, "id = "..callid);
   end
   
   -- cleanup
   con:close();
   env:close();
   logfile:flush();
   logfile:close();
   
   -- hangup
   termination_reason = NORMAL_HANGUP;
   error();
end

-----------
-- transfer_hangup
-- Do everything as above
-- except hangup the session
-----------

function transfer_hangup() 
   logfile:write(sessid, "\t",
		 caller, "\t", destination, "\t",
		 os.time(), "\t", "End call", "\n");

   for i,curs in ipairs(opencursors) do
		curs:close();
   end
   
   -- cleanup
   con:close();
   env:close();
   logfile:flush();
   logfile:close();
   
end

--[[ 
*********************************************************************
****************** pause_for_session_ready ************************** 
*********************************************************************
	For different providers and dialer types (and potentially FS quirks)
	originated calls from Session() take an extra pause of time for
	session:ready() to be actually true. Call this funtion after originating
	a call
	
*********************************************************************
--]]
function pause_for_session_ready()
	-- do it in increments so we don't wait unnecessarily long
	local ready_cnt = 0;
	while (ready_cnt < 10 and session:ready() ~= true) do
		-- session:sleep doesn't work!
		os.execute("sleep 2");
		ready_cnt = ready_cnt + 1;
	end
end

-----------
-- rows 
-----------

function rows (sql_statement)
	local cursor = assert (con:execute (sql_statement));
	local closed = false;
	freeswitch.consoleLog("info", script_name .. " : " .. sql_statement .. "\n");
	table.insert(opencursors, cursor);
	return function ()
		if (closed) then 
			return nil;
		end
		local row = {};
		result = cursor:fetch(row);
		if (result == nil) then
			cursor:close();
			closed = true;
			return nil;
		end
		return row;
	end
end

-----------
-- row 
-----------
function row(sql_statement)
	local cursor = assert (con:execute (sql_statement));
	freeswitch.consoleLog("info", script_name .. " : " .. sql_statement .. "\n");
	local row = {};
	result = cursor:fetch(row);
	cursor:close();
	if (result == nil) then
		return nil;
	else
		return row;
	end
end


-----------
-- sleep
-----------

function sleep(delay)
   return read("", delay);
end


-----------
-- read
-----------

function read(file, delay, len)
   local len = len or 1;
   if (digits == "") then
      logfile:write(sessid, "\t",
		    caller, "\t", destination, "\t",
		    os.time(), "\t", "Prompt", "\t", file, "\n");
	  -- timeout (4th) param delays forever if it is set to 0, so make it at least 1ms
      digits = session:playAndGetDigits (1, len, 1, math.max(delay,1), "#", file, "", "\\d+|\\w+|\\*", "", math.max(delay,MULTI_DIGIT_INPUT_THRESH));
      if (digits ~= "") then
	 logfile:write(sessid, "\t", caller, "\t", destination, "\t", os.time(), "\t", "dtmf", "\t", file, "\t", digits, "\n"); 
      end
   end
end

-----------
-- read_no_bargein
-----------

function read_no_bargein(file, delay)
	logfile:write(sessid, "\t",
		    caller, "\t", destination, "\t",
		    os.time(), "\t", "Prompt", "\t", file, "\n");
    session:streamFile(file);
    sleep(delay);
    -- ignore all input
    input();
end

--[[
-------------------------------------------
----------------- input ------------------- 
-------------------------------------------

	used to be use() 
	changed for compatibility with forward.lua

-------------------------------------------
--]]

function input()
   local d = digits;
   digits = "";
   -- need the below so any input from the stream
   -- doesn't carry over to the next
   session:flushDigits();
   return d;
end

-----------
-- speak
-----------
function speak(phrase)
   if (digits == "") then
      logfile:write(sessid, "\t",
		    caller, "\t", destination, "\t",
		    os.time(), "\t", "Speak", "\t", phrase, "\n");
      session:speak(phrase);
   end
end

-----------
-- playcontent
-----------

function playcontent (content)
   local d;
   
   arg[1] = sd .. content;
   logfile:write(sessid, "\t",
		 caller, "\t", destination, "\t",
		 os.time(), "\t", "Stream", "\t", arg[1], "\n");

   session:streamFile(sd .. content);
   sleep(3000);
   
   return input();
end

--[[
-------------------------------------------
------------- play_prompt ---------------- 
-------------------------------------------
--]]
function play_prompt(promptname, delay, promptsd)
	delay = delay or DEF_INPUT_DELAY;
	promptsd = promptsd or sd;
	if (promptsd:sub(-1) ~= '/') then
		-- add trailing slash
		promptsd = promptsd .. '/';
	end
	local promptfile = promptname..PROMPT_SOUND_EXT;
	freeswitch.consoleLog("info", script_name .. " : playing prompt " .. promptsd .. promptfile .. "\n");
	read(promptsd .. promptfile, delay);
end
-----------
-- recordmessage
-----------

function recordmessage (forumid, thread, moderated, maxlength, rgt, adminmode, confirm, okrecordedprompt)
   maxlength = tonumber(maxlength);
   rgt = tonumber(rgt) or 1;
   confirm = tonumber(confirm);
   local okrecordedprompt = okrecordedprompt or aosd .. "okrecorded.wav";
   local mediasubdir = get_media_subdir();
   -- add caller digits to prevent name collisions
   local partfilename = mediasubdir..os.time() .. caller:sub(caller:len()-1) .. RECORD_SOUND_EXT;
   local filename = recordsd .. partfilename;

   repeat
      read(aosd .. "pleaserecord.wav", 1000);
      local d = input();

      if (d == GLOBAL_MENU_MAINMENU) then
	 return d;
      end

      session:execute("playback", "tone_stream://%(500, 0, 620)");
      freeswitch.consoleLog("info", script_name .. " : Recording " .. filename .. "\n");
      logfile:write(sessid, "\t",
		    caller, "\t", destination, "\t", 
		    os.time(), "\t", "Record", "\t", filename, "\n");
      session:execute("record", filename .. " " .. maxlength .. " 100 5");
      --sleep(1000);
      d = input();
      
      if (confirm == 1) then
	      local review_cnt = 0;
	      while (d ~= GLOBAL_MENU_MAINMENU and d ~= "1" and d ~= "2" and d ~= "3") do
			 read(aosd .. "hererecorded.wav", 1000);
			 read(filename, 1000);
			 read(aosd .. "notsatisfied.wav", 2000);
			 sleep(6000)
			 d = input();
			 review_cnt = check_abort(review_cnt, 3)
	      end
	      
	     if (d ~= "1" and d ~= "2") then
		 	 os.remove(filename);
			 if (d == GLOBAL_MENU_MAINMENU) then
			    return d;
			 elseif (d == "3") then
			    read(aosd .. "messagecancelled.wav", 500);
			    return input();
			 end
	     end
	  else
	  	 d = "1";
	  end
   until (d == "1");
   
   query1 = "INSERT INTO ao_message (user_id, file, date";
   query2 = " VALUES ("..userid..",'"..partfilename.."',".."now()";
   
   if (thread ~= nil) then -- this is a response
      query = "UPDATE ao_message SET rgt=rgt+2 WHERE rgt >=" .. rgt .. " AND (thread_id = " .. thread .. " OR id = " .. thread .. ")";
      con:execute(query);
      freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n")
      query = "UPDATE ao_message SET lft=lft+2 WHERE lft >=" .. rgt .. " AND (thread_id = " .. thread .. " OR id = " .. thread .. ")";
      con:execute(query);
      freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n")
      query1 = query1 .. ", thread_id, lft, rgt)";
      query2 = query2 .. ",'" .. thread .. "','" .. rgt .. "','" .. rgt+1 .. "')";
   else
      query1 = query1 .. ", lft, rgt)";
      query2 = query2 .. ", 1, 2)";
   end
   
   query = query1 .. query2;
   con:execute(query);
   freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n")
   id = {};
   cur = con:execute("SELECT LAST_INSERT_ID()");
   cur:fetch(id);
   cur:close();
   freeswitch.consoleLog("info", script_name .. " : ID = " .. tostring(id[1]) .. "\n");
   
   query1 = "INSERT INTO ao_message_forum (message_id, forum_id, last_updated";
   query2 = " VALUES ("..id[1]..","..forumid..",now()";
      
   local position = "null";
   if (moderated == 'y' and not adminmode) then
	 status = MESSAGE_STATUS_PENDING;
   else
	 status = MESSAGE_STATUS_APPROVED; 
	 if (thread == nil) then
		    cur = con:execute("SELECT MAX(mf.position) from ao_message_forum mf, ao_message m WHERE mf.message_id = m.id AND m.lft = 1 AND mf.forum_id = " .. forumid .. " AND mf.status = " .. MESSAGE_STATUS_APPROVED );
		    -- only set position if we have to
		    pos = cur:fetch();
		    cur:close();
		    if (pos ~= nil) then 
		       position = tonumber(pos) + 1;
		    end
	 end
   end
   query1 = query1 .. ", status, position)";
   query2 = query2 .. "," .. status .. ",".. position..")";
   
   query = query1 .. query2;
   con:execute(query);
   freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n")

   read(okrecordedprompt, 500);
   return input();
end


-----------
-- check_abort
-----------

function check_abort(counter, threshold)
	counter = counter + 1;
	if (counter >= threshold) then
		logfile:write(sessid, "\t", caller, "\t", destination, "\t", os.time(), "\t", "Abort call", "\n");
		hangup(CAUSE_NO_RESP_HANGUP);
	else
		return counter;
	end
end

-----------
-- is_admin 
-----------

function is_admin(forumid, forums) 
	if (forumid == nil) then
		local numItems = 0;
		for k,v in pairs(forums) do
		    numItems = numItems + 1;
		end
		
		return numItems > 0;
	else
		return forums[forumid] == true;
	end
end

-----------
-- trim (string) 
-----------
function trim (s)
	return (string.gsub(s, "^%s*(.-)%s*$", "%1"))
end

--[[
-------------------------------------------
------------- is_sufficient_balance ------- 
-------------------------------------------

	Check the given user's balance and return
	true or false if the person has sufficient
	balance.

	Method is required for forward.lua
-------------------------------------------
--]]
function is_sufficient_balance(userid)
	if (userid == nil) then
		-- could happen if the survey app in question is pure
		-- survey with no inbound app, hence no automatic
		-- way to create a user
		return false;
	else
		local balance = get_table_field("ao_user", "balance", "id="..userid);
		balance = tonumber(balance);
		return balance ~= nil and (balance > 0 or balance == -1);
	end
end

--[[
-------------------------------------------
------------- get_num_channels ------------ 
-------------------------------------------

	Given a profile, return the number of
	current occupied channels
-------------------------------------------
--]]
function get_num_channels(api, prefix, dialer_type)
	local profile = "";
	dialer_type = tonumber(dialer_type);
	if  (dialer_type == DIALER_TYPE_PRI) then
		local pri = string.match(prefix,'grp(%d+)');
		profile = 'FreeTDM/'.. tostring(pri);
	else -- SIP
		-- NOTE THIS ASSUMES profile name is same as gateway name
		-- FS show channels names calls by profile name, not gateway name.
		-- so if we need multiple gateways in a profile that could be a problem 
		-- if it there is not physical limit to SIP calls, safe to not worry about
		-- naming the gateway in any particular way
		local gateway = string.match(prefix,"sofia/gateway/([%w%p]+)/");
		profile = 'sofia/'..tostring(gateway);
	end
	local status_str = "show channels like " .. profile;
	--freeswitch.consoleLog("info", script_name .. " : executing " .. status_str .."\n");
	local reply = api:executeString(status_str);
	--freeswitch.consoleLog("info", script_name .. " : reply =  " .. reply);
 	reply = trim(reply);
	
	local pattern = "(%d+) total.";
	local num = reply:match(pattern);
	
	--freeswitch.consoleLog("info", script_name .. " : num channels for " .. profile ..": " .. num .. "\n");
	return tonumber(num);
end

--[[
-------------------------------------------
------- get_available_inbound_line --------
-------------------------------------------

	Find an available channel from the given
	set of dialer db rows
-------------------------------------------
--]]
function get_available_line(api, prefixes, maxparallels, dialer_types)
	local nchannels = nil;
	
	for i,prefix in ipairs(prefixes) do
		nchannels = get_num_channels(api, prefix, dialer_types[i]);
		if (nchannels < tonumber(maxparallels[i])) then
			return prefix;
		end
	end
	
	-- means all qualified dialers are full. Return nothing
end

--[[
-------------------------------------------
------- get_media_subdir ------------------
-------------------------------------------

	Returns the prefix for a media file.
	Currently media files are stored by
	date, so return the current year/month/day/
-------------------------------------------
--]]
function get_media_subdir()
	local d = os.date('*t');
	local year = d.year;
	local month = d.month;
	local day = d.day;
	
	if month < 10 then
		month = '0'..month;
	end
	
	if day < 10 then
		day = '0'..day;
	end
	
	local subdir = year..'/'..month..'/'..day..'/';
	
	-- create it if it doesn't already exist
	if io.open(recordsd .. subdir,"rb") == nil then
		os.execute("mkdir -p "..recordsd..subdir);
		-- chmod from the file's root on down
		os.execute("chmod -R 775 "..recordsd..year);
	end
	
	return subdir;
end

--[[
-------------------------------------------
------ replace_channel_vars_wildcards -----
-------------------------------------------
--]]
function replace_channel_vars_wildcards(channel_vars)
	if (channel_vars == nil or channel_vars == '') then
		return nil;
	end
	
	-- add all supported wildcards here for substitutions
	channel_vars = channel_vars:gsub('__destination__', outbound_number or destination);
	
	return channel_vars;
end

--[[ 
**********************************************************
********* BEGIN COMMON RESPONDER FUNCTIONS
**********************************************************
--]]

-- App-specific GLOBALS
GLOBAL_MENU_RESP_REPLAY = "6";
GLOBAL_MENU_ASK_LATER = "7";
GLOBAL_MENU_PASS = "8";
GLOBAL_MENU_REFER = "9";
GLOBAL_MENU_CANCEL_REFERRAL = "*";

-- The ground truths; sh be consistent with views.py
RESERVE_PERIOD = "2"
LISTENS_THRESH = "5"

-----------
-- read_phone_num
-----------

function read_phone_num(file, delay)
   if (digits == "") then
      logfile:write(sessid, "\t",
		    caller, "\t", destination, "\t",
		    os.time(), "\t", "Prompt", "\t", file, "\n");
	  -- allow 1 or 10 (1 to cancel)
      digits = session:read(1, 10, file, delay, "#");
      if (digits ~= "") then
	 logfile:write(sessid, "\t", caller, "\t", destination, "\t", os.time(), "\t", "dtmf", "\t", file, "\t", digits, "\n"); 
      end
   end
end

-----------
-- get_responder_messages
-----------

function get_responder_messages (userid, lineid)
   local query = "SELECT message.id, message.file, message.rgt, message_forum.forum_id, message_forum.id, forum.moderated, message.thread_id, forum.max_responder_len ";
   query = query .. " FROM ao_message message, ao_message_forum message_forum, ao_message_responder message_responder, ao_forum forum ";
   query = query .. " WHERE message.id = message_forum.message_id";
   query = query .. " AND forum.id = message_forum.forum_id ";
   query = query .. " AND message_responder.message_forum_id = message_forum.id ";
   query = query .. " AND message_responder.user_id = " .. userid;
   
   -- temporarily rolling back this part with the join
   -- because this query is bogging things down
   --[[
   if (lineid ~= nil) then
   		query = query .. " AND line.id = " .. lineid;
   		query = query .. " AND lf.line_id = line.id AND lf.forum_id = forum.id ";
   		query = query .. " AND message_forum.forum_id = forum.id ";
   end
   --]]
   
   -- Next part says to only select messages
   -- for response if this user hasn't already
   -- responded to it message
   query = query .. " AND NOT EXISTS (SELECT 1 ";
   query = query .. "			  FROM ao_message msg ";
   query = query .. "			  WHERE ( (message.thread_id IS NULL AND msg.thread_id = message.id) OR ";
   query = query .. "			  		  (message.thread_id IS NOT NULL AND msg.thread_id = message.thread_id) )";
   query = query .. "			  AND msg.lft BETWEEN message.lft AND message.rgt AND NOT EXISTS (SELECT 1";
   query = query .. "			   														FROM ao_message msg2 ";
   query = query .. "			   														WHERE msg2.thread_id = msg.thread_id ";
   query = query .. "			   														AND msg2.lft > message.lft AND msg2.lft < message.rgt ";
   query = query .. "			   														AND msg.lft > msg2.lft AND msg.rgt < msg2.rgt ) ";
   query = query .. "			  AND msg.user_id = " .. userid ..") ";
   -- END part referenced above
   query = query .. " AND message_responder.listens <= " .. LISTENS_THRESH;
   query = query .. " AND message_responder.passed_date IS NULL ";
   query = query .. " AND (message_responder.reserved_by_id IS NULL ";
   query = query .. "      OR (message_responder.reserved_until > now() AND message_responder.reserved_by_id = " .. userid .. " ) ";
   query = query .. " 	   OR message_responder.reserved_until < now() ) ";
   query = query .. " ORDER BY message.date DESC";
   return rows(query);
end

-----------
-- ask_later
-----------

function ask_later (userid, messageforumid)
   local query = "UPDATE ao_message_responder ";
   query = query .. " SET reserved_by_id = " .. userid .. " , reserved_until = now() + INTERVAL " .. RESERVE_PERIOD .. " DAY ";
   query = query .. " WHERE message_forum_id = " .. messageforumid;
   con:execute(query);
   freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
end

-----------
-- pass_question
-----------

function pass_question (userid, messageforumid)
   local query = "UPDATE ao_message_responder ";
   query = query .. " SET passed_date = now() ";
   query = query .. " WHERE message_forum_id = " .. messageforumid .. " AND user_id = " .. userid;
   con:execute(query);
   freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
end

-----------
-- refer_question
-----------
function refer_question(ph_num, messageforumid)
	query = "SELECT id FROM ao_user where number = ".. ph_num;
	cur = con:execute(query);
	row = {};
	result = cur:fetch(row);
	cur:close();
	
	if (result == nil) then
	   -- unregistered number
	   query = "INSERT INTO ao_user (number, allowed) VALUES ('" .. ph_num .."','y')";
	   con:execute(query);
	   freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n");
	   cur = con:execute("SELECT LAST_INSERT_ID()");
	   uid = tostring(cur:fetch());
	   cur:close();
	else
	   uid = tostring(row[1]);
	end	
	
	-- create referal
	query = "INSERT INTO ao_message_responder (message_forum_id, user_id) VALUES (" ..messageforumid..", " .. uid ..")";
	freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n");
	con:execute(query);
	
	read(anssd .. "okreferral.wav", 500);
	   
end

-----------
-- update_listens
-----------

function update_listens (msgs, userid)
	-- build msg_id list
	local msg_forum_id_list = "(";
	for i,msg in ipairs(msgs) do
		msg_forum_id_list = msg_forum_id_list .. msg[1] .. ", ";
	end
	-- remove trailing space and comma
	msg_forum_id_list = msg_forum_id_list:sub(1, -3);
	-- close list
	msg_forum_id_list = msg_forum_id_list .. ")";
	
   local query = "UPDATE ao_message_responder ";
   query = query .. "SET listens = listens + 1 ";
   query = query .. "WHERE message_forum_id in " .. msg_forum_id_list .. " AND user_id = " .. userid;
   con:execute(query);
   freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
end

-----------
-- play_responder_message
-----------

function play_responder_message (msg)
  local id = msg[1];
  local content = msg[2];

  d = playcontent(content);
  
  -- remind about the options, and
  -- give some time for users to compose themselves and
  -- potentially respond
  if (d == "" or d == GLOBAL_MENU_NEXT) then
  	read(anssd .. "instructions_short.wav", 5000)
  else
  	return d;
  end
  
  d = input();
  if (d ~= "") then
  	return d;
  else
	  -- default	
	  return GLOBAL_MENU_NEXT;
  end
end


-----------
-- play_responder_messagess
-----------

function play_responder_messages (userid, msgs, adminforums)
   -- get the first top-level message for this forum
   local current_msg = msgs();
   if (current_msg == nil) then
      read(aosd .. "nomessages.wav", 1000);
      return input();
   end

   prevmsgs = {};
   table.insert(prevmsgs, current_msg);
   local current_msg_idx = 1;
   local d = "";
   
   while (current_msg ~= nil) do
      if (d == GLOBAL_MENU_INSTRUCTIONS) then
		 -- if last msg played recd a response
		 read(aosd .. "backtomessage.wav", 1000);
	  elseif (d == GLOBAL_MENU_RESP_REPLAY) then
	     -- do nothing
      elseif (current_msg_idx == 1) then
      	 -- do this before prev check b/c 
		 -- its helpful to know when u are at the first message
		 read(aosd .. "firstmessage.wav", 1000);
      elseif (d == GLOBAL_MENU_SKIP_BACK) then  
	 	read(aosd .. "previousmessage.wav", 1000);
      else -- default
	 	read(aosd .. "nextmessage.wav", 1000);
      end

      d = input();
      -- check if a pre-emptive action was taken
      -- don't listen for pre-emptive actions that require
      -- listening to the message at least a little. Make an
      -- exception for responses which we want to encourage
      if (d ~= GLOBAL_MENU_MAINMENU and d ~= GLOBAL_MENU_SKIP_BACK and d ~= GLOBAL_MENU_SKIP_FWD and d ~= GLOBAL_MENU_RESPOND and d ~= GLOBAL_MENU_INSTRUCTIONS) then
	 	d = play_responder_message(current_msg);
      end
      
      if (d == GLOBAL_MENU_INSTRUCTIONS) then
	  	 read(aosd .. "okinstructions.wav", 500);
		 read(anssd .. "instructions_full.wav", 500);
		 
		 d = input();
	  end
      
      if (d == GLOBAL_MENU_RESPOND) then
	    read(aosd .. "okrecordresponse.wav", 500);
	    local thread = current_msg[7] or current_msg[1];
	    local forumid = current_msg[4];
	    local rgt = current_msg[3];
	    local moderated = current_msg[6];
	    local adminmode = is_admin(forumid, adminforums);
	    local okrecordedprompt = anssd .. "okrecorded.wav";
	    local maxlength = current_msg[8] or MAX_RESPONDER_LEN_DEF;
	    d = recordmessage (forumid, thread, moderated, maxlength, rgt, adminmode, 1, okrecordedprompt);
	    if (d == GLOBAL_MENU_MAINMENU) then
	    	update_listens(prevmsgs, userid);
	       return d;
	    else
	       d = GLOBAL_MENU_NEXT;
	    end
      elseif (d == GLOBAL_MENU_SKIP_BACK) then
		 if (current_msg_idx > 1) then
		    current_msg_idx = current_msg_idx - 1;
		    current_msg = prevmsgs[current_msg_idx];
		 end
	  elseif (d == GLOBAL_MENU_ASK_LATER) then
	  	local msgforumid = current_msg[5];
	  	ask_later(userid, msgforumid);
	  	read(anssd .. "asklater.wav", 500);
	  	d = GLOBAL_MENU_NEXT;
	  elseif (d == GLOBAL_MENU_PASS) then
	  	local msgforumid = current_msg[5];
	  	pass_question(userid, msgforumid);
	  	read(anssd .. "passquestion.wav", 500);
	  	d = GLOBAL_MENU_NEXT;
	  elseif (d == GLOBAL_MENU_REFER) then

	  	read_phone_num(anssd .. "referquestion.wav", 3000);
		d = input();
		local phone_num_cnt = 0;
	  	while (d ~= GLOBAL_MENU_CANCEL_REFERRAL and string.len(d) ~= 10) do
		  	session:execute("playback", "tone_stream://%(500, 0, 620)");
		  	read_phone_num("", 3000);
		  	d = input();
		  	
		  	if (d ~= GLOBAL_MENU_CANCEL_REFERRAL and string.len(d) ~= 10) then
	  			read(anssd .. "invalidphonenum.wav",500)
	  		end
	  		phone_num_cnt = check_abort(phone_num_cnt, 4);
	  	end
	  	
	  	if (d == GLOBAL_MENU_CANCEL_REFERRAL) then
	  		read(aosd .. "messagecancelled.wav", 500);
	  	else
	  		local msgforumid = current_msg[5];
	  		refer_question(d, msgforumid);
	  	end
	  	
	  	-- go to next msg
	  	d = GLOBAL_MENU_NEXT;
      elseif (d == GLOBAL_MENU_RESP_REPLAY) then
		-- do nothing
	  end
	  
      if (d == GLOBAL_MENU_NEXT) then
	  	current_msg_idx = current_msg_idx + 1;
		-- check to see if we are at the last msg in the list
	 	if (current_msg_idx > #prevmsgs) then
		    -- get next msg from the cursor
		    current_msg = msgs();
		    if (current_msg == nil) then
		       read(aosd .. "lastmessage.wav", 1000);
		       d = input(); 
		       if (d == GLOBAL_MENU_SKIP_BACK) then
				  current_msg_idx = current_msg_idx - 1;
				  current_msg = prevmsgs[current_msg_idx];
		       end
		    else
		       table.insert(prevmsgs, current_msg);
		    end
		else
		    -- get msg from the prev list
		    current_msg = prevmsgs[current_msg_idx];
	    end
	  end
      
      if (d == GLOBAL_MENU_MAINMENU) then
      	update_listens(prevmsgs, userid);
	 	return d;
      end
   end -- end while
   update_listens(prevmsgs, userid);
end

--[[ 
**********************************************************
********* END COMMON RESPONDER FUNCTIONS
**********************************************************
--]]

--[[ 
**********************************************************
********* BEGIN COMMON SURVEY FUNCTIONS
**********************************************************
--]]

-----------
-- get_prompts
-----------

function get_prompts(surveyid)
	local query = 	"SELECT id, file, bargein, delay, inputlen, dependson_id, survey_id, random ";
	query = query .. " FROM surveys_prompt ";
	query = query .. " WHERE survey_id = " .. surveyid;
	query = query .. " ORDER BY surveys_prompt.order ASC ";
	return rows(query);
end

-----------
-- get_option
-----------

function get_option (promptid, number)
   local query = " SELECT opt.id, opt.action";
   query = query .. " FROM surveys_option opt, surveys_prompt prompt ";
   query = query .. " WHERE prompt.id = " .. promptid;
   query = query .. " AND opt.prompt_id = prompt.id ";
   query = query .. " AND opt.number = '" .. number .. "' ";
   return row(query)
end

-----------
-- get_params
-----------

function get_params (optionid)
   local query = " SELECT param.name, param.value ";
   query = query .. " FROM surveys_option opt, surveys_param param ";
   query = query .. " WHERE opt.id = " .. optionid;
   query = query .. " AND param.option_id = opt.id ";
   local params = rows(query);
   local paramtbl = {};
   local current_param = params();
   while (current_param ~= nil) do
  	paramtbl[current_param[1]] = current_param[2];
	current_param = params();
   end
   return paramtbl;
end

-----------
-- set_survey_complete
-----------

function set_survey_complete (callid)
   if (callid ~= nil) then
   	local query = " UPDATE surveys_call ";
   	query = query .. " SET complete = 1 ";
   	query = query .. " WHERE id = " .. callid;
   	con:execute(query);
   	freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
   end
end

-----------
-- play_prompts
-----------

function play_prompts (prompts)
   -- get the first prompt
   local current_prompt = prompts();
   local prevprompts = {};
   table.insert(prevprompts, current_prompt);
   local current_prompt_idx = 1;
   local d = "";
   local inputval = "";
   local replay_cnt = 0;
   local optionid = "";
   local action = nil;
   local randomized_prompts = nil;
   
   -- a complete_after 0 means it's complete if they've picked up the call
   if (complete_after_idx ~= nil and complete_after_idx == 0) then
   	  	set_survey_complete(callid);
   end
   
   while (current_prompt ~= nil) do
   	  local promptid = current_prompt[1];
   	  local promptfile = current_prompt[2];
   	  local bargein = tonumber(current_prompt[3]);
   	  local delay = tonumber(current_prompt[4]);
   	  local inputlen = tonumber(current_prompt[5]);
   	  local dependson = tonumber(current_prompt[6]);
   	  local surveyid = tonumber(current_prompt[7]);
   	  local random = tonumber(current_prompt[8]);
   	  
   	  if (dependson ~= nil) then
   	  	local query = "SELECT input FROM surveys_input ";
   	  	query = query .. " WHERE call_id = ".. callid;
   	  	query = query .. " AND prompt_id = ".. dependson;
   	  	query = query .. " ORDER BY id DESC ";
		result = row(query);
		
		if (result == nil) then
			result = "blank";
		else
			result = result[1]
		end
		
		-- assumes orig promptfile has trailing slash
		promptfile = promptfile .. result .. ".wav";
	  end
		
   	  freeswitch.consoleLog("info", script_name .. " : playing prompt " .. promptfile .. "\n");	  
   	  
   	  if (random == 1) then
   	  	  -- preserve (i.e. don't reset) randomized order of 
   	  	  -- the random prompt if it is repeating itself
   	  	  if (action ~= OPTION_REPLAY) then
   	  	  	randomized_prompts = nil;
   	  	  end
   	  	  randomized_prompts = play_random_prompt(current_prompt, promptfile, randomized_prompts);
   	  else
	   	  if (bargein == 1) then
	   	  	if (promptfile:sub(0,1) == '/') then
	   	  		-- DEPRECATED: no files should have absolute paths for the sake of remote file access
	   	  		read(promptfile, delay, inputlen);
	   	  	else
	   	  		read(sd .. promptfile, delay, inputlen);
	   	  	end
	  	  else
	  	  	if (promptfile:sub(0,1) == '/') then
	  	  		-- DEPRECATED: no files should have absolute paths for the sake of remote file access
	  	  		read_no_bargein(promptfile, delay);
	  	  	else
	  			read_no_bargein(sd .. promptfile, delay);
	  		end
	   	  end
	  end
   	  
   	  -- Do this check right after the prompt plays in case of there are no more prompts
	  if (complete_after_idx ~= nil and current_prompt_idx == complete_after_idx) then
   	  	set_survey_complete(callid);
   	  end
   	  
   	  d = input();
   	  inputval = d;
   	  
   	  -- get option
   	  local option = nil;
   	  if (random == 1) then
   	  	option = randomized_prompts[inputval];
   	  else
   	  	option = get_option(promptid, inputval);
   	  end
   	  
   	  if (option ~= nil) then
   	  	optionid = tonumber(option[1]);
   	  	action = tonumber(option[2]);
   	  elseif (inputval ~= "" and inputlen ~= nil and inputlen > 0 and inputlen >= string.len(tostring(inputval))) then
   	  	-- there is no specific option, it is a range
   	  	-- The check for input being non-empty means that on no input the prompt will
   	  	-- always repeat on a multiple-digit input prompt. This is actually correct. To
   	  	-- get it to go forward on no-input, simply add the Option (since we check for options first).
   	  	optionid = nil;
   	  	action = OPTION_INPUT;
   	  else
   	  	-- default: repeat which is safer than NEXT since bad input
		-- will make the prompt be skipped. Downside is that prompts have to have
		-- an explicit option for no input, though this is probably better practice.
   	  	action = OPTION_REPLAY;
   	  end
      
      freeswitch.consoleLog("info", script_name .. " : option selected - " .. tostring(action) .. "\n");
      
      -- abort if 3 replays for any prompt in a row
      if (action == OPTION_REPLAY) then
		replay_cnt = check_abort(replay_cnt, 3);
      else
		replay_cnt = 0;
      end

      -- keep together all options which have a goto IDX param
      -- in order to avoid duplicating the code that checks the
      -- param and sets the current_prompt_idx accordingly
      if (action == OPTION_INPUT or action == OPTION_FORWARD) then
      	local params = nil;
      	if (optionid ~= nil) then
      		params = get_params(optionid);
      	end
      	
      	if (action == OPTION_INPUT) then
	      	-- in case there is a data for this option
	      	-- that should be inputted instead of the raw dialed number.
	      	-- Used for passing prompt names for conditional prompts.
		   	if (params ~= nil and params[OPARAM_NAME] ~= nil) then
		   		inputval = params[OPARAM_NAME];
		   	end
		    query = 		 "INSERT INTO surveys_input (call_id, prompt_id, input) ";
	   		query = query .. " VALUES ("..tostring(callid)..","..promptid..",'"..inputval.."')";
	   		con:execute(query);
	   		freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n");
	   elseif (action == OPTION_FORWARD) then
	   		-- required param
	   		local mfid = params[OPARAM_MFID];
	   		local promptsd = params[OPARAM_FWD_PROMPT_PATH];
	   		if (promptsd ~= nil) then
	   			promptsd = sd .. promptsd;
	   		end
	   		local msginfo = get_table_one_row("ao_message_forum mf", "mf.id = "..mfid, "mf.message_id, mf.forum_id");	   		
	   		forward(userid, msginfo[1], msginfo[2], surveyid, promptsd);
	   end
   		
   		local goto_idx = nil;
   		if (params ~= nil and params[OPARAM_IDX] ~= nil) then
   			goto_idx = tonumber(params[OPARAM_IDX]);
   		end
   		
   		if (goto_idx == nil) then
   			goto_idx = current_prompt_idx + 1;
   		end
		-- check to see if we are at the last msg in the list
	 	if (goto_idx > #prevprompts) then
		    for i=#prevprompts+1, goto_idx do
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
      elseif (action == OPTION_NEXT) then
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
	  	local goto_idx = tonumber(get_params(optionid)[OPARAM_IDX]);
		-- check to see if we are at the last msg in the list
	 	if (goto_idx > #prevprompts) then
		    for i=#prevprompts+1, goto_idx do
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
	  elseif (action == OPTION_RECORD) then
	  	local params = get_params(optionid);
	    local maxlength = tonumber(params[OPARAM_MAXLENGTH]);
	    local oncancel = tonumber(params[OPARAM_ONCANCEL]);
	    local mfid = tonumber(params[OPARAM_MFID]);
	    local confirm = tonumber(params[OPARAM_CONFIRM_REC]);
		-- assume recording prompts are
		-- in the same folder as the prompt that
		-- got us to the recording step
    	--freeswitch.consoleLog("info", script_name .. " found path: " .. promptfile .. "\n");
    	local pathend = promptfile:find("[a-zA-Z-_0-9]+\.wav") - 2;
    	local lang = promptfile:sub(1,pathend);
	    --freeswitch.consoleLog("info", script_name .. " lang is: " .. lang .. "\n");
	  	outcome = recordsurveyinput(callid, promptid, lang, maxlength, mfid, confirm);
	  	-- move forward by default. Why? bc it seems overkill to have a goto as well
	  	-- if you need a goto, build it into the next prompt with a blank recording
	  	local goto_idx = current_prompt_idx + 1;
	  	if (outcome == "3" and oncancel ~= nil) then
	  		goto_idx = oncancel;
	  	end
		-- check to see if we are at the last msg in the list
	 	if (goto_idx > #prevprompts) then
		    for i=#prevprompts+1, goto_idx do
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
	  elseif (action == OPTION_TRANSFER) then
	  	local number = get_params(optionid)[OPARAM_NUM];
	  	session:setAutoHangup(false);
	  	session:setHangupHook("transfer_hangup");
        session:transfer(number, "XML", "default");
	  end
    
   end -- end while
   
   -- if survey doesn't specify a finished prompt,
   -- that means the survey is finished after all prompts
   -- have been heard
   if (complete_after_idx == nil) then
   		set_survey_complete(callid);
   end
end

--[[ 
*********************************************************************
****************** play_random_prompt ******************************* 
*********************************************************************
	Pass in promptfile separately in case the filename was dyanmically
	altered based on a depending prompt. Pass in randomized_opts in case
	you want to fix the ordering (like when the question repeats on
	none or invalid input).
	
	1. Play the fixed beginning
	2. determine which sub-prompt options are static
		and which options are to be randomized
	3. Assign an ordering with static subprompts set
		and random subprompts randomized
	4. Play the subprompts in the randomized ordering
	
	Return the prompt ordering back to interpret the input
*********************************************************************
--]]

function play_random_prompt (prompt, promptfile, randomized_opts)
	local promptid = prompt[1];
  	local bargein = tonumber(prompt[3]);
  	local delay = tonumber(prompt[4]);
  	local inputlen = tonumber(prompt[5]);
  	
	-- numbers dir. Unzip makes everything flat
	local pathend = promptfile:find("[a-zA-Z-_0-9]+\.wav") - 1;
    local nums_sd  = sd .. promptfile:sub(1,pathend);
	
	-- remove the extension if it's there (may not be if it's a dependent prompt)
	promptfile = promptfile:gsub(SOUND_EXT,'');
		
	-- arrange the subprompts in the order
	-- that they should play
	local subprompts = {};
	if (randomized_opts == nil) then
		randomized_opts = {};
		local random_opts = {};
		local random_slots = {};
		
		-- get options. Get action for the return value (randomized_prompts). The caller will need it
		local options = get_table_rows("surveys_option", "prompt_id = "..promptid .. " AND number != ''", "id, action, number");
		local opt = options();
		-- gather the random and static options individually
		while (opt ~= nil) do
			local optionid = opt[1];
			local number = opt[3];
			local params = get_params(optionid);
			freeswitch.consoleLog("info", script_name .. " found opt: " .. optionid .. " number: " .. number .. "\n");
			if (next(params) ~= nil and params[OPARAM_NAME] ~= nil) then
				-- to be randomized, since it has a symbolic name
				table.insert(random_opts, opt);
				table.insert(random_slots, number);
				freeswitch.consoleLog("info", script_name .. " to be randomized \n");
			else
				-- static prompt, slot into the final play list
				-- index +1 accounting for the starting static prompt
				subprompts[tonumber(number)] = promptfile .. '-opt' .. number .. SOUND_EXT;
				randomized_opts[number] = opt;
				freeswitch.consoleLog("info", script_name .. " to be static \n");
			end
			opt = options();
		end
		
		--freeswitch.consoleLog("info", script_name .. ": random_slots= "..  table.tostring(random_slots) .."\n");
	    --freeswitch.consoleLog("info", script_name .. ": random_opts= "..  table.tostring(random_opts) .."\n");
		-- assign the random opts to slots
		for i,slot in ipairs(random_slots) do
			-- get random subprompt
			local idx = math.random(#random_opts);
			local subprompt = random_opts[idx];
			-- assign the slot
			subprompts[tonumber(slot)] = promptfile .. '-opt' .. subprompt[3] .. SOUND_EXT;
			freeswitch.consoleLog("info", script_name .. " assigned slot: " .. slot .. " subprompt: " .. promptfile .. '-opt' .. subprompt[3] .. "\n");
			-- remove the subprompt from consideration for next slot(s)
			table.remove(random_opts,idx);
			-- need to make it string because this will
			-- be indexed on dtmf input value in play_prompts
			-- (and also to be consistent with indexing of static subprompts)
			randomized_opts[tostring(slot)] = subprompt;
		end
	else
		-- make sure subprompts is number indexed to work with ipairs below
		for i,subprompt in pairs(randomized_opts) do
			subprompts[tonumber(i)] = promptfile .. '-opt' .. subprompt[3] .. SOUND_EXT;
		end
	end
	--freeswitch.consoleLog("info", script_name .. ": subprompts= "..  table.tostring(subprompts) .."\n");
	
	-- Prompt always starts off with a static part (question)
	if (bargein == 1) then
		read(sd.. promptfile .. SOUND_EXT, 0, inputlen);
	else
		read(sd .. promptfile .. SOUND_EXT, 0);
	end
	-- play the subprompts in the randomized ordering
	for i,subprompt in ipairs(subprompts) do
		freeswitch.consoleLog("info", script_name .. " playing subprompt " .. subprompt .. " with num " .. tostring(i) .. "\n");
		if (bargein == 1) then
		  	read(sd .. subprompt, 0, inputlen);
		  	read(nums_sd .. tostring(i) .. SOUND_EXT, 0, inputlen);
		else
			read_no_bargein(sd .. subprompt, 0);
			read_no_bargein(nums_sd .. tostring(i) .. SOUND_EXT, 0);
		end
	end
	
	sleep(delay);
	return randomized_opts;
	
end

-----------
-- recordsurveyinput
-----------

function recordsurveyinput (callid, promptid, lang, maxlength, mfid, confirm)
   maxlength = tonumber(maxlength) or 90;
   -- add callid digits to prevent name collisions
   local mediasubdir = get_media_subdir();
   local partfilename = mediasubdir..os.time() .. callid:sub(callid:len()-1) .. RECORD_SOUND_EXT;
   local filename = recordsd .. partfilename;
   local lang = lang or 'eng';
   confirm = tonumber(confirm) or 1;
   local firstiter = true;
   local recprompts = nil;
   
   if (lang:sub(0,1) == '/') then
   	  recprompts = lang .. '/';
   else
   	  recprompts = aosd .. lang .. '/';
   end
   
   repeat
      if (firstiter == false) then
	   	  read(recprompts .. "pleaserecord.wav", 1000);
	  end
      local d = input();
	  
      if (d == GLOBAL_MENU_MAINMENU) then
	 	  return d;
      end

      session:execute("playback", "tone_stream://%(500, 0, 620)");
      freeswitch.consoleLog("info", script_name .. " : Recording " .. filename .. "\n");
      logfile:write(sessid, "\t",
		    caller, "\t", destination, "\t", 
		    os.time(), "\t", "Record", "\t", filename, "\n");
      session:execute("record", filename .. " " .. maxlength .. " 100 5");
      
      d = input();
      
      if (confirm == 1) then
	      local review_cnt = 0;
	      while (d ~= "1" and d ~= "2" and d ~= "3") do
			 read(recprompts .. "hererecorded.wav", 1000);
			 read(filename, 1000);
			 read(recprompts .. "notsatisfied.wav", 2000);
			 sleep(6000)
			 d = input();
			 review_cnt = check_abort(review_cnt, 3)
	      end
	      
	     if (d ~= "1" and d ~= "2") then
		 	 os.remove(filename);
			 if (d == "3") then
			    read(recprompts .. "messagecancelled.wav", 500);
			    return d;
			 end
	     end
      else
	  	d = "1";
	  end 
	  firstiter = false;
   until (d == "1");
   
   local query = 	"INSERT INTO surveys_input (call_id, prompt_id, input) ";
   query = query .. " VALUES ("..tostring(callid)..","..promptid..",'"..partfilename.."')";
   con:execute(query);
   freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n");
   
   -- check if this sh be attached as a response to an existing msg
   if (mfid ~= nil) then
   	   -- get rgt, forumid
   	   query = "SELECT mf.forum_id, m.rgt, m.thread_id, m.id FROM ao_message_forum mf, ao_message m WHERE mf.message_id = m.id and mf.id = " .. mfid;
	   local cur = con:execute(query);
	   local result = {};
	   result = cur:fetch(result);
	   cur:close();
	   
	   local forumid = result[1];
	   local rgt = tonumber(result[2]);
	   local thread = result[3] or result[4];

		-- get userid
		uid = row("SELECT u.id, u.allowed FROM ao_user u, surveys_subject sub, surveys_call c WHERE sub.id = c.subject_id and sub.number = u.number and c.id = " .. callid);
		local userid = '';
		if (uid ~= nil) then
			userid = tostring(uid[1]);
		else
		   query = "INSERT INTO ao_user (number, allowed) VALUES ('" ..caller.."','y')";
		   con:execute(query);
		   freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n");
		   cur = con:execute("SELECT LAST_INSERT_ID()");
		   userid = tostring(cur:fetch());
		   cur:close();
		end  
       query = "UPDATE ao_message SET rgt=rgt+2 WHERE rgt >=" .. rgt .. " AND (thread_id = " .. thread .. " OR id = " .. thread .. ")";
       con:execute(query);
       freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n")
       query = "UPDATE ao_message SET lft=lft+2 WHERE lft >=" .. rgt .. " AND (thread_id = " .. thread .. " OR id = " .. thread .. ")";
       con:execute(query);
       freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n")
       
       query = "INSERT INTO ao_message (user_id, file, date, thread_id, lft, rgt)";
	   query = query .. " VALUES ("..userid..",'"..partfilename.."',".."now(),'" .. thread .. "','" .. rgt .. "','" .. rgt+1 .. "')";
	   con:execute(query);
	   freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n")
	   id = {};
	   cur = con:execute("SELECT LAST_INSERT_ID()");
	   cur:fetch(id);
	   cur:close();
	   freeswitch.consoleLog("info", script_name .. " : ID = " .. tostring(id[1]) .. "\n");
	   
	   query = "INSERT INTO ao_message_forum (message_id, forum_id, status, last_updated) ";
	   query = query .. " VALUES ("..id[1]..","..forumid..","..MESSAGE_STATUS_PENDING..", now())";
	   con:execute(query);
   end	
   
   read(recprompts .. "okrecorded.wav",500);
   return d;
end

--[[ 
**********************************************************
********* END COMMON SURVEY FUNCTIONS
**********************************************************
--]]