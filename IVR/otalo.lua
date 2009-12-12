#!/usr/local/bin/lua

-- INCLUDES

require "luasql.mysql";

-- TODO: figure out how to get the local path
dofile("/usr/local/freeswitch/scripts/AO/paths.lua");

logfile = io.open(logfilename, "a");
script_name = "otalo.lua";
sessid = os.time();
digits = "";
arg = {};

session:setVariable("playback_terminators", "#");
session:setHangupHook("hangup");
session:setInputCallback("my_cb", "arg");

MESSAGE_STATUS_PENDING = 0;
MESSAGE_STATUS_APPROVED = 1;
MESSAGE_STATUS_REJECTED = 2;

-- TAP: Still not sure about these mappings.
GLOBAL_MENU_MAINMENU = "0";
GLOBAL_MENU_NEXT = "1";
GLOBAL_MENU_BACK = "2";
GLOBAL_MENU_PAUSE = "3";
GLOBAL_MENU_REPLAY = "4";
GLOBAL_MENU_RESPOND = "5";
GLOBAL_MENU_SEEK_FWD = "6";
GLOBAL_MENU_SEEK_BACK = "7";
GLOBAL_MENU_INSTRUCTIONS = "8";


-- FUNCTIONS

-----------
-- hangup 
-----------

function hangup()
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
  freeswitch.consoleLog("info", script_name .. " : " .. sql_statement .. "\n")
  return function ()
	    row = {};
	    result = cursor:fetch(row);
	    if (result == nil) then
	       cursor:close();
	       return nil;
	    end;
	    return row;
	 end
end


-----------
-- read
-----------

function read(file, delay)
   if (digits == "") then
      digits = session:read(1, 1, file, delay, "#");
      if (digits ~= "") then
	 logfile:write(sessid, "\t", session:getVariable("caller_id_number"), "\t", os.time(), "\t", file, "\t", "dtmf", "\t", digits, "\n"); 
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
      
      logfile:write(sessid, "\t", session:getVariable("caller_id_number"), "\t", os.time(), "\t", arg[1], "\t", "dtmf", "\t", obj['digit'], "\n"); 
      freeswitch.console_log("info", "\ndigit: [" .. obj['digit'] .. "]\nduration: [" .. obj['duration'] .. "]\n");
	  
      if (obj['digit'] == GLOBAL_MENU_MAINMENU) then
	 digits = GLOBAL_MENU_MAINMENU;
	 return "break";
      end

      if (obj['digit'] == GLOBAL_MENU_NEXT or obj['digit'] == "#") then
	 digits = GLOBAL_MENU_NEXT;
	 return "break";
      end

      if (obj['digit'] == GLOBAL_MENU_BACK) then
	 digits = GLOBAL_MENU_BACK;
	 freeswitch.consoleLog("info", script_name .. ".callback() : digits = " .. digits .. "\n");
	 return "break";
      end

      if (obj['digit'] == GLOBAL_MENU_REPLAY) then
	 return "seek:0";
      end
             
      if (obj['digit'] == GLOBAL_MENU_PAUSE) then
	 if (digits ~= GLOBAL_MENU_PAUSE) then
	    read(aosd .. "paused.wav", 500);
	    if (digits == GLOBAL_MENU_MAINMENU) then
	       return "break";
	    end
	    digits = GLOBAL_MENU_PAUSE;
	 end
	 return "pause";
      end
        
      if (obj['digit'] == GLOBAL_MENU_RESPOND) then	
	 digits = GLOBAL_MENU_RESPOND;
	 return "break";
      end

      if (obj['digit'] == GLOBAL_MENU_SEEK_FWD) then
	 return "seek:+500";
      end
      
      if (obj['digit'] == GLOBAL_MENU_SEEK_BACK) then
	 return "seek:-500";
      end
      
      if (obj['digit'] == GLOBAL_MENU_INSTRUCTIONS) then
	 read(aosd .. "okinstructions.wav", 500);
	 read(aosd .. "instructions.wav", 500);
	 if (digits ~= GLOBAL_MENU_MAINMENU) then
	    use();
	    read(aosd .. "backtomessage.wav", 1000);
	 end
	 if (digits == GLOBAL_MENU_MAINMENU) then
	    return "break";
	 end
	 return;
      end

   else
      freeswitch.console_log("info", obj:serialize("xml"));
   end
