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

function hangup() 
   logfile:write(sessid, "\t",
		 session:getVariable("caller_id_number"), "\t",
		 os.time(), "\t", "End call", "\n");

   -- cleanup
   con:close();
   env:close();
   logfile:flush();
   logfile:close();
   
   -- hangup
   session:hangup();
end

-----------
-- rows 
-----------

function rows (sql_statement)
   local cursor = assert (con:execute (sql_statement));
   local closed = false;
   freeswitch.consoleLog("info", script_name .. " : " .. sql_statement .. "\n")
   return function ()
	     if (closed) then 
		return nil;
	     end;
	     local row = {};
	     result = cursor:fetch(row);
	     if (result == nil) then
		cursor:close();
		closed = true;
		return nil;
	     end;
	     return row;
	  end
end

-----------
-- row 
-----------
function row(sql_statement)
	local cursor = assert (con:execute (sql_statement));
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

function read(file, delay)
   if (digits == "") then
      logfile:write(sessid, "\t",
		    session:getVariable("caller_id_number"), "\t",
		    os.time(), "\t", "Prompt", "\t", file, "\n");
      digits = session:read(1, 1, file, delay, "#");
      if (digits ~= "") then
	 logfile:write(sessid, "\t", session:getVariable("caller_id_number"), "\t", os.time(), "\t", "dtmf", "\t", file, "\t", digits, "\n"); 
      end
   end
end

-----------
-- read_no_bargein
-----------

function read_no_bargein(file, delay)
      logfile:write(sessid, "\t",
		    session:getVariable("caller_id_number"), "\t",
		    os.time(), "\t", "Prompt", "\t", file, "\n");
      session:streamFile(file);
      sleep(delay);
      -- ignore all input
      use();
end

----------
-- use
----------

function use()
   d = digits;
   digits = "";
   -- need the below so any input from the stream
   -- doesn't carry over to the next
   session:flushDigits();
   return d;
end

-----------
-- playcontent
-----------

function playcontent (summary, content)
   local d;
   
   if (summary ~= nil and summary ~= "") then
      arg[1] = sd .. summary;
      logfile:write(sessid, "\t",
		    session:getVariable("caller_id_number"), "\t",
		    os.time(), "\t", "Stream", "\t", arg[1], "\n");
      session:streamFile(sd .. summary);
      sleep(1000);
      
      d = use();
      if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_SKIP_BACK or d == GLOBAL_MENU_SKIP_FWD or d == GLOBAL_MENU_RESPOND) then
	 return d;
      end
   
      read(aosd .. "morecontent.wav", 2000);
      d = use();
      if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_SKIP_BACK or d == GLOBAL_MENU_SKIP_FWD or d == GLOBAL_MENU_RESPOND) then
	 return d;
      elseif (d ~= "1") then
	 return GLOBAL_MENU_NEXT;
      else
	 read(aosd .. "okcontent.wav", 500);
	 d = use();
	 if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_SKIP_BACK or d == GLOBAL_MENU_SKIP_FWD or d == GLOBAL_MENU_RESPOND) then
	    return d;
	 end
      end
   end
   
   arg[1] = sd .. content;
   logfile:write(sessid, "\t",
		 session:getVariable("caller_id_number"), "\t",
		 os.time(), "\t", "Stream", "\t", arg[1], "\n");

   session:streamFile(sd .. content);
   sleep(3000);
   
   return use();
end

-- BEGIN common resonder functions

-- App-specific GLOBALS
GLOBAL_MENU_REPLAY = "6";
GLOBAL_MENU_ASK_LATER = "7";
GLOBAL_MENU_PASS = "8";
GLOBAL_MENU_REFER = "9";
GLOBAL_MENU_CANCEL_REFERRAL = "*";

RESERVE_PERIOD = "2"
LISTENS_THRESH = "5"

-----------
-- read_phone_num
-----------

