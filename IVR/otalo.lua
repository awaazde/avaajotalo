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

script_name = "otalo.lua";
digits = "";
arg = {};

sessid = os.time();
userid = nil;
adminforums = {};

-- set the language, check if line is restricted
destination = session:getVariable("destination_number");
line_info = row("SELECT language, open, dialstring_prefix, dialstring_suffix, callback, personalinbox, quota, id, checkpendingmsgs FROM ao_line WHERE number LIKE '%" .. destination .. "%'");
aosd = basedir .. "/scripts/AO/sounds/" .. line_info[1] .. "/";		

-- responder section-specific sounds
anssd = aosd .. "answer/";

-- tagfiles
tagsd = aosd .. "tag/";

local open = line_info[2];
local DIALSTRING_PREFIX = line_info[3];
local DIALSTRING_SUFFIX = line_info[4];
local callback_allowed = line_info[5];
local personal_inbox = line_info[6];
local quota_imposed = line_info[7];
local lineid = line_info[8];
local checkpendingmsgs = line_info[9];

logfilename = logfileroot .. "inbound_" .. lineid .. ".log";
logfile = io.open(logfilename, "a");
logfile:setvbuf("line");

caller = session:getVariable("caller_id_number");
caller = caller:sub(-10);
freeswitch.consoleLog("info", script_name .. " : caller id = " .. caller .. "\n");
uid = row("SELECT id, allowed, balance FROM ao_user WHERE number = " .. caller);
local balance = nil;

if (uid ~= nil) then
	local allowed = uid[2];
	if (allowed == 'n') then
		-- number not allowed; exit
		return;
	end
	
	userid = tostring(uid[1]);
	balance = tonumber(uid[3]);
else
	if (open == 1) then
	   -- first time caller
	   query = "INSERT INTO ao_user (number, allowed) VALUES ('" ..caller.."','y')";
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

      if (obj['digit'] == GLOBAL_MENU_SKIP_FWD) then
	 digits = GLOBAL_MENU_SKIP_FWD;
	 return "break";
      end

      if (obj['digit'] == GLOBAL_MENU_SEEK_BACK) then
	 return "seek:-10";
      end

      if (obj['digit'] == GLOBAL_MENU_REPLAY) then
     	digits = GLOBAL_MENU_REPLAY;
     	return "break";
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

function getmessages (forumid, tagid)
   local query = "SELECT message.id, message.content_file, message.summary_file, message.rgt, message.thread_id, forum.id, forum.responses_allowed, forum.moderated, message_forum.status, forum.confirm_recordings, forum.max_user_resp_len ";
   query = query .. " FROM ao_message message, ao_message_forum message_forum, ao_forum forum ";
   query = query .. " WHERE forum.id = " .. forumid .. " AND message_forum.forum_id = " .. forumid .. " AND message.id = message_forum.message_id AND message.lft = 1";
   query = query .. " AND message_forum.status = " .. MESSAGE_STATUS_APPROVED;
   if (tagid ~= nil) then
   		query = query .. " AND EXISTS (SELECT 1 ";
   		query = query .. " 				FROM ao_message_forum_tags mf_tags ";
   		query = query .. " 				WHERE mf_tags.message_forum_id = message_forum.id AND mf_tags.tag_id = " .. tagid .. ") ";
   end
   -- Sort first by position AND then date
   query = query .. " ORDER BY message_forum.position DESC, message.date DESC";
   freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
   return rows(query);
end


-----------
-- getreplies
-----------

function getreplies (thread)
   local query = "SELECT message.id, message.content_file, message.summary_file, message.rgt, message.thread_id, forum.id, forum.responses_allowed, forum.moderated, message_forum.status, forum.confirm_recordings, forum.max_user_resp_len ";
   query = query .. " FROM ao_message message, ao_message_forum message_forum, ao_forum forum ";
   query = query .. " WHERE message.thread_id = " .. thread .. " AND message_forum.message_id = message.id ";
   query = query .. " AND message_forum.status = " .. MESSAGE_STATUS_APPROVED .. " AND message_forum.forum_id = forum.id ";
   query = query .. " ORDER BY message.lft";
   freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
   return rows(query);
end


-----------
-- getusermessages
-----------