end



-----------
-- getmessages
-----------

function getmessages (forumid)
   local query = "SELECT message.id, message.content_file, message.extra_content_file, message_forum.position, message.lft, message.rgt, message.thread_id ";
   query = query .. "FROM AO_message message, AO_message_forum message_forum ";
   query = query .. "WHERE message_forum.forum_id = " .. forumid .. " AND message_forum.status = " .. MESSAGE_STATUS_APPROVED .. " AND message.id = message_forum.message_id AND message.lft = 1 ";
   -- TAP: Sort first by position AND then date
   query = query .. "ORDER BY message_forum.position DESC, message.date DESC";
  
   return rows(query);
end


-----------
-- getreplies
-----------

function getreplies (thread)
   local query = "SELECT message.id, message.content_file, message.extra_content_file, message_forum.position, message.lft, message.rgt, message.thread_id ";
   query = query .. "FROM AO_message message, AO_message_forum message_forum ";
   query = query .. "WHERE message.thread_id = " .. thread .. " AND message_forum.message_id = message.id AND message_forum.status = " .. MESSAGE_STATUS_APPROVED .. " ";
   -- TAP: even though we have threading information (lft, rgt), we
   -- only order by date.  consider losing the lft, right altogether.
   query = query .. "ORDER BY message.date ASC";
   -- query = query .. "ORDER BY message.lft";

   return rows(query);
end


-----------
-- chooseforum
-----------

function chooseforum ()
  
   -- choose the forum
   while (1) do
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
   
      d = tonumber(use());

      if (d ~= nil and d > 0 and d <= i) then
	 freeswitch.consoleLog("info", script_name .. " : Selected Forum : " .. forumnames[d] .. "\n");
	 read(aosd .. "okyouwant_pre.wav", 0);
	 read(aosd .. forumnames[d], 0);
	 read(aosd .. "okyouwant_post.wav", 0);
	 return forumids[d];
      elseif (d ~= nil) then
	 freeswitch.consoleLog("info", script_name .. " : No such forum number : " .. d .. "\n");
	 session:sleep(500);
	 read(aosd .. "noforum.wav", 500);
      else
	 session:sleep(1000);
      end 
   end
end


-----------
-- playcontent
-----------

function playcontent (extra, content)
   local d;
   
   if (extra ~= nil and extra ~= "") then
      -- TAP: Do you really want to play the "extra" file first?  Then
      -- that sounds like a "subject" file to me.  If so you should
      -- change the naming here and in the DB.
      arg[1] = sd .. extra;
      logfile:write(sessid, "\t", session:getVariable("caller_id_number"), "\t", os.time(), "\t", arg[1], "\t", "play", "\n"); 
      session:streamFile(sd .. extra);
      session:sleep(1000);
      
      d = use();
      if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_BACK or d == GLOBAL_MENU_RESPOND) then
	 return d;
      end
   
      read(aosd .. "morecontent.wav", 2000);
      d = use();
      if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_BACK or d == GLOBAL_MENU_RESPOND) then
	 return d;
      elseif (d ~= 1) then
	 return GLOBAL_MENU_NEXT;
      else
	 read(aosd .. "okcontent.wav", 500);
	 d = use();
	 if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_BACK or d == GLOBAL_MENU_RESPOND) then
	    return d;
	 end
      end
   end
   
   arg[1] = sd .. content;
   logfile:write(sessid, "\t", session:getVariable("caller_id_number"), "\t", os.time(), "\t", arg[1], "\t", "play", "\n"); 
   session:streamFile(sd .. content);
   session:sleep(1000);
   
   return use();
end


-----------
-- playmessage
-----------

