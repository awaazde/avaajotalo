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

import com.google.gwt.core.client.JsArray;


public class Line extends BaseModel {
	private static final String MANAGEMENT_DESIGNATOR = "";
	
	public Line(JSOModel data) {
		super(data);
	}
	
	public String getLogoFile() {
		return getField("logo_file");
	}
	
	public String getName() {
		return getField("name");
	}
	
	public String[] getForumIds() {
		
		String lst = getField("forums");
		lst = lst.replace("[","");
		return lst.split(",");

	}
	
	public List<Forum> getForums()
	{
		List<Forum> forums = new ArrayList<Forum>();
		JsArray<JSOModel> arr = getObject("fields").getArray("forums");
		
		JSOModel m;
		for (int i=0; i<arr.length(); i++)
		{
			m = arr.get(i);
			forums.add(new Forum(m));
		}
		return forums;
	}
	public boolean hasSMSConfig() {
		return !getField("sms_config").equals("null");
	}
	
	public Integer getMaxBlocksize() {
		String blockSize = getField("max_call_block");
		if (!blockSize.equals("null"))
			return new Integer(blockSize);
		else
			return null;
	}

	public Integer getMinInterval() {
		String interval = getField("min_interval_mins");
		if (!interval.equals("null"))
			return new Integer(interval);
		else
			return null;
	}
	
	public boolean bcastingAllowed() {
		return Boolean.valueOf(getField("bcasting_allowed"));
	}
	
	public boolean canManage() {
		return getName().contains(MANAGEMENT_DESIGNATOR);
	}
	
	public String getLanguage() {
		return getField("language");
	}
	
	public String getNumber() {
		return getField("number");
	}
	
}
