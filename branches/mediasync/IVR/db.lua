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

opencursors = {};
--[[
-------------------------------------
------- get_table_one_row ----------- 
-------------------------------------

	returns a table with one result row,
	or nil if no record found
-------------------------------------
--]]

function get_table_one_row(table, cond, fields)
	fields = fields or "*";
	local sql_statement = " SELECT " .. fields .. " FROM " .. table .. " WHERE " .. cond .. " LIMIT 0,1";
	freeswitch.consoleLog("info", script_name .. " : " .. sql_statement .. "\n");
	local cursor = assert (con:execute (sql_statement));
	local row = {}
	row = cursor:fetch(row);
	cursor:close();
	return row;
end

--[[
-------------------------------------------
------- get_table_rows -------------------- 
-------------------------------------------

	returns iterable cursor with resultset
-------------------------------------------
--]]

function get_table_rows(table, cond, fields)
	fields = fields or "*";
	local sql_statement = " SELECT " .. fields .. " FROM " .. table .. " WHERE " .. cond;
	freeswitch.consoleLog("info", script_name .. " : " .. sql_statement .. "\n");
	return rows(sql_statement);
end

--[[
-------------------------------------------
------- get_table_field ------------------- 
-------------------------------------------

	returns a single-value (i.e. not a table)
	from the db, or nil if no record found
-------------------------------------------
--]]

function get_table_field(table, fieldname, cond)
	local sql_statement = " SELECT " .. fieldname .. " FROM " .. table .. " WHERE " .. cond .. " LIMIT 0,1";
	freeswitch.consoleLog("info", script_name .. " : " .. sql_statement .. "\n");
	local cursor = assert (con:execute (sql_statement));
	local row = {}
	row = cursor:fetch(row);
	cursor:close();
	if row == nil then
		return row;
	else
		return row[1];
	end
	
end

--[[
-------------------------------------------
------- insert_into_table ----------------- 
-------------------------------------------

	inserts the name_value table into 
	the given table
	return inserted id
-------------------------------------------
--]]

function insert_into_table(table, name_vals)
	local sql_statement = " INSERT INTO " .. table .. " ( ";
	
	for name, val in pairs(name_vals) do
		sql_statement = sql_statement .. "`" ..name .. "`, ";
   	end
   	-- remove trailing space and comma
	sql_statement = sql_statement:sub(1, -3);
	sql_statement = sql_statement .. ") VALUES ( ";
	
	for name, val in pairs(name_vals) do
		sql_statement = sql_statement .. val .. ", ";
	end
	-- remove trailing space and comma
	sql_statement = sql_statement:sub(1, -3);
	sql_statement = sql_statement .. " ) ";
	
	freeswitch.consoleLog("info", script_name .. " : " .. sql_statement .. "\n");
	local success,err = con:execute(sql_statement);
	local id = nil;
	if (success) then
		local cur = con:execute("SELECT LAST_INSERT_ID()");
	   	id = tostring(cur:fetch());
	   	cur:close();	   	
	end
   	return id, err;
end

--[[
-------------------------------------------
------- update_table ---------------------- 
-------------------------------------------

	updates the table with the given data
	for the given condition

	returns nothing
-------------------------------------------
--]]

function update_table(table, name_vals, cond)
	local sql_statement = " UPDATE " .. table .. " SET ";
	
	for name, val in pairs(name_vals) do
		--freeswitch.consoleLog("info", script_name .. " : name:" .. name .. ' val:'.. val  .. "\n");
		sql_statement = sql_statement .. "`" .. name .. "` = " .. val .. ", ";
   	end
   	-- remove trailing space and comma
	sql_statement = sql_statement:sub(1, -3);
	if (cond ~= nil) then
		sql_statement = sql_statement .. " WHERE " .. cond;
	end
	
	freeswitch.consoleLog("info", script_name .. " : " .. sql_statement .. "\n");
	con:execute(sql_statement);
	return;
	
end

--[[
-------------------------------------------
------- delete_table ---------------------- 
-------------------------------------------

	deletes from the given table
	for records with the given condition

	returns nothing
-------------------------------------------
--]]

function delete_from_table(table, cond)
	local sql_statement = " DELETE FROM " .. table;
	
	if (cond ~= nil) then
		sql_statement = sql_statement .. " WHERE " .. cond;
	end
	
	freeswitch.consoleLog("info", script_name .. " : " .. sql_statement .. "\n");
	con:execute(sql_statement);
	return;
	
end

--[[
-------------------------------------------
----------------- rows -------------------- 
-------------------------------------------

	helper function for returning cursors
	(not meant for public access). Will
	error if caller uses the iterator
	after it has returned nil (signalling
	end of the resultset).
-------------------------------------------
--]]

function rows (sql_statement)
	local cursor = assert (con:execute (sql_statement));
	table.insert(opencursors, cursor);
	return function ()
		local row = {};
		--[[
			You need to pass row into the fetch method in order to populate the
			table correctly (will return just the first field of the resultset). 
			You need to assign the result of the fetch in order
			to properly check for the end of the resultset (will populate the table
			with nil values).
		--]]
		row = cursor:fetch(row);
		if (row == nil) then
			cursor:close();
		end
		return row;
	end
end