function playmessage (msg, responsesallowed, listenreplies)
  local id = msg[1];
  local content = msg[2];
  local extra = msg[3];
  local rgt = tonumber(msg[6]);

  d = playcontent(extra, content);

  -- no short circuit for next here; still want to prompt to listen to replies
  if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_BACK or d == GLOBAL_MENU_RESPOND) then
  	return d;
  end
  
  if (rgt > 2 and listenreplies == 'y') then
     read(aosd .. "listenreplies.wav", 2000);
     d = use();
	 
     -- TAP: Why 3?  Hasnt the default for Yes been 1?  We should be
     -- careful not to overextend the GLOBAL_MENU mapping.  In my
     -- mind, 0 is the only global mapping.  Make this consistent w/
     -- other Yes/No prompts.  (1 = Yes / Default).  YOURS: no short
     -- circuit for next here; still want to prompt to record a
     -- response
     if (d == "1") then
	read(aosd .. "okreplies.wav", 500);
	d = use();
	-- just like when we are about to play messages in the forum
	-- (instructions), don't short circuit on next
	if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_BACK or d == GLOBAL_MENU_RESPOND) then
	   return d;
	end
	d = playmessages(getreplies(id), responsesallowed, 'n');
     end
  end -- close check for replies

  if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_BACK or d == GLOBAL_MENU_RESPOND) then
     return d;
  end

   -- TAP: this is a hack too.  also, this sounds annoying.  suggest
   -- removing this prompt. Lets talk about this.  YOU: if responses
   -- allowed, prompt to record a response
  --if (listenreplies == 'y' and responsesallowed == 'y' or adminmode()) then 
  if (false) then
     read(aosd .. "recordresponse.wav", 2000);
     d = use();
     -- TAP: What is the expected value here, GLOBAL_MENU_RESPOND?
     -- Hasnt the default for Yes been 1?  
     if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_BACK or d == GLOBAL_MENU_RESPOND) then
	return d;
     end
  end
  
  -- default	
  return GLOBAL_MENU_NEXT;
end


-----------
-- playmessages
-----------

