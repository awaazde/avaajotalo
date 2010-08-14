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

script_name = "otalo.lua";
digits = "";
arg = {};

session:setVariable("playback_terminators", "#");
session:setHangupHook("hangup");
session:setInputCallback("my_cb", "arg");

sessid = os.time();
userid = nil;
adminforums = {};

-- set the language, check if line is restricted
line_num = session:getVariable("destination_number");
query = "SELECT language, open FROM AO_line WHERE number LIKE '%" .. line_num .. "%'";
cur = con:execute(query);
line_info = {};
result = cur:fetch(line_info);
cur:close();

if (result == nil) then
   -- default
   aosd = basedir .. "/scripts/AO/sounds/eng/";
else
   aosd = basedir .. "/scripts/AO/sounds/" .. line_info[1] .. "/";
end		

-- responder section-specific sounds
anssd = aosd .. "answer/";

local open = line_info[2];

phonenum = session:getVariable("caller_id_number");
freeswitch.consoleLog("info", script_name .. " : caller id = " .. phonenum .. "\n");
query = "SELECT id, allowed FROM AO_user WHERE number = " .. phonenum;
cur = con:execute(query);
uid = {};
result = cur:fetch(uid);
cur:close();

if (result ~= nil) then
	local allowed = uid[2];
	if (allowed == 'n') then
		-- number not allowed; exit
		return;
	end
	
	userid = tostring(uid[1]);
else
	if (open == 1) then
	   -- first time caller
	   query = "INSERT INTO AO_user (number, allowed) VALUES ('" ..session:getVariable("caller_id_number").."','y')";
	   con:execute(query);
	   freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n");
	   cur = con:execute("SELECT LAST_INSERT_ID()");
	   userid = tostring(cur:fetch());
	   cur:close();
	else
	   -- restricted line and number not pre-registered; exit
	   return;
	end		
end

freeswitch.consoleLog("info", script_name .. " : user id = " .. userid .. "\n");

-- FUNCTIONS
-----------
-- my_cb
-----------

