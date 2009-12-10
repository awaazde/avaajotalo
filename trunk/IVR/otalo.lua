#!/usr/local/bin/lua


-- INCLUDES

require "luasql.mysql";

-- TODO: figure out how to get the local path
dofile("/usr/local/freeswitch/scripts/AO/paths.lua");

script_name = "otalo.lua";

sessid = os.time();
digits = "";
currfile = "";
arg = {};

session:setVariable("playback_terminators", "#");
session:setHangupHook("hangup");
session:setInputCallback("my_cb", "arg");

MESSAGE_STATUS_PENDING = 0;
MESSAGE_STATUS_APPROVED = 1;
MESSAGE_STATUS_REJECTED = 2;

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
-- my_cb
-----------

function my_cb(s, type, obj, arg)
   freeswitch.console_log("info", "\ncallback: [" .. obj['digit'] .. "]\n")

   if (type == "dtmf") then
      
      logfile:write(sessid, "\t", session:getVariable("caller_id_number"), "\t", os.time(), "\t", currfile, "\t", "dtmf", "\t", obj['digit'], "\n"); 
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
	 	--session:speak("start over");
        return "seek:0";
      end
      
            
      if (obj['digit'] == GLOBAL_MENU_PAUSE) then
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
		 if (digits ~= "0") then
		    use()
		    read(aosd .. "backtomessage.wav", 1000);
		 end
		 if (digits == "0") then
		    return "break";
		 end
		 use();
		 return;
      end


   else
      freeswitch.console_log("info", obj:serialize("xml"));
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
-- chooseforum
-----------

function chooseforum ()
   forumids = {};
   forumnames = {};
   
   read(aosd .. "welcome.wav", 500);

   i = 0;
   for row in rows ("SELECT id, name_file FROM AO_forum ORDER BY id ASC") do      
      i = i + 1;
      forumids[i] = row[1];
      forumnames[i] = row[2];
      read(aosd .. "listento_pre.wav", 0);
      read(aosd .. forumnames[i], 0);
      read(aosd .. "listento_post.wav", 0);
      read(aosd .. "digits/" .. i .. ".wav", 500);
   end
   
   d = use();

   if (d == "") then
      return -1;
   else
      d = tonumber(d);
   end;

   if (d > 0 and d <= i) then
      freeswitch.consoleLog("info", script_name .. " : Selected Forum : " .. forumnames[d] .. "\n");
      
      
	  read(aosd .. "okyouwant_pre.wav", 0);
	  read(aosd .. forumnames[d], 0);
	  read(aosd .. "okyouwant_post.wav", 0);

      return forumids[d];
   else
      freeswitch.consoleLog("info", script_name .. " : No such forum number : " .. d .. "\n");
      session:sleep(500);
      read(aosd .. "noforum.wav", 500);
      use();
      return -1;
   end
end


-----------
-- playcontent
-----------