function playmessages (msgs, responsesallowed, listenreplies)
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
      elseif (d == GLOBAL_MENU_BACK) then  
	 read(aosd .. "previousmessage.wav", 1000);
      else -- default
	 read(aosd .. "nextmessage.wav", 1000);
      end

      d = use();
      -- check if a pre-emptive action was taken
      if (d ~= GLOBAL_MENU_MAINMENU and d ~= GLOBAL_MENU_BACK and d ~= GLOBAL_MENU_RESPOND) then
	 freeswitch.consoleLog("info", script_name .. ".playforum[" .. forumid .."] : playing msg [" .. current_msg[1] .. "]\n"); 
	 d = playmessage(current_msg, responsesallowed, listenreplies);
      end
  
      if (d == GLOBAL_MENU_BACK) then
	 if (current_msg_idx > 1) then
	    current_msg_idx = current_msg_idx - 1;
	    current_msg = prevmsgs[current_msg_idx];
	 end
      elseif (d == GLOBAL_MENU_RESPOND) then
	 read(aosd .. "okrecordresponse.wav", 500);
	 --d = use();
	 --if (d == GLOBAL_MENU_MAINMENU) then
	 -- return;
	 --end
	 --recordmessage handles this
	 local thread = current_msg[7];
	 if (thread == nil) then
	    thread = current_msg[1];
	 end
	 if (recordmessage (forumid, thread, moderated, maxlength, current_msg[6]) == GLOBAL_MENU_MAINMENU) then
	    return GLOBAL_MENU_MAINMENU;
	 end
      elseif (d ~= GLOBAL_MENU_MAINMENU) then
	 current_msg_idx = current_msg_idx + 1;
	 -- check to see if we are at the last msg in the forum
	 if (current_msg_idx > #prevmsgs) then
	    -- get next msg from the cursor
	    current_msg = msgs();
	    if (current_msg == nil) then
	       -- give a chance to go back if we are at the end of the
	       -- forum TAP: Total hack.  Develop a more general
	       -- prompt or parametrize
	       if (listenreplies == 'y') then
		  read(aosd .. "endforum.wav", 2000);
	       else
		  read(aosd .. "endreplies.wav", 1000);
	       end
	       d = use(); 
	       if (d == GLOBAL_MENU_BACK) then
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

      -- TAP: Are you sure you want Back to be accessible from here?
      if (d == GLOBAL_MENU_MAINMENU) then
	 return d;
      end

      session:execute("playback", "tone_stream://%(500, 0, 620)");
      freeswitch.consoleLog("info", script_name .. " : Recording " .. filename .. "\n")
      session:execute("record", filename .. " " .. maxlength .. " 80 2");
      --session:sleep(1000);
      d = use();

      if (d == GLOBAL_MENU_MAINMENU) then
	 os.remove(filename);
	 return d;
      end
      
      read(aosd .. "hererecorded.wav", 1000);
      read(filename, 1000);
      read(aosd .. "notsatisfied.wav", 2000);
      d = use();

      if (d == GLOBAL_MENU_MAINMENU) then
	 os.remove(filename);
	 return d;
      elseif (d ~= "1" and d ~= "2") then
	 os.remove(filename);
	 read(aosd .. "messagecancelled.wav", 500);
	 d = use();
	 if (d == GLOBAL_MENU_MAINMENU) then
	    return d;
	 else
	    return;
	 end
      end
   until (d == "1");
   
   phone_num = session:getVariable("caller_id_number");
   --freeswitch.consoleLog("info", script_name .. " : caller id is " .. phone_num .. "\n");
   user_query = "SELECT id FROM AO_user where number = ".. phone_num;
   cur = con:execute(user_query);
   user_id = cur:fetch();
   cur:close();
   
   if (user_id == nil) then
      -- first time caller
      create_user_query = "INSERT INTO AO_user (number, allowed, admin) VALUES ('" ..session:getVariable("caller_id_number").."','y','n')";
      con:execute(create_user_query);
      freeswitch.consoleLog("info", script_name .. " : " .. create_user_query .. "\n");
      cur = con:execute("SELECT LAST_INSERT_ID()");
      user_id = cur:fetch();
      cur:close();
   end		

   freeswitch.consoleLog("info", script_name .. " : USER ID = " .. tostring(user_id) .. "\n");
   
   query1 = "INSERT INTO AO_message (user_id, content_file, date";
   query2 = " VALUES ('"..tostring(user_id).."','"..partfilename.."',".."now()";
   
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
   query2 = " VALUES ('"..id[1].."','"..forumid.."'";

   local position = "null";
   if (moderated == 'y' and not adminmode()) then
      status = MESSAGE_STATUS_PENDING;
   else
      status = MESSAGE_STATUS_APPROVED;
      -- TAP: I dont like that all messages need a position.  That
      -- should be the exception rather then the rule.  The default
      -- should be ordering by date, with special messages promoted
      -- using the position field.
      if (thread == nil) then
	 cur = con:execute("SELECT MAX(mf.position) from AO_message_forum mf, AO_message m WHERE mf.message_id = m.id AND m.lft = 1 AND mf.forum_id = " .. forumid .. " AND mfstatus = " .. MESSAGE_STATUS_APPROVED );
	 if (cur == nil) then
	    position = 1;
	 else	 
	    position = tonumber(cur:fetch()) + 1;
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
	
   if (postingallowed == 'y' or adminmode()) then
      repeat
	 read(aosd .. "recordorlisten.wav", 3000);
	 d = tonumber(use());
	 if (d == GLOBAL_MENU_MAINMENU) then
	    return;
	 end
	 if (d == 1) then
	    read(aosd .. "okrecord.wav", 1000);
	    if (use() == GLOBAL_MENU_MAINMENU) then
	       return;
	    end
	    if (recordmessage(forumid, nil, moderated, maxlength, nil) == GLOBAL_MENU_MAINMENU) then
	       return;
	    end
	    read(aosd .. "backtoforum.wav", 1000);
	    -- else continue to playing messages
	 end
      until (d ~= 1);
      
      -- TAP: Wouldnt you want to drive users to listening to messages
      -- even in the case of bad / no input?  
      read(aosd .. "okplay.wav", 1000);
   end
 
   if (use() == GLOBAL_MENU_MAINMENU) then
      return;
   end

   if (responsesallowed == 'y' or adminmode()) then
      read(aosd .. "instructions.wav", 1000);
   else
      read(aosd .. "instructions_noresponse.wav", 1000);
   end
    
   if (use() == GLOBAL_MENU_MAINMENU) then
      return;
   end

   playmessages(getmessages(forumid), 'y', 'y');
   return;
end


-----------
-- MAIN 
-----------

-- answer the call
session:answer();

-- sleep for a sec
session:sleep(1000);

while (1) do
   -- choose a forum
   forumid = chooseforum();
  
   -- play the forum
   playforum(forumid);

   -- go back to the main menu
   read(aosd .. "mainmenu.wav", 1000);
end

-- say goodbye 
read(bsd .. "/zrtp/8000/zrtp-thankyou_goodbye.wav", 1000);

hangup();