function my_cb(s, type, obj, arg)
   freeswitch.console_log("info", "\ncallback: [" .. obj['digit'] .. "]\n")
   
   if (type == "dtmf") then
      
      logfile:write(sessid, "\t",
      session:getVariable("caller_id_number"), "\t", session:getVariable("destination_number"), "\t", os.time(), "\t",
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
	 digits = obj['digit'];
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
	 read(aosd .. "instructions_full.wav", 500);
	 if (digits ~= GLOBAL_MENU_MAINMENU) then
	    use();
	    read(aosd .. "backtomessage.wav", 1000);
	 end
	 if (digits == GLOBAL_MENU_MAINMENU) then
	    return "break";
	 end
	 return;
      end
      
      if (obj['digit'] == GLOBAL_MENU_SKIP_BACK) then
	 digits = GLOBAL_MENU_SKIP_BACK;
	 freeswitch.consoleLog("info", script_name .. ".callback() : digits = " .. digits .. "\n");
	 return "break";
      end

      if (obj['digit'] == GLOBAL_MENU_PAUSE) then
	 if (digits ~= GLOBAL_MENU_PAUSE) then
	    read(aosd .. "paused.wav", 500);
	    if (digits == GLOBAL_MENU_MAINMENU) then
	       return "break";
	    end
	    if (digits == "") then
	       digits = GLOBAL_MENU_PAUSE;
	       return "pause";
	    else
	       session:execute("playback", "tone_stream://%(500, 0, 620)");
	    end
	 end
      end

      if (obj['digit'] == GLOBAL_MENU_SKIP_FWD) then
	 digits = GLOBAL_MENU_SKIP_FWD;
	 return "break";
      end

      if (obj['digit'] == GLOBAL_MENU_SEEK_BACK) then
	 return "seek:-10";
      end

      if (obj['digit'] == GLOBAL_MENU_REPLAY) then
	 return "seek:0";
      end
              
      if (obj['digit'] == GLOBAL_MENU_SEEK_FWD) then
	 return "seek:+10";
      end
      
   else
      freeswitch.console_log("info", obj:serialize("xml"));
   end
end

-----------
-- getmessages
-----------

function getmessages (forumid)
   local query = "SELECT message.id, message.content_file, message.summary_file, message.rgt, message.thread_id, forum.id, forum.responses_allowed, forum.moderated, message_forum.status ";
   query = query .. "FROM AO_message message, AO_message_forum message_forum, AO_forum forum ";
   query = query .. "WHERE forum.id = " .. forumid .. " AND message_forum.forum_id = " .. forumid .. " AND message.id = message_forum.message_id AND message.lft = 1";
   -- NP: I think this would be confusing to Pareshbhai, especially since there is a dedicated section to approving messages. Leaving out.
   --if (adminmode) then
    --  query = query .. " AND NOT message_forum.status = " .. MESSAGE_STATUS_REJECTED;
   --else
   query = query .. " AND message_forum.status = " .. MESSAGE_STATUS_APPROVED;
   --end
   -- Sort first by position AND then date
   query = query .. " ORDER BY message_forum.position DESC, message.date DESC";
   freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
   return rows(query);
end


-----------
-- getreplies
-----------

function getreplies (thread)
   local query = "SELECT message.id, message.content_file, message.summary_file, message.rgt, message.thread_id, forum.id, forum.responses_allowed, forum.moderated, message_forum.status ";
   query = query .. "FROM AO_message message, AO_message_forum message_forum, AO_forum forum ";
   query = query .. "WHERE message.thread_id = " .. thread .. " AND message_forum.message_id = message.id";
   query = query .. " AND message_forum.status = " .. MESSAGE_STATUS_APPROVED .. " AND message_forum.forum_id = forum.id";
   -- TAP: even though we have threading information (lft, rgt), we
   -- only order by date.  consider losing the lft, right altogether.
   query = query .. " ORDER BY message.date ASC";
   -- query = query .. "ORDER BY message.lft";
   freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
   return rows(query);
end


-----------
-- getusermessages
-----------

function getusermessages ()
   local query = "SELECT message.id, message.content_file, message.summary_file, message.rgt, message.thread_id, forum.id, forum.responses_allowed, forum.moderated, message_forum.status ";
   query = query .. " FROM AO_message message, AO_message_forum message_forum, AO_forum forum ";
   query = query .. " WHERE message.id = message_forum.message_id AND message.lft = 1 AND message.user_id = " .. userid;
   query = query .. " AND message_forum.forum_id = forum.id";
   query = query .. " ORDER BY message.date DESC";
   freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
   return rows(query);
end


-----------
-- getpendingmessages
-----------

function getpendingmessages (lineid)
   local query = "SELECT message.id, message.content_file, message.summary_file, message.rgt, message.thread_id, forum.id, forum.responses_allowed, forum.moderated, message_forum.status ";
   query = query .. "FROM AO_message message, AO_message_forum message_forum, AO_forum forum, AO_line_forums line_forum ";
   query = query .. "WHERE message.id = message_forum.message_id";
   query = query .. " AND message_forum.status = " .. MESSAGE_STATUS_PENDING .. " AND message_forum.forum_id = forum.id AND line_forum.forum_id = forum.id AND line_forum.line_id = " .. lineid;
   query = query .. " ORDER BY message.date DESC";
   freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
   return rows(query);
end

-----------
-- isresponder
-----------

function isresponder (userid, linenum)
   local query = "SELECT 1 ";
   query = query .. "FROM AO_forum_responders fr, AO_line line, AO_line_forums lf, AO_forum forum ";
   query = query .. " WHERE line.number LIKE '%" .. line_num .. "%' "; 
   query = query .. " AND line.id = lf.line_id and lf.forum_id = forum.id AND forum.id = fr.forum_id and fr.user_id = " .. userid;
   freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
   cur = con:execute(query);
   result = cur:fetch();
   cur:close();
	
   return (result ~= nil)
end

-----------
-- hasreplies
-----------

function hasreplies (msgid)
   local query = "SELECT 1 ";
   query = query .. "FROM AO_message m, AO_message_forum mf ";
   query = query .. " WHERE mf.message_id = m.id ";
   query = query .. " AND m.thread_id = " .. msgid;
   query = query .. " AND m.lft > 1 "
   query = query .. " AND mf.status = " .. MESSAGE_STATUS_APPROVED;
   freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
   cur = con:execute(query);
   result = cur:fetch();
   cur:close();
	
   return (result ~= nil)
end



-----------
-- mainmenu
-----------

function mainmenu ()
  
   read(aosd .. "welcome.wav", 500);
   
   local forumids = {};
   local forumnames = {};
   local lineid = nil;
   local i = 0;
   local adminmode = is_admin(nil, adminforums);

   -- TAP: Handle the case where there is only one forum - default
   -- to going straight to that forum.
   local line_num = session:getVariable("destination_number");
   local query = "SELECT forum.id, forum.name_file, line.id ";
   query = query .. "FROM AO_forum forum, AO_line line, AO_line_forums line_forum ";
   query = query .. " WHERE line.number LIKE '%" .. line_num .. "%' "; 
   query = query .. " AND line_forum.line_id = line.id AND line_forum.forum_id = forum.id";
   query = query .. " ORDER BY forum.id ASC";
   
   for row in rows (query) do
      i = i + 1;
      forumids[i] = row[1];
      forumnames[i] = row[2];
      lineid = row[3];
      read(aosd .. "listento_pre.wav", 0);
      read(aosd .. forumnames[i], 0);
      read(aosd .. "listento_post.wav", 0);
      read(aosd .. "digits/" .. i .. ".wav", 500);
   end
   local numforums = i;
 
   i = i + 1;
   local chkrepliesidx = i;
   read(aosd .. "checkmyreplies.wav", 0);
   read(aosd .. "digits/" .. chkrepliesidx .. ".wav", 1000);

   local chkpendingidx = -1;
   if (adminmode) then
   	  i = i + 1;
   	  chkpendingidx = i;
      read(aosd .. "checkpending.wav", 0);
      read(aosd .. "digits/" .. chkpendingidx .. ".wav", 1000);
   end
   
   local responderidx = -1;
   if (isresponder(userid, line_num)) then
   	  i = i + 1;
   	  responderidx = i;
   	  read(aosd .. "checkmyassignedquestions.wav", 0);
      read(aosd .. "digits/" .. responderidx .. ".wav", 1000);
   end
     
   d = tonumber(use());
   
   if (d ~= nil and d > 0 and d <= numforums) then
      freeswitch.consoleLog("info", script_name .. " : Selected Forum : " .. forumnames[d] .. "\n");
      read(aosd .. "okyouwant_pre.wav", 0);
      read(aosd .. forumnames[d], 0);
      read(aosd .. "okyouwant_post.wav", 0);
      playforum(forumids[d]);
   elseif (d == chkrepliesidx) then
      read(aosd .. "okyourreplies.wav", 0);
      use();
      playmessages(getusermessages(), 'y');
   elseif (d == chkpendingidx and adminmode) then
      read(aosd .. "okpending.wav", 0);
      use();
      -- pending messages shouldn't have replies so
      -- leave the flag as 'n'
      playmessages(getpendingmessages(lineid), 'n');
   elseif (d == responderidx) then
   	  read(aosd .. "okresponder.mp3", 0);
      use();
   	  local rmsgs = get_responder_messages(userid);
      play_responder_messages(userid, rmsgs);
   elseif (d ~= nil) then
      freeswitch.consoleLog("info", script_name .. " : No such forum number : " .. d .. "\n");
      sleep(500);
      read(aosd .. "noforum.wav", 500);
   else
      sleep(10000);
   end 
end



-----------
-- playmessage
-----------

function playmessage (msg, listenreplies)
  local id = msg[1];
  local content = msg[2];
  local summary = msg[3];
  local rgt = tonumber(msg[4]);
  local forumid = msg[6];
  local responsesallowed = msg[7];
  local moderated = tonumber(msg[8]);
  local status = tonumber(msg[9]);
  local adminmode = is_admin(forumid, adminforums);

  if (adminmode) then
     local status = tonumber(msg[9]);
  end

  d = playcontent(summary, content);

  if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_SKIP_BACK or d == GLOBAL_MENU_SKIP_FWD or d == GLOBAL_MENU_RESPOND) then
     return d;
  end

  if (status == MESSAGE_STATUS_PENDING and adminmode) then
     read(aosd .. "approvereject.wav", 2000);
     d = use();
     if (d == "1") then
     	local position = 'null';
     	local cur = con:execute("SELECT MAX(mf.position) from AO_message_forum mf, AO_message m WHERE mf.message_id = m.id AND m.lft = 1 AND mf.forum_id = " .. forumid .. " AND mf.status = " .. MESSAGE_STATUS_APPROVED );
	    -- only set position if we have to
	    local pos = cur:fetch()
	    if (pos ~= nil) then 
	       position = tonumber(pos) + 1;
	    end
	    local query = "UPDATE AO_message_forum SET status = " .. MESSAGE_STATUS_APPROVED .. ", position = " .. position .. " WHERE message_id = " .. id .. " AND forum_id = " .. forumid;
		con:execute(query);
		freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n")
		read(aosd .. "messageapproved.wav", 0);
     elseif (d == "2") then
     	local query = "UPDATE AO_message_forum SET status = " .. MESSAGE_STATUS_REJECTED .. " WHERE message_id = " .. id .. " AND forum_id = " .. forumid; 
		con:execute(query);
		freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n")
		read(aosd .. "messagerejected.wav", 0);
     elseif (d == GLOBAL_MENU_MAINMENU) then
	return d;
     end
  end
  
  if (hasreplies(id) and listenreplies == 'y') then
     read(aosd .. "listenreplies.wav", 6000);
     d = use();
	 
     if (d == "1") then
		read(aosd .. "okreplies.wav", 500);
		d = use();
		if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_RESPOND or d == GLOBAL_MENU_SKIP_BACK or d == GLOBAL_MENU_SKIP_FWD) then
		   return d;
		end
		
		d = playmessages(getreplies(id), 'n');
		if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_RESPOND or d == GLOBAL_MENU_SKIP_BACK or d == GLOBAL_MENU_SKIP_FWD) then
		   return d;
		end
		
		read(aosd .. "backtoforum.wav", 1000);
		d = use();
		if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_RESPOND or d == GLOBAL_MENU_SKIP_BACK or d == GLOBAL_MENU_SKIP_FWD) then
		   return d;
		end

        -- dont catch RESPOND because it could also be NO
    elseif (d == GLOBAL_MENU_MAINMENU) then
  		return d;
    end  
  end -- close check for replies

  -- remind about the options, and
  -- give some time for users to compose themselves and
  -- potentially respond
  if (d == "") then
    if (responsesallowed == 'y') then
	  	read(aosd .. "instructions_between.wav", 1000)
	  	d = use();
	end
  	if (d == "") then
     	sleep(3000)
    else
    	return d;
    end
  else
  	return d;
  end
	
  -- default	
  return GLOBAL_MENU_NEXT;
