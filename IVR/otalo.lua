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

script_name = "otalo.lua";
digits = "";
arg = {};

session:setVariable("playback_terminators", "#");
session:setHangupHook("hangup");
session:setInputCallback("my_cb", "arg");

sessid = os.time();
userid = nil;
adminforums = {};

phonenum = session:getVariable("caller_id_number");
freeswitch.consoleLog("info", script_name .. " : caller id = " .. phonenum .. "\n");
query = "SELECT id FROM AO_user WHERE number = " .. phonenum;
cur = con:execute(query);
row = {};
result = cur:fetch(row);
cur:close();

if (result == nil) then
   -- first time caller
   query = "INSERT INTO AO_user (number, allowed, admin) VALUES ('" ..session:getVariable("caller_id_number").."','y','n')";
   con:execute(query);
   freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n");
   cur = con:execute("SELECT LAST_INSERT_ID()");
   userid = tostring(cur:fetch());
   cur:close();
else
   userid = tostring(row[1]);
end		


-- FUNCTIONS

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
	     row = {};
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


----------
-- use
----------

function use()
   d = digits;
   digits = "";
   return d;
end


-----------
-- my_cb
-----------

function my_cb(s, type, obj, arg)
   freeswitch.console_log("info", "\ncallback: [" .. obj['digit'] .. "]\n")
   
   if (type == "dtmf") then
      
      logfile:write(sessid, "\t",
      session:getVariable("caller_id_number"), "\t", os.time(), "\t",
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
-- is_admin 
-----------

function is_admin(forumid) 
	if (forumid == nil) then
   		freeswitch.consoleLog("info", script_name .. " : is_admin(nil) : " .. tostring(#adminforums>0) .. "\n");
		return #adminforums > 0;
	else
   		freeswitch.consoleLog("info", script_name .. " : is_admin(" .. forumid ..") : " .. tostring(adminforums[forumid] == true) .. "\n");
		return adminforums[forumid] == true;
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
   query = query .. "FROM AO_message message, AO_message_forum message_forum, AO_forum forum ";
   query = query .. "WHERE message.id = message_forum.message_id AND message.lft = 1 AND message.user_id = " .. userid;
   query = query .. " AND message_forum.status = " .. MESSAGE_STATUS_APPROVED .. " AND message_forum.forum_id = forum.id";
   query = query .. " ORDER BY message.date DESC";
   freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
   return rows(query);
end


-----------
-- getpendingmessages
-----------

function getpendingmessages ()
   local query = "SELECT message.id, message.content_file, message.summary_file, message.rgt, message.thread_id, forum.id, forum.responses_allowed, forum.moderated, message_forum.status ";
   query = query .. "FROM AO_message message, AO_message_forum message_forum, AO_forum forum ";
   query = query .. "WHERE message.id = message_forum.message_id";
   query = query .. " AND message_forum.status = " .. MESSAGE_STATUS_PENDING .. " AND message_forum.forum_id = forum.id";
   query = query .. " ORDER BY message.date DESC";
   freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
   return rows(query);
end


-----------
-- mainmenu
-----------

function mainmenu ()
  
   read(aosd .. "welcome.wav", 500);
   
   local forumids = {};
   local forumnames = {};
   local i = 0;
   local adminmode = is_admin(nil);

   -- TAP: Handle the case where there is only one forum - default
   -- to going straight to that forum.
   phone_num = session:getVariable("destination_number");
   local query = "SELECT forum.id, forum.name_file ";
   query = query .. "FROM AO_forum forum, AO_line line, AO_line_forum line_forum ";
   query = query .. " WHERE line.number = ".. phone_num;
   query = query .. " AND line_forum.line_id = line.id AND line_forum.forum_id = forum.id";
   query = query .. " ORDER BY forum.id ASC";
   
   for row in rows (query) do
      i = i + 1;
      forumids[i] = row[1];
      forumnames[i] = row[2];
      read(aosd .. "listento_pre.wav", 0);
      read(aosd .. forumnames[i], 0);
      read(aosd .. "listento_post.wav", 0);
      read(aosd .. "digits/" .. i .. ".wav", 500);
   end

   read(aosd .. "checkmyreplies.wav", 1000);
   read(aosd .. "digits/" .. i + 1 .. ".wav", 500);

   if (adminmode) then
      read(aosd .. "checkpending.wav", 1000);
      read(aosd .. "digits/" .. i + 2 .. ".wav", 500);
   end
     
   d = tonumber(use());
   
   if (d ~= nil and d > 0 and d <= i) then
      freeswitch.consoleLog("info", script_name .. " : Selected Forum : " .. forumnames[d] .. "\n");
      read(aosd .. "okyouwant_pre.wav", 0);
      read(aosd .. forumnames[d], 0);
      read(aosd .. "okyouwant_post.wav", 0);
      playforum(d);
   elseif (d == i + 1) then
      read(aosd .. "okyourreplies.wav", 0);
      use();
      playmessages(getusermessages(), 'n');
   elseif (d == i + 2 and adminmode) then
      read(aosd .. "okpending.wav", 0);
      use();
      playmessages(getpendingmessages(), 'n');
   elseif (d ~= nil) then
      freeswitch.consoleLog("info", script_name .. " : No such forum number : " .. d .. "\n");
      sleep(500);
      read(aosd .. "noforum.wav", 500);
   else
      sleep(10000);
   end 
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


-----------
-- playmessage
-----------

function playmessage (msg, listenreplies)
  local id = msg[1];
  local content = msg[2];
  local summary = msg[3];
  local rgt = tonumber(msg[4]);
  local forumid = msg[6];
  local responsesallowed = tonumber(msg[7]);
  local moderated = tonumber(msg[8]);
  local status = MESSAGE_STATUS_APPROVED;
  local adminmode = is_admin(forumid);

  if (adminmode) then
     local status = tonumber(msg[9]);
  end

  d = playcontent(summary, content);

  if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_SKIP_BACK or d == GLOBAL_MENU_SKIP_FWD or d == GLOBAL_MENU_RESPOND) then
     return d;
  end

  if (status == MESSAGE_STATUS_PENDING and adminmode) then
     read(aosd .. "approvereject.wav", 500);
     d = use();
     if (d == "1") then
	con:execute("UPDATE AO_message_forum SET status = " .. MESSAGE_STATUS_APPROVED .. " WHERE message_id = " .. id);
	read(aosd .. "messageapproved.wav", 0);
     elseif (d == "2") then
	con:execute("UPDATE AO_message_forum SET status = " .. MESSAGE_STATUS_REJECTED .. " WHERE message_id = " .. id);
	read(aosd .. "messagerejected.wav", 0);
     elseif (d == GLOBAL_MENU_MAINMENU) then
	return d;
     end
  end
  
  if (rgt > 2 and listenreplies == 'y') then
     read(aosd .. "listenreplies.wav", 2000);
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

  -- give some time for users to compose themselves and
  -- potentially respond
  if (d == "") then
     sleep(3000)
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
      adminmode = is_admin(current_msg[6]);
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
-- recordmessage
-----------

function recordmessage (forumid, thread, moderated, maxlength, rgt, adminmode)
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
      
      while (d ~= GLOBAL_MENU_MAINMENU and d ~= "1" and d ~= "2" and d ~= "3") do
	 read(aosd .. "hererecorded.wav", 1000);
	 read(filename, 1000);
	 read(aosd .. "notsatisfied.wav", 2000);
	 sleep(6000)
	 d = use();
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
   query2 = " VALUES ("..userid..",'"..partfilename.."',".."now()";
   
   if (thread ~= nil) then -- this is a response
      query = "UPDATE AO_message SET rgt=rgt+2 WHERE rgt >=" .. rgt .. " AND (thread_id = " .. thread .. " OR id = " .. thread .. ")";
      con:execute(query);
      freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n")
      query = "UPDATE AO_message SET lft=lft+2 WHERE lft >=" .. rgt .. " AND (thread_id = " .. thread .. " OR id = " .. thread .. ")";
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
   
      query1 = "INSERT INTO AO_message_forum (message_id, forum_id";
      query2 = " VALUES ("..id[1]..","..forumid;
      
      local position = "null";
      if (moderated == 'y' and not adminmode) then
	 	status = MESSAGE_STATUS_PENDING;
      else
	 	status = MESSAGE_STATUS_APPROVED; 
	 	if (thread == nil) then
		    cur = con:execute("SELECT MAX(mf.position) from AO_message_forum mf, AO_message m WHERE mf.message_id = m.id AND m.lft = 1 AND mf.forum_id = " .. forumid .. " AND mf.status = " .. MESSAGE_STATUS_APPROVED );
		    -- only set position if we have to
		    pos = cur:fetch()
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

   read(aosd .. "okrecorded.wav", 500);
   return use();
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
   local adminmode = is_admin(forumid);
	
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
      until (d ~= "1");
      
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
freeswitch.consoleLog("info", script_name .. " : user id = " .. userid .. "\n");

-- answer the call
session:answer();

logfile:write(sessid, "\t", session:getVariable("caller_id_number"),
"\t", os.time(), "\t", "Start call", "\n");

-- sleep for a sec
sleep(1000);

while (1) do
   -- choose a forum
   mainmenu();

   -- go back to the main menu
   read(aosd .. "mainmenu.wav", 1000);
end

-- say goodbye 
read(bsd .. "/zrtp/8000/zrtp-thankyou_goodbye.wav", 1000);

hangup();
