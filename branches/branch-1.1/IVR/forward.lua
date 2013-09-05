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

--[[
--------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------
	Self-contained set of functionality for forward-2-friend.

	IMPORTANT NOTE: In order to use this module, your importing
	script *must* adhere to the following naming conventions:

		callernum => phone number of user (in or outbound caller)
		fwdsd -> default directory where the sound files for forward are located (not used if directory specified)

	DEPENDS ON:
		db.lua
		play_prompt(file, delay, promptsd) (in your common.lua)
		is_sufficient_balance(userid) (in your common.lua)
		input() (in your common.lua)
--------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------
--]]



--[[
-------------------------------------------
------------- CONSTANTS -------------------
-------------------------------------------
--]]
PHONE_NUM_TIMEOUTS = 3;
DEF_INPUT_DELAY = 4000;
PROMPT_SOUND_EXT = '.wav';

-- Should be consistent with Forum model's constants
NO_FORWARD = 0;
FORWARD = 1;
FORWARD_INBOUND_ONLY = 2;
FORWARD_OUTBOUND_ONLY = 3;

MAX_FORWARD_RECIPIENTS = 5;


--[[
-------------------------------------------
--------- read_phone_num ------------------
-------------------------------------------
--]]
function read_phone_num(delay, promptsd)
	delay = delay or DEF_INPUT_DELAY;
	promptsd = promptsd or fwdsd;
	if (promptsd:sub(-1) ~= '/') then
		-- add trailing slash
		promptsd = promptsd .. '/';
	end
	
	local callernum = callernum or caller;
	local file = promptsd .. "inputnumber" .. PROMPT_SOUND_EXT;
	local invalid_num_file = promptsd.."invalidnumber"..PROMPT_SOUND_EXT;
	
	if (digits == "") then
		logfile:write(sessid, "\t", callernum, "\t", destination, "\t", os.time(), "\t", "Prompt", "\t", file, "\n");
	  	-- allow 10 only
	  	digits = session:playAndGetDigits(10, 10, PHONE_NUM_TIMEOUTS, delay, "#", file, invalid_num_file, "\\d+");
      	if (digits ~= "") then
	 		logfile:write(sessid, "\t", callernum, "\t", destination, "\t", os.time(), "\t", "phnum", "\t", file, "\t", digits, "\n"); 
      	end
   	end
end

--[[
-------------------------------------------
---------------- forward ------------------
-------------------------------------------

	Prompt caller to enter phone numbers
	to pass the given message on to.

	The implementation of this method can
	be changed depending on the interaction
	you want to use to collect forwarding
	input from the caller. The below utility
	functions should be universally useful/used

	Current implementation: prompt caller to
	inter 10-digit numbers one at a time, each time
------------------------------------------- 
--]]
function forward(userid, messageid, forumid, surveyid, promptsd)
	promptsd = promptsd or fwdsd;
	local num_recipients = 0;
	local d = nil;
	
	-- check balance before proceeding
	if (is_sufficient_balance(userid)) then
		-- do this right away and add recipients in real time
		-- because we don't know when the hangup will happen
		local forwardid = create_forward_request(userid, messageid, forumid, surveyid);
		while (d ~= GLOBAL_MENU_MAINMENU and num_recipients < MAX_FORWARD_RECIPIENTS) do
			read_phone_num(nil, promptsd);
			d = input();
			if (d ~= nil and d ~= "") then
				add_forward_recipient(forwardid, d)
				play_prompt("okforwarded", nil, promptsd);
				num_recipients = num_recipients + 1;
			else
				-- if user is unable to successfully add a number, stop prompting
				break;
			end
			
		end
	else
		play_prompt("recharge", nil, promptsd);
	end
end

--[[
-------------------------------------------
--------- create_forward_request ----------
-------------------------------------------
	
	Setup a request to forward the given
	message from the given requestor

	forum and survey identification is optional
	and used for analytics/tracking purpose
	use forumid for inbound, use both forumid
	and surveyid for outbound
-------------------------------------------
--]]
function create_forward_request(requestorid, messageid, forumid, surveyid)
	name_vals = {requestor_id=requestorid, message_id=messageid, forum_id=forumid, survey_id=surveyid, created_on='now()'};
	return insert_into_table("ao_forward", name_vals);
end

--[[
-------------------------------------------
--------- add_forward_recipient -----------
-------------------------------------------
--]]
function add_forward_recipient(forwardid, recipient_num)
	userid = get_table_field('ao_user', 'id', 'number='..recipient_num);
	if (userid == nil) then
		name_vals = {number=recipient_num, allowed="'y'"};
		userid = insert_into_table('ao_user', name_vals);		
	end
	name_vals = {forward_id=forwardid, user_id=userid};
	return insert_into_table("ao_forward_recipients", name_vals);
end