end


-----------
-- playmessages
-----------

function playmessages (msgs, listenreplies)
   -- get the first top-level message for this forum
   local current_msg = msgs();
   local adminmode = false;
   if (current_msg == nil) then
      read(aosd .. "nomessages.wav", 1000);
      return use();
   end

   local prevmsgs = {};
   table.insert(prevmsgs, current_msg);
   local current_msg_idx = 1;
   local d = "";
   
   while (current_msg ~= nil) do
      local adminmode = is_admin(current_msg[6], adminforums);
      local responsesallowed = current_msg[7];
      local moderated = current_msg[8];

      if (d == GLOBAL_MENU_RESPOND) then
		 -- if last msg played recd a response
		 read(aosd .. "backtomessage.wav", 1000);
		 -- do this first b/c its helpful to know when u are at the
		 -- first message
      elseif (current_msg_idx == 1) then
	 	read(aosd .. "firstmessage.wav", 1000);
      elseif (d == GLOBAL_MENU_SKIP_BACK) then  
	 	read(aosd .. "previousmessage.wav", 1000);
      else -- default
	 	read(aosd .. "nextmessage.wav", 1000);
      end

      d = use();
      -- check if a pre-emptive action was taken
      if (d ~= GLOBAL_MENU_MAINMENU and d ~= GLOBAL_MENU_SKIP_BACK and d ~= GLOBAL_MENU_SKIP_FWD and d ~= GLOBAL_MENU_RESPOND) then
	 	d = playmessage(current_msg, listenreplies);
      end

      if (d == GLOBAL_MENU_RESPOND) then
		 if (responsesallowed == 'y' or adminmode) then
		    read(aosd .. "okrecordresponse.wav", 500);
		    local thread = current_msg[5];
		    if (thread == nil) then
		       thread = current_msg[1];
		    end
		    forumid = current_msg[6];
		    d = recordmessage (forumid, thread, moderated, maxlength, current_msg[4], adminmode);
		    if (d == GLOBAL_MENU_MAINMENU) then
		       return d;
		    else
		       d = GLOBAL_MENU_RESPOND;
		    end
		 else
		    read(aosd .. "responsesnotallowed.wav", 500);
		    d = use();
		 end
     elseif (d == GLOBAL_MENU_SKIP_BACK) then
		 if (current_msg_idx > 1) then
		    current_msg_idx = current_msg_idx - 1;
		    current_msg = prevmsgs[current_msg_idx];
		 end
      elseif (d ~= GLOBAL_MENU_MAINMENU) then
		 current_msg_idx = current_msg_idx + 1;
		 -- check to see if we are at the last msg in the forum
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
	 	return d;
      end
   end
