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

import java.util.ArrayList;
import java.util.List;

import org.otalo.ao.client.model.Message.MessageStatus;


public class Membership extends BaseModel {
	/* Order matters. The constants are mirrored in 
	 * server side code. The ordinal value of the first declared
	 * is 0 and then increases from there.
	 */
	public enum MembershipStatus {
		SUBSCRIBED("Joined"),
    UNSUBSCRIBED("Unsubscribed"),
    REQUESTED("Requested"),
    INVITED("Pending"),
    DELETED("Deleted"),
    DNC("Do Not Call")
    ;
		
		private MembershipStatus(String value)
		{
			this.txtValue = value;
		}
		
		public static List<String> getValues()
		{
			List<String> vals = new ArrayList<String>();
			for (MembershipStatus s : values())
			{
				vals.add(s.txtValue);
			}
			return vals;
		}
		
		public String getTxtValue()
		{
			return txtValue;
		}
		
		private String txtValue;
	}
	
	public Membership(JSOModel data) 
	{
		super(data);
	}
	
	public String getName() {
		return getField("name");
	}
	
	public User getUser() {
		return new User(getObject("fields").getObject("user"));
	}
	
	public MembershipStatus getStatus()
	{
		int statusCode = Integer.valueOf(getObject("fields").get("status"));
		
		if (statusCode == MembershipStatus.SUBSCRIBED.ordinal())
		{
			return MembershipStatus.SUBSCRIBED;
		}
		else if (statusCode == MembershipStatus.UNSUBSCRIBED.ordinal())
		{
			return MembershipStatus.UNSUBSCRIBED;
		}
		else if (statusCode == MembershipStatus.REQUESTED.ordinal())
		{
			return MembershipStatus.REQUESTED;
		}
		else if (statusCode == MembershipStatus.INVITED.ordinal())
		{
			return MembershipStatus.INVITED;
		}
		else if (statusCode == MembershipStatus.DELETED.ordinal())
		{
			return MembershipStatus.DELETED;
		}
		else if (statusCode == MembershipStatus.DNC.ordinal())
		{
			return MembershipStatus.DNC;
		}
		
		// this should never happen
		return null;
	}
}
