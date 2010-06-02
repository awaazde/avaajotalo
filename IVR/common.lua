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

function read_no_bargein(file)
      logfile:write(sessid, "\t",
		    session:getVariable("caller_id_number"), "\t",
		    os.time(), "\t", "Prompt", "\t", file, "\n");
      session:streamFile(file);
      sleep(2000);
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