end

-----------
-- playforum
-----------

function playforum (forumid)
   local forum = {};
   cur = con:execute("SELECT name_file, moderated, posting_allowed, responses_allowed, maxlength FROM AO_forum WHERE id = " .. forumid);
   cur:fetch(forum);
   cur:close();
   local forumname = forum[1];
   local moderated = forum[2];
   local postingallowed = forum[3];
   local responsesallowed = forum[4];
   local maxlength = forum[5];
   local d = "";
   local adminmode = is_admin(forumid, adminforums);
	
   if (postingallowed == 'y' or adminmode) then
      repeat
		 read(aosd .. "recordorlisten.wav", 3000);
		 d = use();
		 if (d == GLOBAL_MENU_MAINMENU) then
		    return;
		 end
		 if (d == "1") then
		    read(aosd .. "okrecord.wav", 1000);
		    if (recordmessage(forumid, nil, moderated, maxlength, nil, adminmode) == GLOBAL_MENU_MAINMENU) then
		       return;
		    end
		    read(aosd .. "backtoforum.wav", 1000);
		    -- else continue to playing messages
		 end
      until (d == "2");
      
      read(aosd .. "okplay.wav", 1000);
   end

   if (responsesallowed == 'y' or adminmode) then
      read(aosd .. "instructions_short.wav", 1000);
   else
      read(aosd .. "instructions_short_noresponse.wav", 1000);
   end
    
   if (use() == GLOBAL_MENU_MAINMENU) then
      return;
   end

   playmessages(getmessages(forumid), 'y');
   return;
end


-----------
-- MAIN 
-----------
-- get admin permissions
adminrows = rows("SELECT forum_id FROM AO_admin where user_id =  " .. userid);
adminforum = adminrows();
while (adminforum ~= nil) do
	-- use the table as a set to make lookup faster
	adminforums[adminforum[1]] = true;
	freeswitch.consoleLog("info", script_name .. " : adminforum = " .. adminforum[1] .. "\n");
	adminforum = adminrows();
end

-- answer the call
session:answer();

logfile:write(sessid, "\t", session:getVariable("caller_id_number"), "\t", session:getVariable("destination_number"),
"\t", os.time(), "\t", "Start call", "\n");

-- sleep for a sec
sleep(1000);

local mm_cnt = 0;
while (1) do
   -- choose a forum
   mainmenu();

   -- go back to the main menu
   read(aosd .. "mainmenu.wav", 1000);
   
   -- prevent the non-deterministic spinning forever
   mm_cnt = check_abort(mm_cnt, 10)
end

-- say goodbye 
read(bsd .. "/zrtp/8000/zrtp-thankyou_goodbye.wav", 1000);

hangup();
