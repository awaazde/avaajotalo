/*
 * Copyright (c) 2009 Regents of the University of California, Stanford University, and others
 * 
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License. You may obtain a copy of
 * the License at
 * 
 * http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations under
 * the License.
 */
package org.otalo.ao.client.model;

import java.math.BigDecimal;

public class User extends BaseModel {
	public static final String UNLIMITED_BALANCE = "999.00";
	public static final String BCAST_DISALLOW_BALANCE_THRESH = "0";
	// this doesn't have a backend equivalent because its represented by null
	// set it here because of strongly typed methods
	public static final int MAX_GROUPS_NO_LIMIT = -101;
	// make all of the following consistent with ao:models.py
	public static final int DISABLE_GROUP_ADD_REMOVE = -1;
	
	public User(JSOModel data) {
		super(data);
	}

	public String getNumber()
	{
		return getObject("fields").get("number");
	}
	
	public String getName()
	{
		return getObject("fields").get("name");
	}
	
	public String getDistrict()
	{
		return getObject("fields").get("district");
	}
	
	public String getTaluka()
	{
		return getObject("fields").get("taluka");
	}
	
	public String getVillage()
	{
		return getObject("fields").get("village");
	}
	
	public String getEmail()
	{
		return getObject("fields").get("email");
	}
	
	public String getBalance()
	{
		return getField("balance");
	}
	
	public int getMaxGroups()
	{
		String max = getField("max_groups");
		if ("null".equals(max))
			// no limit
			return MAX_GROUPS_NO_LIMIT;
		else
			return Integer.valueOf(max);
	}
}
