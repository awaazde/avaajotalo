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

import org.otalo.ao.client.Fora.Images;

import com.google.gwt.core.client.JavaScriptObject;
import com.google.gwt.user.client.ui.AbstractImagePrototype;
import com.google.gwt.user.client.ui.Tree;
import com.google.gwt.user.client.ui.TreeItem;
import com.google.gwt.user.client.ui.Widget;

public class Forum extends BaseModel {
	
	
	public Forum(JSOModel data) 
	{
		super(data);
	}
	
	public String getName() {
		return getObject("fields").get("name");
	}
	
	public boolean postingAllowed()
	{
		return getObject("fields").get("posting_allowed").equals("y");
	}
	
	public boolean responsesAllowed()
	{
		return getObject("fields").get("responses_allowed").equals("y");
	}
	
	public boolean moderated()
	{
		return getObject("fields").get("moderated").equals("y");
	}
	
	public boolean routeable()
	{
		return getObject("fields").get("routeable").equals("y");
	}

}