function getusermessages (lineid)
   local query = "SELECT message.id, message.content_file, message.summary_file, message.rgt, message.thread_id, forum.id, forum.responses_allowed, forum.moderated, message_forum.status, forum.confirm_recordings, forum.max_user_resp_len ";
   query = query .. " FROM ao_message message, ao_message_forum message_forum, ao_forum forum, ao_line_forums line_forum ";
   query = query .. " WHERE message.id = message_forum.message_id AND message.lft = 1 AND message.user_id = " .. userid;
   query = query .. " AND message_forum.forum_id = forum.id AND line_forum.forum_id = forum.id AND line_forum.line_id = " .. lineid;
   query = query .. " ORDER BY message.date DESC";
   freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
   return rows(query);
end


-----------
-- getpendingmessages
-----------

function getpendingmessages (lineid)
   local query = "SELECT message.id, message.content_file, message.summary_file, message.rgt, message.thread_id, forum.id, forum.responses_allowed, forum.moderated, message_forum.status, forum.confirm_recordings, forum.max_user_resp_len ";
   query = query .. "FROM ao_message message, ao_message_forum message_forum, ao_forum forum, ao_line_forums line_forum ";
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
   query = query .. "FROM ao_forum_responders fr, ao_line line, ao_line_forums lf, ao_forum forum ";
   query = query .. " WHERE line.number LIKE '%" .. destination .. "%' "; 
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
   query = query .. "FROM ao_message m, ao_message_forum mf ";
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
   
   local query = "SELECT forum.id, forum.name_file, line.id ";
   query = query .. "FROM ao_forum forum, ao_line line, ao_line_forums line_forum ";
   query = query .. " WHERE line.number LIKE '%" .. destination .. "%' "; 
   query = query .. " AND line_forum.line_id = line.id AND line_forum.forum_id = forum.id ";
   query = query .. " AND (forum.status IS NULL OR forum.status <> " .. FORUM_STATUS_INACTIVE .. ") ";
   query = query .. " ORDER BY forum.id ASC";
   
   for row in rows (query) do
      i = i + 1;
      forumids[i] = row[1];
      forumnames[i] = row[2];
      lineid = row[3];
   end
   local numforums = i;
   
   local responder = isresponder(userid, destination);
   if (numforums == 1 and personal_inbox == 0 and checkpendingmsgs == 0 and not responder) then
   		-- go to the one and only forum straight away
   		playforum(forumids[1]);
   else
	   for i,fname in ipairs(forumnames) do
	      read(aosd .. "listento_pre.wav", 0);
	      if io.open(aosd .. fname,"rb") ~= nil then
	      	read(aosd .. fname, 0);
	      else
	      	local forumname = fname:sub(1,-5)
	      	speak(forumname);
	      end
	      read(aosd .. "listento_post.wav", 0);
	      read(aosd .. "digits/" .. i .. ".wav", 500);
	   end
   end
   
   local chkrepliesidx = -1;
   if (personal_inbox == 1) then
	   i = i + 1;
	   chkrepliesidx = i;
	   read(aosd .. "checkmyreplies.wav", 0);
	   read(aosd .. "digits/" .. chkrepliesidx .. ".wav", 1000);
   end

   local chkpendingidx = -1;
   if (adminmode and checkpendingmsgs == 1) then
   	  i = i + 1;
   	  chkpendingidx = i;
      read(aosd .. "checkpending.wav", 0);
      read(aosd .. "digits/" .. chkpendingidx .. ".wav", 1000);
   end
   
   local responderidx = -1;
   if (responder) then
   	  i = i + 1;
   	  responderidx = i;
   	  read(aosd .. "checkmyassignedquestions.wav", 0);
      read(aosd .. "digits/" .. responderidx .. ".wav", 1000);
   end
     
   d = tonumber(input());
   
   if (d ~= nil and d > 0 and d <= numforums) then
      freeswitch.consoleLog("info", script_name .. " : Selected Forum : " .. forumnames[d] .. "\n");
      read(aosd .. "okyouwant_pre.wav", 0);
      if io.open(aosd .. forumnames[d],"rb") ~= nil then
      	read(aosd .. forumnames[d], 0);
      else
      	local forumname = forumnames[d]:sub(1,-5)
      	session:speak(forumname);
      end
      read(aosd .. "okyouwant_post.wav", 0);
      playforum(forumids[d]);
   elseif (d == chkrepliesidx and personal_inbox == 1) then
      read(aosd .. "okyourreplies.wav", 0);
      input();
      playmessages(getusermessages(lineid), 'y');
   elseif (d == chkpendingidx and adminmode) then
      read(aosd .. "okpending.wav", 0);
      input();
      -- pending messages shouldn't have replies so
      -- leave the flag as 'n'
      playmessages(getpendingmessages(lineid), 'n');
   elseif (d == responderidx and responder) then
   	  if (io.open(aosd .. "okresponder.wav","rb") ~= nil) then
   	  	read(aosd .. "okresponder.wav", 0);
   	  else
   	  	read(aosd .. "okresponder.mp3", 0);
   	  end
      input();
   	  local rmsgs = get_responder_messages(userid);
      play_responder_messages(userid, rmsgs, adminforums);
   --elseif (d == GLOBAL_JUMP_MESSAGE) then
          --jumptomessage() ;
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

  if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_SKIP_BACK or d == GLOBAL_MENU_SKIP_FWD or d == GLOBAL_MENU_RESPOND or d == GLOBAL_MENU_INSTRUCTIONS) then
     return d;
  end

  if (status == MESSAGE_STATUS_PENDING and adminmode) then
     read(aosd .. "approvereject.wav", 2000);
     d = input();
     if (d == "1") then
     	local position = 'null';
     	local cur = con:execute("SELECT MAX(mf.position) from ao_message_forum mf, ao_message m WHERE mf.message_id = m.id AND m.lft = 1 AND mf.forum_id = " .. forumid .. " AND mf.status = " .. MESSAGE_STATUS_APPROVED );
	    -- only set position if we have to
	    local pos = cur:fetch()
	    cur:close();
	    if (pos ~= nil) then 
	       position = tonumber(pos) + 1;
	    end
	    local query = "UPDATE ao_message_forum SET status = " .. MESSAGE_STATUS_APPROVED .. ", position = " .. position .. " WHERE message_id = " .. id .. " AND forum_id = " .. forumid;
		con:execute(query);
		freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n")
		read(aosd .. "messageapproved.wav", 0);
     elseif (d == "2") then
     	local query = "UPDATE ao_message_forum SET status = " .. MESSAGE_STATUS_REJECTED .. " WHERE message_id = " .. id .. " AND forum_id = " .. forumid; 
		con:execute(query);
		freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n")
		read(aosd .. "messagerejected.wav", 0);
     elseif (d == GLOBAL_MENU_MAINMENU) then
	return d;
     end
  end
  
  if (hasreplies(id) and listenreplies == 'y') then
     read(aosd .. "listenreplies.wav", 6000);
     d = input();
	 
     if (d == "1") then
		-- quicken pace by getting rid of confirmation
		-- read(aosd .. "okreplies.wav", 500);
		d = input();
		if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_RESPOND or d == GLOBAL_MENU_SKIP_BACK or d == GLOBAL_MENU_SKIP_FWD or d == GLOBAL_MENU_INSTRUCTIONS) then
		   return d;
		end
		
		d = playmessages(getreplies(id), 'n');
		if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_RESPOND or d == GLOBAL_MENU_SKIP_BACK or d == GLOBAL_MENU_SKIP_FWD or d == GLOBAL_MENU_INSTRUCTIONS) then
		   return d;
		end
		
		read(aosd .. "backtoforum.wav", 500);
		d = input();
		if (d == GLOBAL_MENU_MAINMENU or d == GLOBAL_MENU_RESPOND or d == GLOBAL_MENU_SKIP_BACK or d == GLOBAL_MENU_SKIP_FWD or d == GLOBAL_MENU_INSTRUCTIONS) then
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
  -- only between threads, not between replies
  if (listenreplies == 'y' and (responsesallowed == 'y' or adminmode)) then
	  	read(aosd .. "instructions_between.wav", 4000)
	  	d = input();
	  	
	  	if (d ~= "") then
			return d;
		end
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
      return input();
   end

   local prevmsgs = {};
   table.insert(prevmsgs, current_msg);
   local current_msg_idx = 1;
   local d = "";
   
   while (current_msg ~= nil) do
      local adminmode = is_admin(current_msg[6], adminforums);
      local responsesallowed = current_msg[7];
      local moderated = current_msg[8];

      if (d == GLOBAL_MENU_RESPOND or d == GLOBAL_MENU_INSTRUCTIONS) then
		 -- if last msg played recd a response
		 read(aosd .. "backtomessage.wav", 1000);
		 -- do this first b/c its helpful to know when u are at the
		 -- first message
	  elseif (d == GLOBAL_MENU_REPLAY) then
	     -- do nothing
      elseif (current_msg_idx == 1) then
	 	read(aosd .. "firstmessage.wav", 1000);
      elseif (d == GLOBAL_MENU_SKIP_BACK) then  
	 	read(aosd .. "previousmessage.wav", 1000);
      else -- default
	 	read(aosd .. "nextmessage.wav", 1000);
      end

      d = input();
      -- check if a pre-emptive action was taken
      if (d ~= GLOBAL_MENU_MAINMENU and d ~= GLOBAL_MENU_SKIP_BACK and d ~= GLOBAL_MENU_SKIP_FWD and d ~= GLOBAL_MENU_RESPOND and d ~= GLOBAL_MENU_INSTRUCTIONS) then
	 	d = playmessage(current_msg, listenreplies);
      end

      if (d == GLOBAL_MENU_RESPOND) then
		 if (responsesallowed == 'y' or adminmode) then
		 	-- only attach replies to the top-level post
		 	if (listenreplies == 'n') then
		 		return d;
		 	end
		    read(aosd .. "okrecordresponse.wav", 500);
		    local thread = current_msg[5];		    
		    if (thread == nil) then
		       thread = current_msg[1];
		    end
		    local forumid = current_msg[6];
		    local confirm = current_msg[10];
		    local rgt = current_msg[4];
		    local maxlength = current_msg[11] or MAX_USER_RESP_LEN_DEF;
		    d = recordmessage (forumid, thread, moderated, maxlength, rgt, adminmode, confirm);
		    if (d == GLOBAL_MENU_MAINMENU) then
		       return d;
		    else
		       d = GLOBAL_MENU_RESPOND;
		    end
		 else
		    read(aosd .. "responsesnotallowed.wav", 500);
		    d = input();
		 end
     elseif (d == GLOBAL_MENU_SKIP_BACK) then
		 if (current_msg_idx > 1) then
		    current_msg_idx = current_msg_idx - 1;
		    current_msg = prevmsgs[current_msg_idx];
		 end
	 elseif (d == GLOBAL_MENU_INSTRUCTIONS) then
	 	 read(aosd .. "okinstructions.wav", 500);
		 read(aosd .. "instructions_full.wav", 500);
		 
		 d = input();
	 elseif (d == GLOBAL_MENU_REPLAY) then
	     -- do nothing
	 	
      elseif (d ~= GLOBAL_MENU_MAINMENU) then
		 current_msg_idx = current_msg_idx + 1;
		 -- check to see if we are at the last msg in the forum
		 if (current_msg_idx > #prevmsgs) then
		    -- get next msg from the cursor
		    current_msg = msgs();
		    -- speed up by not giving 'last message' warning... 
		    -- it's overkill for single answer case
		    --[[ 
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
			--]]
			if (current_msg ~= nil) then
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
   cur = con:execute("SELECT name_file, moderated, posting_allowed, responses_allowed, maxlength, filter_code, confirm_recordings, listening_allowed FROM ao_forum WHERE id = " .. forumid);
   cur:fetch(forum);
   cur:close();
   local forumname = forum[1];
   local moderated = forum[2];
   local postingallowed = forum[3];
   local responsesallowed = forum[4];
   local maxlength = forum[5];
   local filter_code = tonumber(forum[6]);
   local confirm_recordings = forum[7];
   local listeningallowed = forum[8];
   local d = "";
   local adminmode = is_admin(forumid, adminforums);
   local tagid = nil;
   local first_listen_opt = nil;
   local listen_opts_ids = {}
   local listen_opts_names = {}
   local pf_cnt = 0;
   
   repeat
   	  local i = 1;
   	  if ((postingallowed == 'y' and listeningallowed == 1) or adminmode) then
	   	 read(aosd .. "record.wav", 0);
	   	 i = i + 1;
	  elseif (postingallowed == 'n' and filter_code == FILTER_CODE_ALL_ONLY) then 	 
	  	 -- short-circuit prompt to go straight
	  	 -- to playing messages
	  	 break;
	  end
	  first_listen_opt = i;
	  
	  if (listeningallowed == 1) then
	   	  if (filter_code == FILTER_CODE_ALL_ONLY) then
		  	 read(aosd .. "listen.wav", 3000);
		  else
			 if (filter_code == FILTER_CODE_ALL_FIRST) then
			  	 read(aosd .. "listen_all.wav", 0);
			  	 read(aosd .. "digits/" .. i .. ".wav", 500);
			  	 listen_opts_ids[i] = nil;
			  	 listen_opts_names[i] = "listen_all.wav";
			  	 i = i + 1;
			 end
			 
			 local query = "SELECT tag.id, tag.tag_file ";
			 query = query .. "FROM ao_tag tag, ao_forum forum, ao_forum_tag forum_tag ";
			 query = query .. " WHERE forum.id = " .. forumid; 
			 query = query .. " AND forum_tag.forum_id = forum.id AND forum_tag.tag_id = tag.id ";
			 query = query .. " AND forum_tag.filtering_allowed = 1 ";
			 query = query .. " ORDER BY tag.id ASC";
			   
			 for row in rows (query) do
			      listen_opts_ids[i] = row[1];
			      listen_opts_names[i] = row[2];
			      read(aosd .. "listento_tag_pre.wav", 0);
			      read(tagsd .. listen_opts_names[i], 0);
			      read(aosd .. "listento_tag_post.wav", 0);
			      read(aosd .. "digits/" .. i .. ".wav", 500);
			      i = i + 1;
			 end
			 
			 if (filter_code == FILTER_CODE_ALL_LAST) then
			 	  read(aosd .. "listen_all.wav", 0);
			  	  read(aosd .. "digits/" .. i .. ".wav", 500);
			  	  listen_opts_ids[i] = nil;
			  	  listen_opts_names[i] = "listen_all.wav";
			 end
		  end
	  end 
	  d = input();
	  if (d == GLOBAL_MENU_MAINMENU) then
	     return;
	  end
	  -- if the option was either legally chosen or there is only the option to record
	  if (((postingallowed == 'y' or adminmode) and d == "1") or (postingallowed == 'y' and listeningallowed == 0)) then
	  	 if (listeningallowed == 1) then
	  	    -- otherwise this is redundant
	     	read(aosd .. "okrecord.wav", 1000);
	     end
	     if (recordmessage(forumid, nil, moderated, maxlength, nil, adminmode, confirm_recordings) == GLOBAL_MENU_MAINMENU) then
	        return;
	     end
	     read(aosd .. "backtoforum.wav", 1000);
	     -- else continue to playing messages
	  elseif (d == "") then
	     sleep(6000);
	  end
	  
	  pf_cnt = check_abort(pf_cnt, 4)
   until (d ~= "" and tonumber(d) >= first_listen_opt);
   
   if (postingallowed == 'y' or adminmode) then
   		if (filter_code == FILTER_CODE_ALL_ONLY) then
   			read(aosd .. "okplay.wav", 1000);
   		else
   			tagid = listen_opts_ids[tonumber(d)]
   			if (tagid == nil) then
   				read(aosd .. "okplay_all.wav", 1000);
   			else
   				read(aosd .. "okplaytag_pre.wav", 0)
   				read(tagsd .. listen_opts_names[tonumber(d)], 0);
		      		read(aosd .. "okplaytag_post.wav", 0);
		     
   			end
   		end
   elseif (filter_code ~= FILTER_CODE_ALL_ONLY) then
   		tagid = listen_opts_ids[tonumber(d)]
		if (tagid == nil) then
			read(aosd .. "okplay_all.wav", 1000);
		else
	   		read(aosd .. "okyouwant_tag_pre.wav", 0)
			read(tagsd .. listen_opts_names[tonumber(d)], 0);
	      		read(aosd .. "okyouwant_tag_post.wav", 0);
	    end
   end
   
   

	--Disabling instructions at the beginning when there will be
	--instructions in between messages.
   
   --if (responsesallowed == 'y' or adminmode) then
    --  read(aosd .. "instructions_short.wav", 1000);
   --else
   if (responsesallowed == 'n' and adminmode == false) then
   		read(aosd .. "instructions_short_noresponse.wav", 1000);
   end
   
   d = input(); 
   if (d == GLOBAL_MENU_MAINMENU) then
      return;
   elseif (d == GLOBAL_MENU_INSTRUCTIONS) then
   	  read(aosd .. "okinstructions.wav", 500);
	  read(aosd .. "instructions_full.wav", 500);
	 
	  d = input();
   end
   
   playmessages(getmessages(forumid, tagid), 'y');
   return;
end
-----------
-- get_msgid
-----------

function get_msgid(file, delay)

   if (digits == "") then
      logfile:write(sessid, "\t",
		    caller, "\t", destination, "\t",
		    os.time(), "\t", "Prompt", "\t", file, "\n");
      digits = session:read(5, 5, file, delay, "#");
      if (digits ~= "") then
	 logfile:write(sessid, "\t", caller, "\t", destination, "\t", os.time(), "\t", "dtmf", "\t", file, "\t", digits, "\n"); 
      end
   end
end

-----------
-- jumptomessage 
-----------
function jumptomessage()
   local d = "-1";
   repeat
      read(aosd .. "code.wav", 2000);   -- Expecting 1 digit forum ID or press Zero to return mainmenu
      d = input();
   until (d ~= "");
   if (d == GLOBAL_MENU_MAINMENU) then
      return;
   else
	   id_forum = tonumber(d);
	   get_msgid("", 2000)  -- Expecting 5 Digit Msg ID
	   d = input();
	   if (d ~= "") then
	      id_msg = tonumber(d);
	      id_msg = id_msg % 100000;
	      local query = "SELECT message.id, message.content_file, message.summary_file, message.rgt, message.thread_id, forum.id, forum.responses_allowed, forum.moderated, message_forum.status ";
	      query = query .. " FROM ao_message message, ao_message_forum message_forum, ao_forum forum ";
	      query = query .. " WHERE forum.id = " .. tostring(id_forum) .. " AND message_forum.forum_id = " .. tostring(id_forum) ;
	      query = query .. " AND message.id = " .. tostring(id_msg) .. " AND message_forum.message_id = "	.. tostring(id_msg);
	      freeswitch.consoleLog("info", script_name .. " : " .. query .. "\n");
	      playmessage(row(query),'y');
	   end
   end
      
end 

-----------
-- MAIN 
-----------
-- get admin permissions
local query = "SELECT admin.forum_id FROM ao_admin admin, ao_forum forum, ao_line line, ao_line_forums line_forum "; 
query = query .. " WHERE line.number LIKE '%" .. destination .. "%' "; 
query = query .. " AND line_forum.line_id = line.id AND line_forum.forum_id = forum.id ";
query = query .. " AND (forum.status IS NULL OR forum.status <> " .. FORUM_STATUS_INACTIVE .. ") ";
query = query .. " AND user_id =  " .. userid;
query = query .. " AND admin.forum_id =  forum.id ";

adminrows = rows(query);
adminforum = adminrows();
while (adminforum ~= nil) do
	-- use the table as a set to make lookup faster
	adminforums[adminforum[1]] = true;
	freeswitch.consoleLog("info", script_name .. " : adminforum = " .. adminforum[1] .. "\n");
	adminforum = adminrows();
end

if (callback_allowed == 1 and (quota_imposed == 0 or is_sufficient_balance(userid))) then
	-- Allow for missed calls to be made
	session:execute("ring_ready");
	api = freeswitch.API();
	local uuid = session:getVariable('uuid');
	local mc_cnt = 0;
    while (api:executeString('eval uuid:' .. uuid .. ' ${Channel-Call-State}') == 'RINGING') do
	 	session:sleep(3000);
	 	mc_cnt = check_abort(mc_cnt, 11)
  	end
		freeswitch.consoleLog("info", script_name .. " : woke up \n");
	
	-- decrease the caller's balance if necessary
	if (quota_imposed == 1 and balance > 0) then
		local query = " UPDATE ao_user ";
	   	query = query .. " SET balance = balance - 1 ";
	   	query = query .. " WHERE id = " .. userid;
	   	con:execute(query);
	   	freeswitch.consoleLog("info", script_name .. " : query : " .. query .. "\n");
	end
	
	-- Missed call; 
	-- call the user back
	session:hangup();
	local vars = '{';
	vars = vars .. 'ignore_early_media=true';
	vars = vars .. ',caller_id_number='..caller;
	vars = vars .. ',origination_caller_id_number='..destination;
	vars = vars .. ',origination_caller_id_name='..destination;
	vars = vars .. '}'
	session = freeswitch.Session(vars .. DIALSTRING_PREFIX .. caller .. DIALSTRING_SUFFIX)
	
	-- wait a while before testing
	session:sleep(2000);
	if (session:ready() == false) then
		hangup();
	end
else
	-- No callback allowed; just answer the call
	session:answer();
end

-- put hangup hook after session init in case of missed call;
-- if old session closes and hangup() is invoked, the db conn
-- and logfile will get clobbered
session:setVariable("playback_terminators", "#");
session:setHangupHook("hangup");
session:setInputCallback("my_cb", "arg");
session:set_tts_parms("flite", "awb");

logfile:write(sessid, "\t", caller, "\t", destination,
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
   mm_cnt = check_abort(mm_cnt, 5)
end

-- say goodbye 
read(bsd .. "/zrtp/8000/zrtp-thankyou_goodbye.wav", 1000);

hangup();
