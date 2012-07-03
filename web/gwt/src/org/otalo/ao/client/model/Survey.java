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



public class Survey extends BaseModel {
	/*
	 * Should mirror the constant in models.py in surveys
	 */
	public static final String TEMPLATE_DESIGNATOR = "TEMPLATE";
	
	/* Order matters. The constants are mirrored in 
	 * server side code. The ordinal value of the first declared
	 * is 0 and then increases from there.
	 */
	public enum SurveyStatus {
		ACTIVE, EXPIRED, CANCELLED
	}
	
	public Survey(JSOModel data) {
		super(data);
	}
	
	public String getName()
	{
		return getField("name");
	}
	
	public SurveyStatus getStatus()
	{
		int statusCode = Integer.valueOf(getField("status"));
		
		if (statusCode == SurveyStatus.ACTIVE.ordinal())
		{
			return SurveyStatus.ACTIVE;
		}
		else if (statusCode == SurveyStatus.EXPIRED.ordinal())
		{
			return SurveyStatus.EXPIRED;
		}
		else if (statusCode == SurveyStatus.CANCELLED.ordinal())
		{
			return SurveyStatus.CANCELLED;
		}
		
		// This should never happen
		return null;
	}

}