function read_phone_num(file, delay)
   if (digits == "") then
      logfile:write(sessid, "\t",
		    session:getVariable("caller_id_number"), "\t",
		    os.time(), "\t", "Prompt", "\t", file, "\n");
	  -- allow 1 or 10 (1 to cancel)
      digits = session:read(1, 10, file, delay, "#");
      if (digits ~= "") then
	 logfile:write(sessid, "\t", session:getVariable("caller_id_number"), "\t", os.time(), "\t", "dtmf", "\t", file, "\t", digits, "\n"); 
      end
   end
end

-----------
-- get_responder_messages
-----------

function get_responder_messages (userid)
   local query = "SELECT message.id, message.content_file, message.summary_file, message.rgt, message_forum.forum_id, message_forum.id ";
   query = query .. " FROM AO_message message, AO_message_forum message_forum, AO_message_responder message_responder";
   query = query .. " WHERE message.id = message_forum.message_id";
   query = query .. " AND message_responder.message_forum_id = message_forum.id ";
   query = query .. " AND message_responder.user_id = " .. userid;
   query = query .. " AND message.lft = 1 AND message.rgt = 2 AND message_responder.listens <= " .. LISTENS_THRESH;
   query = query .. " AND message_responder.passed_date IS NULL ";
   query = query .. " AND (message_responder.reserved_by_id IS NULL OR ";
   query = query .. "      (message_responder.reserved_by_id = " .. userid .. " AND message_responder.reserved_until < now())) ";
   query = query .. " ORDER BY message.date DESC";
   return rows(query);
end

-----------
-- ask_later
-----------

function ask_later (userid, messageforumid)
   local query = "UPDATE AO_message_responder ";
   query = query .. " SET reserved_by_id = " .. userid .. " , reserved_until = now() + INTERVAL " .. RESERVE_PERIOD .. " DAY ";
   query = query .. " WHERE message_forum_id = " .. messageforumid;
   con:execute(query);
   freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
end

-----------
-- pass_question
-----------

function pass_question (userid, messageforumid)
   local query = "UPDATE AO_message_responder ";
   query = query .. " SET passed_date = now() ";
   query = query .. " WHERE message_forum_id = " .. messageforumid .. " AND user_id = " .. userid;
   con:execute(query);
   freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
end

-----------
-- refer_question
-----------
function refer_question(ph_num, messageforumid)
	query = "SELECT id FROM AO_user where number = ".. ph_num;
	cur = con:execute(query);
	row = {};
	result = cur:fetch(row);
	cur:close();
	
	if (result == nil) then
	   -- unregistered number
	   query = "INSERT INTO AO_user (number, allowed, admin) VALUES ('" .. ph_num .."','y','n')";
	   con:execute(query);
	   freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n");
	   cur = con:execute("SELECT LAST_INSERT_ID()");
	   uid = tostring(cur:fetch());
	   cur:close();
	else
	   uid = tostring(row[1]);
	end	
	
	-- create referal
	query = "INSERT INTO AO_message_responder (message_forum_id, user_id) VALUES (" ..messageforumid..", " .. uid ..")";
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
	
   local query = "UPDATE AO_message_responder ";
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
  local summary = msg[3];

  d = playcontent(summary, content);
  
  -- remind about the options, and
  -- give some time for users to compose themselves and
  -- potentially respond
  if (d == "") then
  	read(anssd .. "instructions_short.wav", 1000)
  	d = use();
  	if (d == "") then
     	sleep(3000)
    else
    	return d;
    end
  else
  	return d;
  end
  
  d = use();
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

