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
	
	public boolean moderated()
	{
		return getObject("fields").get("moderated").equals("y");
	}

}
