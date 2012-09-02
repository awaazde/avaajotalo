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

import org.otalo.ao.client.model.Forum.ForumStatus;
import org.otalo.ao.client.model.Message.MessageStatus;


public class Membership extends BaseModel {
	/* Order matters. The constants are mirrored in 
	 * server side code. The ordinal value of the first declared
	 * is 0 and then increases from there.
	 */
	public enum MembershipStatus {
		SUBSCRIBED("Joined", 0),
    UNSUBSCRIBED("Unsubscribed", 1),
    REQUESTED("Requested", 2),
    INVITED("Pending", 3),
    DELETED("Deleted", 4),
    DNC("Do Not Call", 5)
    ;
		
		private MembershipStatus(String value, int code)
		{
			this.txtValue = value;
			this.code = code;
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
		
		public int getCode()
		{
			return code;
		}
		
		public static MembershipStatus getStatus(int code) {
    	for (MembershipStatus s : values())
    	{
    		if (s.getCode() == code)
    			return s;
    	}
    	
    	return null;
    }
		
		private String txtValue;
		private int code;
	}
	
	public Membership(JSOModel data) 
	{
		super(data);
	}
	
	public String getMemberName() {
		return getField("membername");
	}
	
	public User getUser() {
		return new User(getObject("fields").getObject("user"));
	}
	
	public MembershipStatus getStatus()
	{
		return MembershipStatus.getStatus(Integer.valueOf(getField("status")));
	}
	
}
