#!/usr/local/bin/lua

-- INCLUDES

require "luasql.mysql";

-- TODO: figure out how to get the local path
dofile("/usr/local/freeswitch/scripts/AO/paths.lua");

logfile = io.open(logfilename, "a");
logfile:setvbuf("line");
script_name = "otalo.lua";
digits = "";
arg = {};

session:setVariable("playback_terminators", "#");
session:setHangupHook("hangup");
session:setInputCallback("my_cb", "arg");

MESSAGE_STATUS_PENDING = 0;
MESSAGE_STATUS_APPROVED = 1;
MESSAGE_STATUS_REJECTED = 2;

GLOBAL_MENU_MAINMENU = "0";
GLOBAL_MENU_NEXT = "1";
GLOBAL_MENU_RESPOND = "2";
GLOBAL_MENU_INSTRUCTIONS = "3";
GLOBAL_MENU_SKIP_BACK = "4";
GLOBAL_MENU_PAUSE = "5";
GLOBAL_MENU_SKIP_FWD = "6";
GLOBAL_MENU_SEEK_BACK = "7";
GLOBAL_MENU_REPLAY = "8";
GLOBAL_MENU_SEEK_FWD = "9";

sessid = os.time();
userid = nil;
adminmode = false;

phonenum = session:getVariable("caller_id_number");
freeswitch.consoleLog("info", script_name .. " : caller id = " .. phonenum .. "\n");
query = "SELECT id, admin FROM AO_user where number = ".. phonenum;
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
   adminmode = false;
   cur:close();
else
   userid = tostring(row[1]);
   if (tostring(row[2]) == 'y') then
      adminmode = true;
   else
      adminmode = false;
   end
end		

freeswitch.consoleLog("info", script_name .. " : user id = " .. userid .. "\n");

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
-- getmessages
-----------

function getmessages (forumid)
   local query = "SELECT message.id, message.content_file, message.summary_file, message_forum.position, message.lft, message.rgt, message.thread_id, message_forum.status ";
   query = query .. "FROM AO_message message, AO_message_forum message_forum ";
   query = query .. "WHERE message_forum.forum_id = " .. forumid .. " AND message.id = message_forum.message_id AND message.lft = 1";
   --if (adminmode) then
   --query = query .. " AND NOT message_forum.status = " .. MESSAGE_STATUS_REJECTED;
   --else
   query = query .. " AND message_forum.status = " .. MESSAGE_STATUS_APPROVED;
   --end
   -- Sort first by position AND then date
   query = query .. " ORDER BY message_forum.position DESC, message.date DESC";
  
   return rows(query);
end


-----------
-- getreplies
-----------

function getreplies (thread)
   local query = "SELECT message.id, message.content_file, message.summary_file, message_forum.position, message.lft, message.rgt, message.thread_id, message_forum.status ";
   query = query .. "FROM AO_message message, AO_message_forum message_forum ";
   query = query .. "WHERE message.thread_id = " .. thread .. " AND message_forum.message_id = message.id";
   query = query .. " AND message_forum.status = " .. MESSAGE_STATUS_APPROVED;
   -- TAP: even though we have threading information (lft, rgt), we
   -- only order by date.  consider losing the lft, right altogether.
   query = query .. " ORDER BY message.date ASC";
   -- query = query .. "ORDER BY message.lft";

   return rows(query);
end


-----------
-- getusermessages
-----------

function getusermessages ()
   local query = "SELECT message.id, message.content_file, message.summary_file, message_forum.position, message.lft, message.rgt, message.thread_id, message_forum.status ";
   query = query .. "FROM AO_message message, AO_message_forum message_forum ";
   query = query .. "WHERE message.id = message_forum.message_id AND message.lft = 1 AND message.user_id = " .. userid;
   query = query .. " AND message_forum.status = " .. MESSAGE_STATUS_APPROVED;
   query = query .. " ORDER BY message.date DESC";
   freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
   return rows(query);
end


-----------
-- getpendingmessages
-----------

function getpendingmessages ()
   local query = "SELECT message.id, message.content_file, message.summary_file, message_forum.position, message.lft, message.rgt, message.thread_id, message_forum.status ";
   query = query .. "FROM AO_message message, AO_message_forum message_forum ";
   query = query .. "WHERE message.id = message_forum.message_id";
   query = query .. " AND message_forum.status = " .. MESSAGE_STATUS_PENDING;
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

   -- TAP: Handle the case where there is only one forum - default
   -- to going straight to that forum.
   for row in rows ("SELECT id, name_file FROM AO_forum ORDER BY id ASC") do
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
      playforum(forumid);
   elseif (d == i + 1) then
      read(aosd .. "okyourreplies.wav", 0);
      use();
      playmessages(getusermessages(), 'n', 'y', 'y');
   elseif (d == i + 2 and adminmode) then
      read(aosd .. "okpending.wav", 0);
      use();
      playmessages(getpendingmessages(), 'n', 'n', 'n');
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

function playmessage (msg, responsesallowed, moderated, listenreplies)
  local id = msg[1];
  local content = msg[2];
  local summary = msg[3];
  local rgt = tonumber(msg[6]);
  local status = tonumber(msg[8]);

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
	
	d = playmessages(getreplies(id), responsesallowed, moderated, 'n');
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

function playmessages (msgs, responsesallowed, moderated, listenreplies)
   -- get the first top-level message for this forum
   local current_msg = msgs();
   if (current_msg == nil) then
      read(aosd .. "nomessages.wav", 1000);
      return use();
   end

   local prevmsgs = {};
   table.insert(prevmsgs, current_msg);
   local current_msg_idx = 1;
   local d = "";
   
   while (current_msg ~= nil) do
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
      if (d ~= GLOBAL_MENU_MAINMENU and d ~= GLOBAL_MENU_SKIP_BACK or d == GLOBAL_MENU_SKIP_FWD and d ~= GLOBAL_MENU_RESPOND) then
	 d = playmessage(current_msg, responsesallowed, moderated, listenreplies);
      end
      
      if (d == GLOBAL_MENU_RESPOND) then
	 if (responsesallowed == 'y' or adminmode) then
	    read(aosd .. "okrecordresponse.wav", 500);
	    local thread = current_msg[7];
	    if (thread == nil) then
	       thread = current_msg[1];
	    end
	    d = recordmessage (nil, thread, moderated, maxlength, current_msg[6]);
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

function recordmessage (forumid, thread, moderated, maxlength, rgt)
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
   query2 = " VALUES ('"..userid.."','"..partfilename.."',".."now()";
   
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
   
   if (forumid ~= nil) then
      query1 = "INSERT INTO AO_message_forum (message_id, forum_id";
      query2 = " VALUES ('"..id[1].."','"..forumid.."'";
      
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
   end

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
	
   if (postingallowed == 'y' or adminmode) then
      repeat
	 read(aosd .. "recordorlisten.wav", 3000);
	 d = use();
	 if (d == GLOBAL_MENU_MAINMENU) then
	    return;
	 end
	 if (d == "1") then
	    read(aosd .. "okrecord.wav", 1000);
	    if (recordmessage(forumid, nil, moderated, maxlength, nil) == GLOBAL_MENU_MAINMENU) then
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

   playmessages(getmessages(forumid), responsesallowed, moderated, 'y');
   return;
end


-----------
-- MAIN 
-----------

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