function playcontent (extra, content)
   local d;
   if (extra ~= nil and extra ~= "") then
   	 currfile = sd .. extra;
	 logfile:write(sessid, "\t", session:getVariable("caller_id_number"), "\t", os.time(), "\t", currfile, "\t", "play", "\n"); 
	 session:streamFile(sd .. extra);
	 session:sleep(1000);
	 
	 d = use();
	 if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_NEXT or d == GLOBAL_MENU_BACK or d == GLOBAL_MENU_RESPOND) then
      	return d;
   	 end
   
     read(aosd .. "morecontent.wav", 2000);
     d = use();
     if (d == "1") then
	 	read(aosd .. "okcontent.wav", 500);
	 else
	 	return GLOBAL_MENU_NEXT;
	 end
   end
      
   currfile = sd .. content;
   logfile:write(sessid, "\t", session:getVariable("caller_id_number"), "\t", os.time(), "\t", currfile, "\t", "play", "\n"); 
   session:streamFile(sd .. content);
   session:sleep(1000);
   
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
	
   if (postingallowed == 'y' or adminmode()) then
      read(aosd .. "recordorlisten.wav", 3000);
      d = use();

      if (d == "1") then
	 	  read(aosd .. "okrecord.wav", 1000);
	      d = recordmessage(forumid, nil, moderated, maxlength);
	      if (d == GLOBAL_MENU_MAINMENU ) then
	  		  return d;
	      end
		  -- else continue to playing messages
		  read(aosd .. "backtoforum.wav", 1000);
		  -- don't check input here; it will be checked when it comes back around
		  -- to this function
		  return GLOBAL_MENU_REPLAY;
	  elseif (d == "2") then
	  	  read(aosd .. "okplay.wav", 1000);
	  else -- global command
	  	  return d;
      end
      
   end

   if (responsesallowed == 'y' or adminmode()) then
   	  read(aosd .. "instructions.wav", 1000);
   else
   	  read(aosd .. "instructions_noresponse.wav", 1000);
   end
   
   d = use();
   if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_BACK) then
      return d;
   end
   
   -- get the first top-level message for this forum
   cur = con:execute("SELECT COUNT(*) from AO_message_forum mf, AO_message m WHERE mf.message_id = m.id AND m.lft = 1 AND forum_id = " .. forumid .. " AND status = " .. MESSAGE_STATUS_APPROVED );
   local first_position = cur:fetch();
   first_position = tonumber(first_position);
   local prevmsgs = {};
   local msgs = getmessages(forumid);
   local current_msg_idx = 1;
   local current_msg = msgs();
   
   if (current_msg == nil) then
   	  read(aosd .. "nomessages.wav", 1000);
   	  return GLOBAL_MENU_MAINMENU;
   end
   
   d = "";
   while (current_msg ~= nil) do
   	  local msgid = current_msg[1];
   	  local position = tonumber(current_msg[4]);
   	  local rgt = tonumber(current_msg[6]);
   	   
   	  if (d == GLOBAL_MENU_RESPOND or d == GLOBAL_MENU_REPLAY) then
   	  	-- if last msg played recd a response
   	  	read(aosd .. "backtomessage.wav", 1000);
	  elseif (d == GLOBAL_MENU_BACK) then  -- do this before next in case you go back to first msg
	  	read(aosd .. "previousmessage.wav", 1000);
	  elseif (position == first_position) then
	 	read(aosd .. "firstmessage.wav", 1000);
	  else -- default
		read(aosd .. "nextmessage.wav", 1000);
	  end

	  d = use();
	  
	  -- check if a pre-emptive action was taken
	  if (d ~= GLOBAL_MENU_MAINMENU and d ~= GLOBAL_MENU_BACK and d~= GLOBAL_MENU_NEXT and d ~= GLOBAL_MENU_RESPOND) then
	  	freeswitch.consoleLog("info", script_name .. ".playforum[" .. forumid .."] : playing msg [" .. msgid .. "]\n"); 
   	  	d = playmessage(current_msg, responsesallowed);
   	  end
   	  
   	  if (current_msg_idx > #prevmsgs) then
    	-- add the current msg to the stack
    	table.insert(prevmsgs, current_msg);
	  end
   	   
   	  if (d == GLOBAL_MENU_MAINMENU) then
	      return d;
	  elseif (d == GLOBAL_MENU_BACK) then
	      if (current_msg_idx == 1) then
	        -- go back from top post
	        -- go to the forum menu
	      	return GLOBAL_MENU_REPLAY;
	      else
	      	current_msg_idx = current_msg_idx - 1;
	   	  	current_msg = prevmsgs[current_msg_idx];
	   	  end
	  elseif (d == GLOBAL_MENU_NEXT) then
        current_msg_idx = current_msg_idx + 1;
        -- check to see if we are at the last msg in the forum
        if (current_msg_idx > first_position) then
        	-- let the end of the forum check happen below
        	current_msg = nil;
        -- check to see if we are at the end of prevmsgs    
        elseif (current_msg_idx > #prevmsgs) then
        	-- get next msg from the cursor
        	current_msg = msgs();
        else
        	-- get msg from the prev list
        	current_msg = prevmsgs[current_msg_idx];
        end
	  elseif (d == GLOBAL_MENU_RESPOND) then
	   	  read(aosd .. "okrecordresponse.wav", 500);
	   	  d = recordmessage (forumid, msgid, moderated, maxlength, rgt);
	   	  if (d == GLOBAL_MENU_MAINMENU) then
	      	  return d;
	      end
	  elseif (d == GLOBAL_MENU_REPLAY) then
	   		-- do nothing; special case if user pressed back from 1st reply 
	  end
	  
	  if (current_msg == nil) then
	  	-- give a chance to go back if we are at the end of the forum
	  	read(aosd .. "endforum.wav", 2000);
        d = use(); 
		if (d == GLOBAL_MENU_BACK) then
			current_msg_idx = current_msg_idx - 1;
	   	  	current_msg = prevmsgs[current_msg_idx];
	   	end
	  end
	  
   end

   return GLOBAL_MENU_MAINMENU;
end

-----------
-- playmessage
-----------

function playmessage (msg, responsesallowed)
  local id = msg[1];
  local content = msg[2];
  local extra = msg[3];
  local position = msg[4];
  local lft = tonumber(msg[5]);
  local rgt = tonumber(msg[6]);
  
  d = playcontent(extra, content);

  -- no short circuit for next here; still want to prompt to listen to replies
  if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_BACK or d == GLOBAL_MENU_RESPOND) then
  	return d;
  end
  
  if (rgt > 2) then
	 read(aosd .. "listenreplies.wav", 2000);
	 d = use();
	 
	 -- no short circuit for next here; still want to prompt to record a response
	 if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_BACK or d == GLOBAL_MENU_RESPOND) then
	  	return d;
	 end

	 if (d == "3") then
	    read(aosd .. "okreplies.wav", 500);
	    d = use();
	 
	 	-- just like when we are about to play messages in the forum
	 	-- (instructions), don't short circuit on next
		if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_BACK or d == GLOBAL_MENU_RESPOND) then
	  		return d;
	    end
	    
	    -- get the first reply
	    local prevreplies = {};
	    local replies = getreplies(id);
	    local current_reply_idx = 1;
	    local current_reply = replies();
	    
	    d = "";
	    while (current_reply ~= nil) do
		   	  local replyid = current_reply[1];
		   	  local reply_content = current_reply[2];
  			  local reply_extra = current_reply[3];
  			  local reply_lft = tonumber(current_reply[5]);
		   	  local reply_rgt = tonumber(current_reply[6]);
		   	  
		   	  if (d == GLOBAL_MENU_RESPOND) then
		   	  	-- if last msg played recd a response
		   	  	read(aosd .. "backtomessage.wav", 1000);
		   	  elseif (d == GLOBAL_MENU_BACK) then
		   	  	read(aosd .. "previousmessage.wav", 1000);
		   	  elseif (reply_lft == 2) then
			 	read(aosd .. "firstmessage.wav", 1000);
			  else
				read(aosd .. "nextmessage.wav", 1000);
			  end
			  
			   d = use();
			   
			   -- check if a pre-emptive action was taken
			   if (d ~= GLOBAL_MENU_MAINMENU and d ~= GLOBAL_MENU_BACK and d~= GLOBAL_MENU_NEXT and d ~= GLOBAL_MENU_RESPOND) then
		   	  	  d = playcontent(reply_extra, reply_content);
		   	   end	   
			   
			   if (current_reply_idx > #prevreplies) then
		    	-- add the current msg to the stack
		    	table.insert(prevreplies, current_reply);
			   end
		   	   
		   	   if (d == GLOBAL_MENU_MAINMENU) then
			      return d;
			   elseif (d == GLOBAL_MENU_BACK) then
			      if (current_reply_idx == 1) then
			        -- go back from top reply
			        -- go to the original msg
			      	return GLOBAL_MENU_REPLAY;
			      else
			   	  	current_reply_idx = current_reply_idx - 1;
	   	  			current_reply = prevreplies[current_reply_idx];
			   	  end
			   elseif (d == GLOBAL_MENU_RESPOND) then
			   	  -- ASSUMING FLAT threads (i.e. no reply to replies)	
			   	  return d;
			   else -- default is go to next
			   	  current_reply_idx = current_reply_idx + 1;
			   	   -- check to see if we are at the last reply
		          if (reply_rgt == rgt-1) then
		        	-- let the end of the replies check happen below
		        	current_reply = nil;  
			      -- check to see if we are at the end of prevreplies
		          elseif (current_reply_idx > #prevreplies) then
		        	-- get next reply from the cursor
		        	current_reply = replies();
		          else
		        	-- get reply from the prev list
		        	current_reply = prevreplies[current_reply_idx];
		          end
			   end
			   
			   if (current_reply == nil) then
			   	  -- give a chance to go back if we are at the end of the replies
			  	  read(aosd .. "endreplies.wav", 2000);
		          d = use(); 
				  if (d == GLOBAL_MENU_BACK) then
					current_reply_idx = current_reply_idx - 1;
			   	  	current_reply = prevreplies[current_reply_idx];
			   	  end
			   end
	    end	    	      
	    
  	end -- close if choose to listen to replies
  end -- close check for replies
  
   -- if responses allowed, prompt to record a response
  if (responsesallowed == 'y' or adminmode()) then 
    read(aosd .. "recordresponse.wav", 2000);
    d = use();
    if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_NEXT or d == GLOBAL_MENU_BACK or d == GLOBAL_MENU_RESPOND) then
  		return d;
    end
  end
  
  -- default	
  return GLOBAL_MENU_NEXT;
end

-----------
-- getmessages
-----------

function getmessages (forumid)
   local query = "SELECT message.id, message.content_file, message.extra_content_file, message_forum.position, message.lft, message.rgt ";
   query = query .. "FROM AO_message message, AO_message_forum message_forum ";
   query = query .. "WHERE message_forum.forum_id = " .. forumid .. " AND message_forum.status = " .. MESSAGE_STATUS_APPROVED .. " AND message.id = message_forum.message_id AND message.lft = 1 ";
   query = query .. "ORDER BY message_forum.position DESC ";
   
   return rows(query);
end

-----------
-- getreplies
-----------

function getreplies (thread)
   local query = "SELECT message.id, message.content_file, message.extra_content_file, message_forum.position, message.lft, message.rgt, message.thread_id ";
   query = query .. "FROM AO_message message, AO_message_forum message_forum ";
   query = query .. "WHERE message.thread_id = " .. thread .. " AND message_forum.message_id = message.id AND message_forum.status = " .. MESSAGE_STATUS_APPROVED .. " ";
   query = query .. "ORDER BY message.lft";
   
   return rows(query);
end
-----------
-- recordmessage
-----------

function recordmessage (forumid, thread, moderated, maxlength, rgt)
   local forumid = forumid or nil;
   local thread = thread or nil;
   local maxlength = maxlength or 60000;
   local moderated = moderated or nil;
   local maxlength = maxlength or 60000;
   local rgt = rgt or 1;
   local partfilename = os.time() .. ".mp3";
   local filename = sd .. partfilename;

   repeat
      read(aosd .. "pleaserecord.wav", 1000);
      local d = use();
	  if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_BACK) then
	  	 return d;
	  end

      session:execute("playback", "tone_stream://%(500, 0, 620)");
      
      freeswitch.consoleLog("info", script_name .. " : Recording " .. filename .. "\n")
      session:execute("record", filename .. " " .. maxlength .. " 80 2");
      --Session:sleep(1000);
      use();
      
      read(aosd .. "hererecorded.wav", 1000);
      read(filename, 1000);
      read(aosd .. "notsatisfied.wav", 2000);
      d = use();
 
      if (d ~= "1" and d ~= "2") then
	 	read(aosd .. "messagecancelled.wav", 500);
	 	-- have to check use() first so it gets cleared for sure
	 	if (use() == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_MAINMENU) then
	 		freeswitch.consoleLog("info", script_name .. " : returning to mm after cancel msg \n");
	 		return GLOBAL_MENU_MAINMENU;
	 	else
	 		return GLOBAL_MENU_REPLAY;
	 	end
      end
   until (d == "1");
   
   phone_num = session:getVariable("caller_id_number");
   --freeswitch.consoleLog("info", script_name .. " : caller id is " .. phone_num .. "\n");
   user_query = "SELECT id FROM AO_user where number = ".. phone_num;
   cur = con:execute(user_query);
   user_id = cur:fetch();
   
   if (user_id == nil) then
   	  -- first time caller
   	  create_user_query = "INSERT INTO AO_user (number, allowed, admin) VALUES ('" ..session:getVariable("caller_id_number").."','y','n')";
   	  con:execute(create_user_query);
	   freeswitch.consoleLog("info", script_name .. " : " .. create_user_query .. "\n")
	   cur = con:execute("SELECT LAST_INSERT_ID()");
	   user_id = cur:fetch();
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
   freeswitch.consoleLog("info", script_name .. " : ID = " .. tostring(id[1]) .. "\n");
   
   query1 = "INSERT INTO AO_message_forum (message_id, forum_id";
   query2 = " VALUES ('"..id[1].."','"..forumid.."'";

   position = "null";
   if (moderated == 'y' and not adminmode()) then
	    status = MESSAGE_STATUS_PENDING;	    
   else
	    status = MESSAGE_STATUS_APPROVED;
	    if (thread == nil) then
		    cur = con:execute("SELECT COUNT(*) from AO_message_forum mf, AO_message m WHERE mf.message_id = m.id AND m.lft = 1 AND forum_id = " .. forumid .. " AND status = " .. MESSAGE_STATUS_APPROVED );
			position = cur:fetch();
			position = tonumber(position) + 1;
		end
   end
   query1 = query1 .. ", status, position)";
   query2 = query2 .. "," .. status .. ",".. position..")";

  query = query1 .. query2;
  con:execute(query);
  freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n")

   
   read(aosd .. "okrecorded.wav", 500);
   d = use();
   if (d == GLOBAL_MENU_MAINMENU) then
  	 return d;
   end
   
   -- replay either the forum or the message (if response)
   return GLOBAL_MENU_REPLAY;
end

-----------
-- MAIN 
-----------

-- answer the call
session:answer();

-- sleep for a sec
session:sleep(1000);

local forumid = -1;
while (1) do
   -- choose the forum
   while (forumid == -1) do
   	  forumid = chooseforum();
   end

   -- play the forum
   d = playforum(forumid);
   
   if (d ~= GLOBAL_MENU_REPLAY) then
	   -- go back to the main menu
	   read(aosd .. "mainmenu.wav", 1000);
	   forumid = -1;
   end
   
end

-- say goodbye 
read(bsd .. "/zrtp/8000/zrtp-thankyou_goodbye.wav", 1000);

hangup();