function play_responder_messages (userid, msgs)
   -- get the first top-level message for this forum
   local current_msg = msgs();
   if (current_msg == nil) then
      read(aosd .. "nomessages.wav", 1000);
      return use();
   end

   prevmsgs = {};
   table.insert(prevmsgs, current_msg);
   local current_msg_idx = 1;
   local d = "";
   
   while (current_msg ~= nil) do
      if (d == GLOBAL_MENU_RESPOND or d== GLOBAL_MENU_REFER or d == GLOBAL_MENU_REPLAY or d == GLOBAL_MENU_INSTRUCTIONS) then
		 -- if last msg played recd a response
		 read(aosd .. "backtomessage.wav", 1000);
      elseif (current_msg_idx == 1) then
      	 -- do this before prev check b/c 
		 -- its helpful to know when u are at the first message
		 read(aosd .. "firstmessage.wav", 1000);
      elseif (d == GLOBAL_MENU_SKIP_BACK) then  
	 	read(aosd .. "previousmessage.wav", 1000);
      else -- default
	 	read(aosd .. "nextmessage.wav", 1000);
      end

      d = use();
      -- check if a pre-emptive action was taken
      -- don't listen for pre-emptive actions that require
      -- listening to the message at least a little. Make an
      -- exception for responses which we want to encourage
      if (d ~= GLOBAL_MENU_MAINMENU and d ~= GLOBAL_MENU_SKIP_BACK and d ~= GLOBAL_MENU_SKIP_FWD and d ~= GLOBAL_MENU_RESPOND) then
	 	d = play_responder_message(current_msg);
      end
      
      
      if (d == GLOBAL_MENU_RESPOND) then
	    read(aosd .. "okrecordresponse.wav", 500);
	    thread = current_msg[1];
	    forumid = current_msg[5];
	    rgt = current_msg[4];
	    d = record_responder_message (forumid, thread, maxlength, rgt);
	    if (d == GLOBAL_MENU_MAINMENU) then
	    	update_listens(prevmsgs, userid);
	       return d;
	    else
	       d = GLOBAL_MENU_RESPOND;
	    end
      elseif (d == GLOBAL_MENU_SKIP_BACK) then
		 if (current_msg_idx > 1) then
		    current_msg_idx = current_msg_idx - 1;
		    current_msg = prevmsgs[current_msg_idx];
		 end
	  elseif (d == GLOBAL_MENU_ASK_LATER) then
	  	read(anssd .. "asklater.wav", 500);
	  	local msgforumid = current_msg[6];
	  	ask_later(userid, msgforumid);
	  elseif (d == GLOBAL_MENU_PASS) then
	  	read(anssd .. "passquestion.wav", 500);
	  	local msgforumid = current_msg[6];
	  	pass_question(userid, msgforumid);
	  elseif (d == GLOBAL_MENU_REFER) then

	  	read_phone_num(anssd .. "referquestion.wav", 3000);
		d = use();
		local phone_num_cnt = 0;
	  	while (d ~= GLOBAL_MENU_CANCEL_REFERRAL and string.len(d) ~= 10) do
		  	session:execute("playback", "tone_stream://%(500, 0, 620)");
		  	read_phone_num("", 3000);
		  	d = use();
		  	
		  	if (d ~= GLOBAL_MENU_CANCEL_REFERRAL and string.len(d) ~= 10) then
	  			read(anssd .. "invalidphonenum.wav",500)
	  		end
	  		phone_num_cnt = check_abort(phone_num_cnt, 4);
	  	end
	  	
	  	if (d == GLOBAL_MENU_CANCEL_REFERRAL) then
	  		read(aosd .. "messagecancelled.wav", 500);
	  	else
	  		local msgforumid = current_msg[6];
	  		refer_question(d, msgforumid);
	  	end
	  	
	  	-- go back to message
	  	d = GLOBAL_MENU_REFER
      elseif (d == GLOBAL_MENU_REPLAY) then
		-- do nothing
      elseif (d == GLOBAL_MENU_INSTRUCTIONS) then
	  	 read(aosd .. "okinstructions.wav", 500);
		 read(anssd .. "instructions_full.wav", 500);
		 
		 d = use();
		 -- ignore anything except main menu 
		if (d ~= GLOBAL_MENU_MAINMENU) then
		    -- go back to original message
		    d = GLOBAL_MENU_INSTRUCTIONS;
		 end
      elseif (d ~= GLOBAL_MENU_MAINMENU) then
	  	current_msg_idx = current_msg_idx + 1;
		-- check to see if we are at the last msg in the list
	 	if (current_msg_idx > #prevmsgs) then
		    -- get next msg from the cursor
		    current_msg = msgs();
		    if (current_msg == nil) then
		       read(aosd .. "lastmessage.wav", 1000);
		       d = use(); 
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


-----------
-- record_responder_message
-----------

function record_responder_message (forumid, thread, maxlength, rgt)
   local forumid = forumid or nil;
   local thread = thread or nil;
   local moderated = moderated or nil;
   local maxlength = maxlength or 60000;
   local rgt = rgt or 1;
   local partfilename = os.time() .. ".mp3";
   local filename = sd .. partfilename;

   repeat
      read(aosd .. "pleaserecord.wav", 1000);
      local d = use();

      if (d == GLOBAL_MENU_MAINMENU) then
	 return d;
      end

      session:execute("playback", "tone_stream://%(500, 0, 620)");
      freeswitch.consoleLog("info", script_name .. " : Recording " .. filename .. "\n");
      logfile:write(sessid, "\t",
		    session:getVariable("caller_id_number"), "\t",
		    os.time(), "\t", "Record", "\t", filename, "\n");
      session:execute("record", filename .. " " .. maxlength .. " 80 2");
      --sleep(1000);
      d = use();
      
      if (d == GLOBAL_MENU_MAINMENU) then
		 os.remove(filename);
		 return d;
      end
      
      local review_cnt = 0;
      while (d ~= GLOBAL_MENU_MAINMENU and d ~= "1" and d ~= "2" and d ~= "3") do
		 read(aosd .. "hererecorded.wav", 1000);
		 read(filename, 1000);
		 read(aosd .. "notsatisfied.wav", 2000);
		 sleep(6000)
		 d = use();
		 review_cnt = check_abort(review_cnt, 4)
      end
      
     if (d ~= "1" and d ~= "2") then
	 	 os.remove(filename);
		 if (d == GLOBAL_MENU_MAINMENU) then
		    return d;
		 elseif (d == "3") then
		    read(aosd .. "messagecancelled.wav", 500);
		    return use();
		 end
     end
   
   until (d == "1");
   
   query1 = "INSERT INTO AO_message (user_id, content_file, date";
   query2 = " VALUES ('"..userid.."','"..partfilename.."',".."now()";
   
   -- this is a response
  query = "UPDATE AO_message SET rgt=rgt+2 WHERE rgt >=" .. rgt .. " AND (thread_id = " .. thread .. " OR id = " .. thread .. ")";
  con:execute(query);
  freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n")
  query = "UPDATE AO_message SET lft=lft+2 WHERE lft >=" .. rgt .. " AND (thread_id = " .. thread .. " OR id = " .. thread .. ")";
  con:execute(query);
  freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n")
  query1 = query1 .. ", thread_id, lft, rgt)";
  query2 = query2 .. ",'" .. thread .. "','" .. rgt .. "','" .. rgt+1 .. "')";

   
   query = query1 .. query2;
   con:execute(query);
   freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n")
   id = {};
   cur = con:execute("SELECT LAST_INSERT_ID()");
   cur:fetch(id);
   cur:close();
   freeswitch.consoleLog("info", script_name .. " : ID = " .. tostring(id[1]) .. "\n");
   
   query1 = "INSERT INTO AO_message_forum (message_id, forum_id";
   query2 = " VALUES ('"..id[1].."','"..forumid.."'";
   
	 status = MESSAGE_STATUS_APPROVED; 
	 
	  query1 = query1 .. ", status)";
	  query2 = query2 .. "," .. status ..")";
   
      query = query1 .. query2;
      con:execute(query);
      freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n")

   read(anssd .. "okrecorded.wav", 500);
   return use();
end

-- END common resonder functions

function check_abort(counter, threshold)
	counter = counter + 1;
	if (counter >= threshold) then
		logfile:write(sessid, "\t", session:getVariable("caller_id_number"), "\t", os.time(), "\t", "Abort call", "\n");
		hangup();
	else
		return counter;
	end
end
